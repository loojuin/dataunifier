# Data Unifier Manual

## Quick Start

1) Create your playbook file
1) Drop your input files into a directory
1) Decide on the name of the output file
1) Run the Programme.

### Usage
```shell script
$ python dataunifier.py [-f] [--log-file-path=<log file path>] [--input-dir=<input directory path>] [--output=<output file path>] <path to playbook file>
```

### Arguments and Options
| Argument | Default | Description |
|----------|---------|-------------|
| `-f` | Unset | If set, the Programme will forcefully overwrite the output file without prompting, if the file exists. |
| `--log-file-path=<log file path>` | `./error.log` | The path to which the Programme should write the error log. |
| `--input-dir=<input directory path>` | `.` (Current directory) | The directory the Programme should look in for input files. |
| `--output=<output file path>` | `./output.csv` | The path to the file that the Programme should write out to. |
| `<path to playbook file>` | | The path to the playbook file to refer follow. |

### Package Dependencies
This project requires the following packages and their transitive dependencies
(if any):
- `yaml`
- `pandas`

These dependencies are listed in `requirements.txt` as well.

## Terminology
The following terms will be used for the rest of this document:
- ***"the Programme"*** - The `dataunifier.py` Python programme
- ***"playbook file"*** - A YAML file with a set structure that tells the
                           Programme what to do
- ***"input file"*** - A file whose data will be read by the Programme
- ***"input directory"*** - The directory containing the input files
- ***"output file"*** - A file that the Programme writes data to
- ***"record"*** - A single unit of data, such as a row in a CSV or Excel file
- ***"task"*** - A single transformation task

## Concept of Operation
You can think of the Programme as a chef. It has all the tools and know-how it needs
to process your files, but it does not know what you need it to do. That is why
you need to provide it with a recipe to follow, which we call the "playbook file".

The Programme will first read the playbook file, which specifies the names of 
the input files to be read, and how to transform the data being read in before being 
written out to the output file.

The Programme will then create the output file at the specified path, and search the 
input directory for the input files and read the data from them file by file, record by 
record.

By default, the Programme searches for input files inside the current directory,
and writes out to a file called `output.csv` in the current directory. You can override
this using the `--input-dir` and `--output` command line options respectively.

For each record, the Programme will perform the transformations specified in the
playbook file, then write the transformed record into the output file (unless
they are discarded as part of the transformation).

The rest of this readme will focus on how to write the playbook file.

## Playbook File
Playbook files are written in YAML, and the YAML structure is heavily inspired by the
playbook files used by Ansible (www.ansible.com). Here is an example:

```yaml
---
filesets:
  - name: "Good students"
    input_files:
      - name: "Good students from Upper Sec"
        regex: 
          - "^good_students_upper_sec.csv$"
          - "^upper_sec_good.csv$"
      - name: "Good students from Lower Sec"
        regex: "^good_students_lower_sec.csv$"
    tasks:
      - name: Map fields
        map_fields:
          ignore_case: true
          fields:
            - target_field: id
              src_fields: ID
            - target_field: name
              src_fields: NAME
            - target_field: numberOfDetentionCases
      - name: Set numberOfDetentionCases to 0
        set_field_value:
          field: numberOfDetentionCases
          value: "0"
  - name: "Naughty students"
    input_files:
      - name: "Naughty students data sheet"
        regex: "^naughty_students.xlsx$"
        sheets:
          - "Nominal Roll"
    tasks:
      - name: Map fields
        map_fields:
          ignore_case: true
          fields:
            - target_field: id
              src_fields: Id
            - target_field: name
              src_fields: Name
            - target_field: numberOfDetentionCases
              src_fields: 
                - "Number of times in Detention"
                - "number of times in detention"
```

### Concepts
Each playbook file is responsible for producing **one** output file, and 
allows you to specify multiple sets of input files and how to process each set.

At the top level is a list of `filesets`. Each `fileset` specifies a list of processing
tasks (`tasks`), and the files to read and apply these processing tasks to 
(`input_files`). The records present in the output will be a union of the records in
each input file.

### Input Files
Each `input_file` block is designed to represent **one** file that you want the
programme to read.

Take a look at the following example of an `input_file` configuration
block to understand the syntax:

```yaml
- name: Nominal Roll
  regex: "^\\w+_nominal_roll_caa_\\d{8}.xlsx$"
  sheets:
    - "Nominal Roll"
    - regex: "^[Ii]ncoming$"
      mandatory: false
```

