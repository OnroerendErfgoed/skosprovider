"""
This example loads a csv file into a SimpleCsvProvider and dumps the provider
to csv again.
"""

import csv
import sys
from pathlib import Path

from skosprovider.csv.dumper import csv_dumper
from skosprovider.csv.provider import SimpleCsvProvider
from skosprovider.uri import UriPatternGenerator

with open(Path(__file__).parents[1] / "data" / "trees.csv") as file:
    provider = SimpleCsvProvider(
        {"id": "TREES"},
        csv.reader(file),
        uri_generator=UriPatternGenerator("http://id.trees.org/%s"),
    )

dump = csv_dumper(provider)
csv.writer(sys.stdout).writerows(dump)
