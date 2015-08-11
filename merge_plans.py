import csv
import sys

hard_wells = {}

with open(sys.argv[2]) as f :
    reader = csv.DictReader(f)
    for row in reader :
        row_id = row.pop('filename')
        if any(row.values()) :
            hard_wells[row_id] = row

with open(sys.argv[1]) as f :
    reader = csv.DictReader(f) 
    writer = csv.DictWriter(sys.stdout, reader.fieldnames) 
    writer.writeheader()
    for row in reader :
        row_id = row['filename']
        if row_id in hard_wells :
            row['statewide_flare'] = hard_wells[row_id]['statewide_flare']
            row['gas_capture_plan?'] = hard_wells[row_id]['gas_capture_plan?']
        writer.writerow(row)