#### Top-level Keys
| Key | Mandatory | Description |
|-----|-----------|-------------|
| `name` | Yes | A descriptive name for the input file. Does not affect application function, but helps keep things maintainable. |
| `regex` | Yes | A regular expression that matches the file name. This is useful for identifying files even if part of the file name changes daily. |
| `sheets` | No | List of sheets to read. If this key is omitted, the programme will read all sheets. Applicable only for Excel files. |

`regex` can also be a list of regular expressions:
```yaml
- name: Nominal Roll
  regex:
    - "^\\w+_nominal_roll_caa_\\d{8}.xlsx$"
    - "^Nominal Roll \\w+ \\(\\d{8}\\).xlsx$"
```
Note that even though a list of regular expressions is provided, the entire list is
still representative of one file. The first file encountered that matches any of the
regular expressions will be the file that is read by the program.

#### Specifying Sheets
For Excel files, there are two ways of specifying the sheets to read, and both can 
coexist in the same `sheets` list.

The first is to simply state the sheet name:
```yaml
sheets:
  - "Nominal Roll"
  - "Incoming"
```
In this case, the sheet names must be exactly `Nominal Roll` and `Incoming` in order 
to be picked up by the programme. The programme will fail with an error if it does 
not find the sheet. For a more flexible specification, you can use a regular
expression, like this:
```yaml
sheets:
  - regex: "^[Nn]ominal roll$"
  - regex: "^[Ii]ncoming$"
    mandatory: false
```
Here, the sheet will get picked up by the programme if its name is either
`Nominal roll` or `nominal roll` for the first sheet, and  `Incoming` or `incoming` 
for the second sheet. Note that if more than one sheet matches the regular expression
for a sheet, only one of them will be picked up, and there is no guarantee which one. 
You must be careful with how you specify your regular expression.

When using the regular expression method, you can add the `mandatory` key to 
determine what the program will do if no sheet matches the regular expression. 
If `mandatory` is set to `false`, the programme will carry on even if it does 
not find a matching sheet. If set to `true`, the program will fail with an error.

For each sheet, can also specify a list of regular expressions:
```yaml
sheets:
  - regex:
      - "^[Nn]ominal roll$"
      - "^[Cc]urrent$" 
  - regex:
      - "^[Ii]ncoming$"
      - "^[Nn]ew$"
```
As with in `input_files`, each list of regular expressions still corresponds to only
one sheet. The first sheet encountered that matches any of the regular expressions
is the sheet that the programme will read.

### Tasks
The `tasks` section specifies a list of tasks that will be performed for each row
that is read in from the input files. The general configuration syntax is as such:

```yaml
- name: <Task Name>
  <task type>:
    <task-specific keys>
  when:
    <"when" keys>
```

#### Top-level Keys

| Key | Mandatory | Description |
|-----|-----------|-------------|
| `name` | Yes | A descriptive name for the task. Providing a name really helps when debugging your configuration. |
| `<task type>` | Yes | Determines what type of task it is. |
| `when` | No | A conditional. The task will only run when the condition is met. If the key is omitted, the task will always run. |

The syntax details differ for each task type, and are documented below.

### Task Types

#### `map_fields`
Determines list of fields in output file, and maps fields from input files to them.

**Note that every `fileset` must have at least one `map_fields` task in order for the
programme to function correctly.**

##### Example Configuration
```yaml
- name: Map Fields
  map_fields:
    ignore_case: true
    fields:
      - target_field: id
        src_fields: employee_ID
        ignore_case: false
      - target_field: name
        src_fields: name
      - target_field: status
        src_fields: status
        mandatory: false
      - target_field: wasUpdated
```

##### Example Input
| employee_ID | Name | status |
|-------------|------|--------|
| 1 | John Doe | fired |
| 2 | Jane Teo | employed |
| 3 | Jean Toe | employed |

##### Example Output
| id | name | status | wasUpdated |
|----|------|--------|------------|
| 1 | John Doe | fired | |
| 2 | Jane Teo | employed | |
| 3 | Jean Toe | employed | |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of objects | List of field definitions |
| `ignore_case` | No | Boolean | Indicates whether to ignore the case of all source fields for all items in `fields` |

