"""
Contains the master list of all "When" classes.
"""

from dataunifier.when.And import And
from dataunifier.when.Or import Or
from dataunifier.when.Not import Not
from dataunifier.when.WhenFieldMatchesRegex import WhenFieldMatchesRegex

ALL_WHEN_CLASSES = [
    WhenFieldMatchesRegex
]
