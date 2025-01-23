"""
Module for performing actual parsing of input files, transformation, and writing to output file.
"""

import csv
import os
import re

import pandas as pd
import xlrd

from dataunifier.common import constants as commonconstants
from dataunifier.common.exceptions import NoFileMatchingRegexException, InputFileException, \
    TransformationException, ParsingException, DiscardRecordException
from dataunifier.parse.classes import ParseFilesetContext, ParseInputFileContext, ParseIteratorContext, ParseRowContext
from dataunifier.utils import fileio, display


def __get_file_paths(input_file_ctxt):
    input_file = input_file_ctxt.input_file
    for regex in input_file.regex_list:
        try:
            file_names = fileio.get_file_names_by_regex(input_file_ctxt.input_dir, regex)
            if len(file_names) > 1:
                msg = 'WARNING: Found more than one file whose name matches regex "%s" in input directory ' \
                      '"%s": "%s" (Input File "%s")' % (
                          regex, input_file_ctxt.input_dir, '", "'.join(file_names), input_file.name
                      )
                display.warn(msg)
            return [os.path.join(input_file_ctxt.input_dir, file_name) for file_name in file_names]
        except NoFileMatchingRegexException:
            pass
    msg = 'Could not find any file names matching patterns "%s" in input directory "%s". ' \
          '(Input File "%s")' % (
              '", "'.join(input_file.regex_list), input_file_ctxt.input_dir, input_file.name
          )
    raise InputFileException(msg)


def __declare_parsing_file(iterator_ctxt):
    if iterator_ctxt.sheet:
        msg = 'Parsing file "%s", sheet "%s"...' % (iterator_ctxt.filepath, iterator_ctxt.sheet)
    else:
        msg = 'Parsing file "%s"...' % iterator_ctxt.filepath
    display.stdout(msg)


def __raise_transform_exception(row_ctxt, task, e):
    if row_ctxt.sheet:
        msg = 'When executing task "%s" on row %d of file "%s", sheet "%s": %s' % (
            task.name, row_ctxt.row_number, row_ctxt.filepath, row_ctxt.sheet, e.message
        )
    else:
        msg = 'When executing task "%s" on row %d of file "%s": %s' % (
            task.name, row_ctxt.row_number, row_ctxt.filepath, e.message
        )
    raise ParsingException(msg)


def __clean_value(value):
    stripped = value.strip()
    cleaned = "".join([c if c in commonconstants.PRINTABLE_CHARS else " " for c in stripped])
    return cleaned


def __parse_row(row_ctxt):
    try:
        tasks = row_ctxt.fileset.tasks
        working_row_ctxt = row_ctxt.with_updated_rowdict({k: __clean_value(v) for k, v in row_ctxt.rowdict.items()})
        for task in tasks:
            try:
                working_row_ctxt = task.transform(working_row_ctxt)
            except TransformationException as e:
                __raise_transform_exception(row_ctxt, task, e)
        row_ctxt.writer.writerow(working_row_ctxt.rowdict)
    except DiscardRecordException:
        pass


def __parse_iterator(iterator_ctxt, progress_bar=None):
    counter = 1
    for rowdict in iterator_ctxt.iterator:
        row_ctxt = ParseRowContext(iterator_ctxt, counter, rowdict)
        __parse_row(row_ctxt)
        counter += 1
        if progress_bar:
            progress_bar.increment()


def __find_sheet(regex_list, sheet_names):
    for regex in regex_list:
        for sheet_name in sheet_names:
            if re.fullmatch(regex, sheet_name):
                return sheet_name
    return None


def __stringify(value):
    stringified = str(value)
    try:
        floatified = float(stringified)
        if floatified.is_integer():
            stringified = str(int(floatified))
    except ValueError:
        pass
    return stringified


def __dataframe_to_rowdicts(dataframe):
    filled = dataframe.fillna("")
    stringified = filled.applymap(__stringify)
    rowdicts = stringified.to_dict(orient="records")
    return rowdicts


def __get_all_excel_sheets(input_file_path):
    try:
        return pd.read_excel(input_file_path, sheet_name=None)
    except xlrd.biffh.XLRDError:
        raise InputFileException(
            f'Could not read Excel file "{input_file_path}". This could mean that it is encrypted with a '
            f'password, or corrupted. Please remove the password (if any), and ensure it is not '
            f'corrupted.'
        )


def __get_xls_iterator_list(input_file_ctxt, input_file_path):
    dataframes = __get_all_excel_sheets(input_file_path)
    if input_file_ctxt.input_file.sheets is None:
        return [
            ParseIteratorContext(input_file_ctxt, input_file_path, sheet_name, __dataframe_to_rowdicts(df))
            for sheet_name, df in dataframes.items()
        ]
    output = []
    for sheet in input_file_ctxt.input_file.sheets:
        matching = __find_sheet(sheet.regex_list, dataframes.keys())
        if matching:
            output.append(ParseIteratorContext(
                input_file_ctxt, input_file_path, matching, __dataframe_to_rowdicts(dataframes[matching])
            ))
        else:
            if sheet.mandatory:
                msg = 'Could not find any sheet name matching patterns "%s" in file "%s". (Input File "%s")' % (
                    '", "'.join(sheet.regex_list), input_file_path, input_file_ctxt.input_file.name
                )
                raise InputFileException(msg)
    return output


def __parse_input_file(input_file_ctxt):
    input_file_paths = __get_file_paths(input_file_ctxt)
    for input_file_path in input_file_paths:
        ext = fileio.get_extension(input_file_path)
        if ext == "csv":
            row_count = fileio.count_rows(input_file_path)
            with open(input_file_path, "r", encoding=commonconstants.DEFAULT_ENCODING) as f:
                iterator_ctxt = ParseIteratorContext(input_file_ctxt, input_file_path, None, csv.DictReader(f))
                __declare_parsing_file(iterator_ctxt)
                progress_bar = display.ProgressBar(row_count)
                __parse_iterator(iterator_ctxt, progress_bar)
            progress_bar.close()
        elif ext[0:3] == "xls":
            iterator_ctxt_list = __get_xls_iterator_list(input_file_ctxt, input_file_path)
            for iterator_ctxt in iterator_ctxt_list:
                __declare_parsing_file(iterator_ctxt)
                progress_bar = display.ProgressBar(len(iterator_ctxt.iterator))
                __parse_iterator(iterator_ctxt, progress_bar)
                progress_bar.close()
        else:
            msg = 'File "%s" has an unsupported format: "%s". Only CSVs and Excel files are accepted. ' \
                  '(Input File "%s")' % (
                      input_file_path, ext, input_file_ctxt.input_file.name
                  )
            raise InputFileException(msg)


def __parse_fileset(ctxt):
    fileset = ctxt.fileset
    display.stdout("Handling fileset: %s" % fileset.name)
    input_files = fileset.input_files
    for input_file in input_files:
        input_file_ctxt = ParseInputFileContext(ctxt, input_file)
        __parse_input_file(input_file_ctxt)


def start(config_ctxt, writer):
    """
    Start the parsing, transformation and writing process for all files specified in the configuration.

    :param ConfigContext config_ctxt: The ConfigContext object representing the configuration.
    :param csv.DictWriter writer: The DictWriter to use to write.
    """

    for fileset in config_ctxt.filesets:
        fileset_ctxt = ParseFilesetContext(config_ctxt.parent, writer, fileset)
        __parse_fileset(fileset_ctxt)