##### Description of Keys in `fields` Objects
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `target_field` | Yes | String | The field name as should appear in the output file |
| `src_fields` | No | List of strings | The names of the field in the input file that should be mapped to this `target_field` |
| `mandatory` | No | Boolean | Indicates if the programme should be allowed to continue if none of the `src_fields` are found |
| `ignore_case` | No | Boolean | Indicates whether to ingore the case of the source fields. This setting takes precedence if `ignore_case` is specified globally for this task |

##### Important Notes
- This task cannot be used with the `when` statement. Adding a `when` statement will
  result in an error
- This task cannot be put into a task block. Doing so will result in an error
- If `src_fields` is omitted, `target_field` will be set to a blank value
- If `src_fields` are specified and not found in input files, and `mandatory` is set
  to `false`, `target_field` will be set to a blank value.
  
##### Error Conditions
An error will be thrown if:
- This task is used with a `when` statement
- This task is put into a task block
- No `src_fields` are found and `mandatory` is set to `true`.


#### `arithmetic`
Performs simple arithmetic, using two fields as input and one field as output.

##### Example Configuration
```yaml
- name: Compute total applications
  arithmetic:
    left_field: approved
    right_field: rejected
    result_field: total_applications
    operation: add
    blank_is_zero: true
```

##### Example Input
| approved | rejected | total_applications |
|----------|----------|--------------------|
| 150      | 2        |                    |
| 30       | 129      |                    |

##### Example Output
| approved | rejected | total_applications |
|----------|----------|--------------------|
| 150      | 2        | 152                |
| 30       | 129      | 159                |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `left_field` | Yes | Field name | The field to use as the left operand (i.e., `a` in `a + b = c`) |
| `right_field` | Yes | Field name |The field to use as the right operand (i.e., `b` in `a + b = c`) |
| `result_field` | Yes | Field name | The field to write the result into |
| `operation` | Yes | Enumerator | The type of operation to perform. See below for list |
| `blank_is_zero` | No | Boolean | Indicates whether to treat a blank value as zero (0). Defaults to `false` if unspecified. |

##### Valid Values for `operation`

| Value | Result |
|-------|-------------|
| `add` | `left_field` + `right_field` |
| `subtract` | `left_field` - `right_field` |
| `multiply` | `left_field` * `right_field` |
| `divide` | `left_field` / `right_field` (float division) |

##### Error Conditions
An error will be thrown if:
- `left_field`, `right_field` or `result_field` cannot be found
- `blank_is_zero` is `false` and either `left_field` or `right_field` is blank
- Either `left_field` or `right_field` cannot be interpreted as a number.

#### `concatenate_fields`
Concatenates the values of two or more fields with a string and place value into 
another field.

##### Example Configuration
```yaml
- name: Concatenate first name and last name
  concatenate_fields:
    fields:
      - first_name
      - last_name
    to_field: full_name
    with_string: " "
```

##### Example Input
| first_name | last_name | full_name |
|------------|-----------|-----------|
| John       | Doe       |           |
| Jane       | Teo       |           |

##### Example Output
| first_name | last_name | full_name |
|------------|-----------|-----------|
| John       | Doe       | John Doe  |
| Jane       | Teo       | Jane Teo  |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of field names | The fields to concatenate |
| `to_field` | Yes | Field name | Name of field to place concatenated value into |
| `with_string` | Yes | String | The string to insert between concatenated values. |

Fields in `fields` will be concatenated in the order they are listed.

##### Error Conditions
An error will be thrown if:
- Any field listed in `fields` or `to_field` cannot be found.

#### `convert_date_format`
Attempts to interpret a field value as a date, and converts it to a set format.

##### Example Configuration
```yaml
- name: Standardise date formats
  convert_date_format:
    fields:
      - dob
      - join_date
    accepted_formats:
      - "%d-%b-%y"
      - "%d/%m/%Y"
    target_format: "%Y-%m-%d"
    allow_blank: false
    timezone: "America/New_York"
```

##### Example Input
| dob | join_date |
|-----|-----------|
| 4-jul-1967 | 5/10/2000 |
| 17-may-1991 | 3/1/2017 |

##### Example Output
| dob | join_date |
|-----|-----------|
| 1967-07-04 | 2000-10-05 |
| 1991-05-17 | 2017-01-03 |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of field names | The fields to apply the task on |
| `accepted_formats` | Yes | List of strings | Date/time formats that are accepted for interpretation |
| `target_format` | Yes | String | The date/time format to convert the value to |
| `allow_blank` | Yes | Boolean | Indicates whether to allow a blank value to pass through. |
| `timezone` | No | String | The timezone to output the date as, in tz database format. Currently defaults to `"Asia/Singapore"`. |

