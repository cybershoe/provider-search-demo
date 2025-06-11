from sys import stdin, stdout
from csv import DictReader
from json import dumps

output = {}

with stdin as infile:
  reader = DictReader(infile)
  for row in reader:
    output[row['city']] = output.get(row['city'], []) + [row['code']]

print(dumps(output, indent=2))