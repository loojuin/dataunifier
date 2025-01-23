# Data Unifier

## Introduction
This Python project is a command-line data processing tool, whose primary purpose
is to combine data from multiple files into a single file. It also allows
transformations to be done on the data before being written to the output file.

This Programme is designed to be **fully automatable** with any automation system,
to be **quickly deployed** on **any computer**, and to be able to operate stably
on **input files of any size**. This leads to the following design constraints:

1) Must be able to run without any user input - i.e., all configuration parameters
   should be part of the command that executes the programme or read from a file
1) Must be OS-independent
1) Should only depend on other Python packages that are easy to install on a new
   offline computer - e.g., out-of-the-box Python packages, or default packages
   in an Anaconda installation
1) Should avoid reading entire input files into memory as far as possible.

Due to the above constraints, operations requiring the entire dataset,
such as deduplication or sorting, are out of the scope of this Programme.

## Usage
Please see the file called `MANUAL.md`.

## License
BSD 3-Clause License. Please see the file called `LICENSE`.

## Backstory
This tool was originally created in 2020, during my time in Singapore’s Defence
Science and Technology Agency (DSTA). It was created to allow data cleaning to be
done “in the field”, when I was forward-deployed as a data engineer supporting
Singapore’s fight against the COVID-19 pandemic.