Values for `accepted_formats` and `target_formats` should conform to the Python
`datetime.strptime()` and `datetime.strftime()` syntax. The Programme will attempt to
parse date values using the formats provided in `accepted_formats` in the order
they are listed.

##### Gotchas
As with any date interpretation system, there will be a problem if date-first
and month-first representations are both accepted, such as the following:
```yaml
accepted_formats:
  - "%m/%d/%Y"
  - "%d/%m/%Y"
```

If an ambiguous value is encountered, such as `06/05/2000`, the Programme will interpret
according to the first matching format - in this case, 5 June 2000.

##### Error conditions
An error will be thrown if:
- Any field listed in `fields` cannot be found
- Any value in `accepted_formats` or `target_format` has invalid syntax
- The value of `timezone` is invalid
- A value does not match any of the formats in `accepted_formats`
- A value is blank and `allow_blank` is `false`.

#### `copy_field_value`
Copies the value from one field to one or more fields

##### Example Configuration
```yaml
- name: Copy name to lookup column
  copy_field_value:
    from_field: name
    to_fields:
      - lookup
```

##### Example Input
| name | lookup |
|------|--------|
| John Doe |    |
| Jane Teo |    |

##### Example Output
| name | lookup |
|------|--------|
| John Doe | John Doe |
| Jane Teo | Jane Teo |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `from_field` | Yes | Field name | The field to copy the value from |
| `to_fields` | Yes | List of field names | The fields to copy the value into. |

##### Error Conditions
An error will be thrown if:
- Any field in `from_field` or `to_fields` cannot be found.

#### `csv_lookup_replace`
Replaces values with values from one column in a CSV file, if the values match
that in another column in the CSV file.

##### Example Configuration
```yaml
- name: CSV Lookup Employee Type
  csv_lookup_replace:
    fields: employeeType
    directory: "some/directory"
    filename_regex: "^employee_nominal_roll.csv$"
    lookup_column: id
    value_column: employee_type
    on_unmatched: blank
    deduplicate_by: higher_row_number
```

##### Example Input
| id | name | employeeType |
|----|------|--------------|
| 1 | John Doe | 1 |
| 2 | Jane Teo | 2 |
| 3 | Jean Toe | 3 |

##### Example CSV File
| id | employeeType |
|----|--------------|
| 1 | perm |
| 2 | contract |
| 2 | perm |

##### Example Output
| id | name | employeeType |
|----|------|--------------|
| 1 | John Doe | perm |
| 2 | Jane Teo | perm |
| 3 | Jean Toe | |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of field names | Fields to act on |
| `directory` | Yes | String | Directory to look for CSV file in |
| `filename_regex` | Yes | String | Regular expression that will uniquely identify the CSV file |
| `lookup_column` | Yes | String | Name of column in CSV file that contains lookup value |
| `value_column` | Yes | String | Name of column in CSV file that contains replacement value |
| `on_unmatched` | Yes | Enum | Determines how the programme behaves if no match is found |
| `deduplicate_by` | No | Enum | Determines how the programme will handle duplicate values in the `lookup_column` | 

##### Valid Values for `on_unmatched`
| Value | Result |
|-------|--------|
| `fail` | Programme will fail with an error if no matching value is found |
| `blank` | Programme will set the field to blank if no matching value is found |
| `passthrough` | Programme will pass through original value if no matching value is found |

##### Valid Values for `deduplicate_by`
| Value | Result |
|-------|--------|
| `lower_row_number` | The value in a lower row number will be preferred |
| `higher_row_number` | The value in a higher row number will be preferred |

##### Error Conditions
An error will be thrown if:
- Any field in `fields` is not found
- Directory stated in `directory` does not exist
- No file matching `filename_regex` is found
- Multiple files matching `filename_regex` are found
- A duplicate value in `lookup_column` is encountered, and the `deduplicate_by` 
  field is omitted
- `lookup_column` cannot be found in the CSV file
- `value_column` cannot be found in the CSV file
- The value in any of the fields in `fields` cannot be found in `lookup_column`,
  and `on_unmatched` is set to `fail`.
  
