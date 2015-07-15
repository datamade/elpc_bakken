import csv
import re
import sys

percent = re.compile('.*?(?<!\S)([0-9]{1,2}(\.\d+)?)[%.]*(?!\S)')


def strip_tags(value):
    """Returns the given HTML with all tags stripped."""
    return re.sub(r'<[^>]*?>', '', value)

def decimal_degrees(degrees) :
    dd = degrees[0]
    dd += degrees[1]/60.0
    dd += degrees[2]/3600.0
    return dd

def latlongs(value) :
    vals = [strip_tags(each.strip('\n')).strip() for each in location]
    vals = ' '.join(vals).split()
    vals = [float(each) for each in vals if floatable(each)]
    lat = decimal_degrees(vals[:3])
    lng = decimal_degrees(vals[3:])

    return lat, lng

def floatable(char) :
    try :
        float(char)
        return True
    except :
        return False

location_line = False
location = []

operator_line = False
well_type_counter = 0

has_capture_plan = False

state_wide_counter = 0
state_wide_percent = ''

with open(sys.argv[1], encoding='iso-8859-1') as f :

    for line in f :
        
        # Well File
        m = re.match('Well File # (\d+)', line)
        if m :
            well_file_number = m.group(1)

        # Operator
        if operator_line :
            operator = line
            operator_line = False
        if line.startswith('Telephone Number') :
            operator_line = True

        # Well Type
        if well_type_counter :
            if well_type_counter == 4 :
                well_type = line
                well_type_counter = False
            else :
                well_type_counter += 1

        if line.startswith('Type of Well') :
            well_type_counter += 1

        # Location
        if line.startswith('Spacing Unit') :
            location_line = False
        if location_line :
            location.append(line)
        if line.startswith('(Subject to NDIC Approval') :
            location_line = True

        if 'capture' in line.lower() :
            has_capture_plan = True
            
        if state_wide_counter == 1 :
            m = percent.match(strip_tags(line))
            if m :
                state_wide_percent = m.group(1)
                state_wide_counter = False
            else : 
                print(sys.argv[1], old_line, file=sys.stderr)
                print(state_wide_counter, line, file=sys.stderr)
                state_wide_counter += 1

        elif state_wide_counter :
            print(state_wide_counter, line, file=sys.stderr)
            state_wide_counter += 1 
            if state_wide_counter > 6 :
                state_wide_counter = False
                
        if 'statewide' in line.lower() :
            m = percent.match(strip_tags(line))
            if m and 'estimated to reduce' not in line :
                state_wide_percent = m.group(1)
            else :
                old_line = line
                state_wide_counter = 1

try :
    well = well_file_number, operator, well_type, state_wide_percent
except :
    print(sys.argv[1], file=sys.stderr)
    raise

well = [each.strip('<br>\n').replace('&amp;', '&') for each in well]

lat, lng = latlongs(location)
filename = sys.argv[1].split('/')[-1].split('.')[0] + '.pdf'

if filename == 'W' + well_file_number + '.pdf' :
    aligned_filename = True
else :
    aligned_filename = False

writer = csv.writer(sys.stdout)

writer.writerow([filename] + well + [has_capture_plan, lat, lng, aligned_filename])




