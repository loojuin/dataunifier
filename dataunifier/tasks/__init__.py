"""
Module containing the master list of available tasks.
"""

from dataunifier.tasks.MapFieldsTask import MapFieldsTask
from dataunifier.tasks.ReplaceTask import ReplaceTask
from dataunifier.tasks.SetFieldValueTask import SetFieldValueTask
from dataunifier.tasks.ConvertDateFormatTask import ConvertDateFormatTask
from dataunifier.tasks.LowercaseTask import LowercaseTask
from dataunifier.tasks.UppercaseTask import UppercaseTask
from dataunifier.tasks.RegexReplaceTask import RegexReplaceTask
from dataunifier.tasks.DiscardRecordTask import DiscardRecordTask
from dataunifier.tasks.DiscardFieldsTask import DiscardFieldsTask
from dataunifier.tasks.CopyFieldValueTask import CopyFieldValueTask
from dataunifier.tasks.ConcatenateFieldsTask import ConcatenateFieldsTask
from dataunifier.tasks.CsvLookupReplaceTask import CsvLookupReplaceTask
from dataunifier.tasks.CsvMatchTask import CsvMatchTask
from dataunifier.tasks.ArithmeticTask import ArithmeticTask
from dataunifier.tasks.FuzzyMatchReplaceTask import FuzzyMatchReplaceTask


ALL_TASK_CLASSES = [
    MapFieldsTask,
    SetFieldValueTask,
    ConvertDateFormatTask,
    LowercaseTask,
    UppercaseTask,
    ReplaceTask,
    RegexReplaceTask,
    DiscardRecordTask,
    DiscardFieldsTask,
    CopyFieldValueTask,
    ConcatenateFieldsTask,
    CsvLookupReplaceTask,
    CsvMatchTask,
    ArithmeticTask,
    FuzzyMatchReplaceTask
]