#### `csv_match`
Attempts to find the field value within a column from another CSV file, and changes
its value depending on whether a match is found or not.

##### Example Configuration
```yaml
- name: Check whether name is found in nominal roll
  csv_match:
    fields: inNominalRoll
    directory: "some/directory"
    filename_regex: "^nominal_roll.csv$"
    lookup_column: "name"
    match_value: "found"
    unmatch_value: "not_found"
```

##### Example Input
| name | inNominalRoll |
|------|---------------|
| John Doe | John Doe |
| Jane Teo | Jane Teo |
| Jean Toe | Jean Toe |

##### Example CSV File
| name |
|------|
| John Doe |
| Jane Teo |

##### Example Output
| name | inNominalRoll |
|------|---------------|
| John Doe | found |
| Jane Teo | found |
| Jean Toe | not_found |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of fields | The fields to act upon |
| `directory` | Yes | String | The directory to look for the CSV file in |
| `filename_regex` | Yes | String | A regular expression that uniquely identifies the CSV file to be looked up |
| `lookup_column` | Yes | String | The column in the CSV to look for the value in |
| `match_value` | Yes | String | The value to change the field to if matched |
| `unmatch_value` | Yes | String | The value to change the field to if not matched |

##### Error Conditions
An error will be thrown if:
- Any field listed in `fields` is not found
- The directory stated in `directory` does not exist
- No file with name matching `filename_regex` is found
- Multiple files with name matching `filename_regex` are found
- `lookup_column` is not found in the CSV file

##### Additional Notes
Unlike the CSV Lookup Replace Task, this task is able to handle duplicate values
in `lookup_column`.

#### `discard_fields`
Discards fields.

##### Example Configuration

```yaml
- name: Discard working fields
  discard_fields:
    fields:
      - wasUpdated
```

##### Example Input
| name | wasUpdated |
|------|------------|
| John Doe | true |
| Jane Teo | false |
| Jean Toe | true |

##### Example Output
| name |
|------|
| John Doe |
| Jane Teo |
| Jean Toe |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of field names | List of fields to discard |

##### Important Notes
- This task cannot be used with the `when` statement. Adding a `when` statement will
  result in an error.
- This task cannot be put into a task block. Doing so will result in an error.
- If any field listed in `fields` is not found, an error will **not** be thrown,
  but a warning will be displayed.

##### Error Conditions
An error will be thrown if:
- This task is used with a `when` statement
- This task is put into a task block.

#### `discard_record`
Discards the entire record.

##### Example Configuration
```yaml
- name: Discard record if person is fired
  discard_record:
  when:
    value_of_field: status
    matches_regex: "^fired$"
```

##### Example Input
| name | status |
|------|--------|
| John Doe | fired |
| Jane Teo | employed |
| Jean Toe | employed |

##### Example Output
| name | status |
|------|--------|
| Jane Teo | employed |
| Jean Toe | employed |

##### Description of Keys
This task has no keys.

##### Important Notes
This task is intended to be used together with a `when` statement. Without the
`when` statement, this task will simply discard all rows.

#### `fuzzy_match_replace`
Replaces field values if they approximately match specified values.

##### Example Configuration
```yaml
- name: Clean and map airport ICAO codes
  fuzzy_match_replace:
    fields: icaoCode
    method: jaccard
    ngram_size: 2
    minumum_score: 0.5
    on_unmatched: blank
    rules:
      - string: "changi"
        replacement: "WSSS"
      - string: "haneda"
        replacement: "RJTT"
      - string: "charles de gaulle"
        replacement: "LFPG"
      - string:
          - "john f kennedy"
          - "jfk"
        replacement: "KJFK"
```

##### Example Input
| name | icaoCode |
|------|----------|
| chngi | chngi |
| haneda | haneda |
| seletar | seletar |
| charles de gaule | charles de gaule |
| john f. kennedy | john f. kennedy |
| jfk | jfk |

##### Example Output
| name | icaoCode |
|------|----------|
| chngi | WSSS |
| haneda | RJTT |
| seletar | |
| charles de gaule | LFPG |
| john f. kennedy | KJFK |
| jfk | KJFK |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of fields | List of fields to act on |
| `method` | No | Enum | Fuzzy matching method |
| `ngram_size` | No | Integer | The size of the n-grams to use for matching |
| `minimum_score` | No | Decimal between 0 and 1 | The minimum matching score to accept as a match |
| `on_unmatched` | Yes | Enum | Determines what to do if no match is found |
| `rules` | Yes | List of objects | List of rules to attempt to match against |

