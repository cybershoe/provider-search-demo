from argparse import ArgumentParser
from sys import stdin, stdout
from os import path
from json import dumps

from csv import DictReader

parser = ArgumentParser(
    prog="convert_data",
    description="Converts StatsCan ODA CSV files into JSON for bulk load into MDB"
)

parser.add_argument("-i", "--infile")
parser.add_argument("-o", "--outfile")
parser.add_argument("-p", "--province", required=True)
parser.add_argument("-c", "--chunk", default=10000)


args = parser.parse_args()

chunkSize = int(args.chunk)

print(args)
outfile = args.outfile or stdin

rownumber = 0
filenumber = 0

if outfile:
    filebase, fileext = path.splitext(args.outfile)

out = open(args.outfile, mode="w") if args.outfile else stdout

out.write("[\n")

with open (args.infile, newline="") if args.infile else stdin as f:
    reader = DictReader(f)
    for row in reader:
        if row['postal_code'] != "":
            if rownumber >= chunkSize:
                rownumber = 0
                filenumber += 1
                out.write("\n]\n")  
                out.close()
                out = open(f"{filebase}_{filenumber}{fileext}", mode="w") if args.outfile else stdout
                out.write("[\n")


            record = {
                "geoPoint": { 
                    "type": "Point",
                    "coordinates" : [
                        row["latitude"],
                        row["longitude"]
                    ]
                },
                "address": {
                    "streetNumber": str(row['street_no']).title(),
                    "streetName": str(row['str_name_pcs']).title(),
                    "streetType": str(row['str_type_pcs']).title(),
                    "streetDirection": str(row['str_dir_pcs']).title(),
                    "unit": str(row['unit']).title(),
                    "city": str(row['city_pcs']).title(),
                    "province": args.province,
                    "postalCode": str(row['postal_code']).title()
                }
            }

            outline = f'{"" if rownumber == 0 else ",\n  "}{dumps(record, indent=2)}'
            rownumber += 1
            out.write(outline)

out.write("\n]\n")  
        
out.close