##### Description of Keys in `rules` Objects
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `string` | Yes | String | String to attempt to match against |
| `replacement` | Yes | String | The string to replace the value with if matched |

##### Valid Values for `method`
| Value | Result |
|-------|--------|
| `jaccard` | Programme will use the Jaccard Index method to perform matching. |

`jaccard` is currently the only implemented method. If the `method` key is omitted,
the programme will use the `jaccard` method by default.

##### Valid Values for `on_unmatched`
| Value | Result |
|-------|--------|
| `fail` | Programme will fail with an error if no matching value is found |
| `blank` | Programme will set the field to blank if no matching value is found |
| `passthrough` | Programme will pass through original value if no matching value is found |

##### Error Conditions
An error will be thrown if:
- Any field listed in `fields` is not found
- An unrecognised value is provided for `method`
- The value for `ngram_size` is not an integer greater than 0
- An unrecognised value is provided for `on_unmatched`
- The field value does not match any of the rules and `on_unmatched` is `fail`.

##### Important Notes
- The programme attempts the rules in the order listed, and will stop processing
  once a matching rule is found.
  
#### `lowercase`
Converts values to lowercase.

##### Example Configuration
```yaml
- name: Convert gender to lowercase
  lowercase:
    fields:
      - gender
```

##### Example Input
| gender |
|--------|
| Male |
| male |
| FEMALE |
| F |

##### Example Output
| gender |
|--------|
| male |
| male |
| female |
| f |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of fields | List of fields to act on |

##### Error Conditions
An error will be thrown if:
- Any field listed in `fields` is not found.

#### `replace`
Replaces field values with other values based on a set of rules.

##### Example Configuration
```yaml
- name: Change enumerator values
  replace:
    fields: status
    on_unmatched: passthrough
    allow_blank: false
    rules:
      - replace:
          - "fired"
          - "terminated"
        with: "dismissed"
      - replace: "detained"
        with: "suspended"
```

##### Example Input
| name | status |
|------|--------|
| John Doe | fired |
| Jane Teo | employed |
| Jean Toe | terminated |
| Joan Leo | detained |

##### Example Output
| name | status |
|------|--------|
| John Doe | dismissed |
| Jane Teo | employed |
| Jean Toe | dismissed |
| Joan Leo | suspended |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of field names | Names of fields to act on |
| `on_unmatched`| Yes | Enum | Determines how the programme handles unmatched values |
| `allow_blank` | Yes | Boolean | Determines whether the programme allows blank values through |
| `rules` | Yes | List of objects | List of replacement rules |

##### Description of Keys in `rules` Objects
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `replace` | Yes | List of strings | List of values to be replaced |
| `with` | Yes | String | Replacement Value |

##### Valid Values for `on_unmatched`
| Value | Result |
|-------|--------|
| `fail` | Programme will fail with an error if no matching value is found |
| `blank` | Programme will set the field to blank if no matching value is found |
| `passthrough` | Programme will pass through original value if no matching value is found |

##### Error Conditions
An error will be thrown if:
- Any field listed in `fields` is not found
- An invalid value is provided for `on_unmatched`
- The field value does not match any of the rules, and `on_unmatched` is set to `fail`.

#### `regex_replace`
Replaces field values if they match the specified regular expression.

##### Example Configuration
```yaml
- name: Standardise gender field
  regex_replace:
    fields:
      - gender
    on_unmatched: fail
    allow_blank: true
    rules:
      - replace:
          - "^[Mm].*$"
        with: "MALE"
      - replace:
          - "^[Ff].*$"
        with: "FEMALE"
```

##### Example Input
| gender |
|--------|
| Male |
| fem |
| m |
|  |
| Female |

##### Example Output
| gender |
|--------|
| MALE |
| FEMALE |
| MALE |
|  |
| FEMALE |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of fields | List of fields to act on |
| `on_unmatched` | Yes | Enum | Determines the programme's behaviour if a value does not match any rules |
| `allow_blank` | Yes | Determines if the programme will allow blank values through even if there is no rule to match them |
| `rules` | Yes | List of rules |

##### Description of Keys in `rules`
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `replace` | Yes | List of strings | List of regular expressions or strings to attempt to match against |
| `with` | Yes | String | Replacement value |

##### Valid Values for `on_unmatched`
| Value | Result |
|-------|--------|
| `fail` | Programme will fail with an error if no matching value is found |
| `blank` | Programme will set the field to blank if no matching value is found |
| `passthrough` | Programme will pass through original value if no matching value is found |

##### Error Conditions
An error will be thrown if:
- Any field in `fields` is not found
- An unrecognised value is provided for `on_unmatched`
- The field value does not match any of the rules and `on_unmatched` is set to `fail`.

##### Advanced Uses
The `replace` and `with` keys can be used to perform partial substitutions of the
original field values, including the use of capturing groups and backreferences.
Consider the following rule:
```yaml
- replace: "chocolate"
  with: "banana"
```
With the above rule, field value "`I like chocolates`" would be transformed to
"`I like bananas`".

You can also use capturing groups and backreferences to include parts of the original
value in the output value:
```yaml
- replace: "^I like (.+)$"
  with: "\\1 are awesome"
```
With this rule, field value "`I like chocolates`" would be transformed to
"`chocolates are awesome`".

##### Important Notes
Note that the rules are attempted in the order they are listed, and processing stops
once a matching rule is found.

#### `set_field_value`
Set a field's value to a constant.

##### Example Configuration
```yaml
- name: Set isJohn to true if first name is John
  set_field_value:
    field: isJohn
    value: "true"
  when:
    value_of_field: name
    matches_regex: "^John.*$"
```

##### Example Input
| name | isJohn |
|------|--------|
| John Doe | |
| John Hurt | |
| Jane Austen | |
| John Cena | |

##### Example Output
| name | isJohn |
|------|--------|
| John Doe | true |
| John Hurt | true |
| Jane Austen | |
| John Cena | true |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `field` | Yes | Field name | Name of field to set |
| `value` | Yes | String | Value to set |

##### Error Conditions
An error will be thrown if:
- Field stated in `field` is not found

#### `uppercase`
Converts values to uppercase.

##### Example Configuration
```yaml
- name: Convert gender to uppercase
  uppercase:
    fields:
      - gender
```

##### Example Input
| gender |
|--------|
| Male |
| male |
| female |
| F |

##### Example Output
| gender |
|--------|
| MALE |
| MALE |
| FEMALE |
| F |

##### Description of Keys
| Key | Mandatory | Type | Description |
|-----|-----------|------|-------------|
| `fields` | Yes | List of fields | List of fields to act on |

##### Error Conditions
An error will be thrown if:
- Any field listed in `fields` is not found.

### Conditional Execution of Tasks
For each task, it is possible to specify that it should only run when certain
conditions are met. This is achieved using the `when` block.

Take this example:
```yaml
- name: Set category to foreigner if NRIC does not start with S or T
  set_field_value:
    field: category
    value: "citizen"
  when:
    value_of_field: nric
    matches_regex: "^[ST].+$"
```

In the above example, the `set_field_value` task will only be executed if the value
of the field `nric` matches the regular expression `^[ST].+$` (a string starting with
"S" or "T").

#### Constructing A `when` Block
The keys inside a `when` block are generally supposed to flow like natural English.

Take this example:
```yaml
when:
  value_of_field: nric
  matches_regex: "^[ST].+$"
```
The above `when` block could be literally read as: "when value of field '`nric`' matches 
regex '`^[ST].+$`'".

The behaviour of a `when` block is therefore determined by the combination of keys used.

At the time of writing, there is only one combination implemented: 
`value_of_field/matches_regex`

#### `value_of_field/matches_regex`
Causes a task to execute only if the value of a field matches a regular expression.

##### Description of Keys
| Key | Type | Description |
|-----|------|-------------|
| `value_of_field` | Field name | Name of field to check |
| `matches_regex` | Regular expression | Regular expression to match against |

#### Combining Conditions
More complex logic can be achieved in the `when` block using meta-keys `and`, `or` and 
`not`.

Take this example:
```yaml
when:
  or:
    - and:
        - value_of_field: status
          matches_regex: "^valid$"
        - value_of_field: name
          matches_regex: "^.+$"
    - not:
        value_of_field: id
        matches_regex: "^-1$"
```

In the above example, the task would only execute if the value of the `status` field
is equal to `"valid"` **and** the value of the `name` field is not blank, **or** if
the value of the `id` field is **not** equal to `"-1"`.

You can also see that the `and` and `or` keys take in a list.
