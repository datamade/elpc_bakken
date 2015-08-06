import csv
import re
import sys

percent = re.compile('.*?(?<!\S)([0-9]{1,2}(\.\d+)?)[%.]*(?!\S)')

def clean_string(value) :
    return value.strip('<br>\n').replace('&amp;', '&')


def strip_tags(value):
    """Returns the given HTML with all tags stripped."""
    return re.sub(r'<[^>]*?>', '', value)

def decimal_degrees(degrees) :
    dd = degrees[0]
    dd += degrees[1]/60.0
    dd += degrees[2]/3600.0
    return dd

def latlongs(value) :
    vals = [strip_tags(each.strip('\n')).strip() for each in value]
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

def make_statewide_flare() :
    state_wide_counter = 0
    def parser(line) :
        nonlocal state_wide_counter
        if any(trigger in line.lower() 
               for trigger in 
               ('statewide', 'state flare')) :
            m = percent.match(strip_tags(line))
            if m and 'estimated to reduce' not in line :
                return ('statewide_flare', m.group(1))
            else :
                state_wide_counter += 1

        if state_wide_counter :
            m = percent.match(strip_tags(line))
            if m :
                return m.group(1)
            state_wide_counter += 1

        if state_wide_counter > 6 :
            state_wide_counter = 0

    return parser

def make_location() :
    location = []
    location_line = False
    def parser(line) :
        nonlocal location_line
        nonlocal location
        
        if location_line :
            location.append(line)

        if line.startswith('(Subject to NDIC Approval') :
            location_line = True
            location = []
        elif line.startswith('Spacing Unit') :
            location_line = False
            return latlongs(location)

    return parser

def gas_capture(line) :
    if 'capture' in line.lower() :
        return True

def countdown(num_steps, start_condition) :
    counter = 0
    def parser(line) :
        nonlocal counter

        if counter == num_steps :
            counter = 0
            return clean_string(line)

        if start_condition(line) or counter :
            counter += 1

    return parser

def well_file_number(line) :
    m = re.match('Well File # (\d+)', line)
    if m :
        return m.group(1)

        
def apply(lines, extractors) :
    extractors = extractors[:]
    for line in lines :
        for name, extractor in extractors[:] :
            result = extractor(line)
            if result :
                yield name, result
                #if name not in ('operator', 'well_type') :
                extractors.remove((name, extractor))
        if not extractors :
            break

if __name__ == '__main__' :

    well_type = countdown(4, lambda line : line.startswith('Type of Well'))
    operator = countdown(1, lambda line : line.startswith('Telephone Number'))
    location = make_location()
    statewide_flare = make_statewide_flare()


    extractor_names = ('well_file_number', 
                       'well_type',
                       'operator',
                       'location',
                       'statewide_flare',
                       'gas_capture_plan?')

    writer = csv.DictWriter(sys.stdout, 
                            ('filename', 'aligned_name') + extractor_names)
    writer.writeheader()

    extractors = [well_file_number, gas_capture, well_type, 
                  operator, location, statewide_flare]
    extractors = list(zip(extractor_names, extractors))

    for filename in sys.argv[1:] :
        print(filename, file=sys.stderr)
        with open(filename, encoding='iso-8859-1') as f :
            results = dict(apply(f, extractors))
            pdf = filename.split('/')[-1].split('.')[0] + '.pdf'
            results['filename'] = pdf
            try :
                results['aligned_name'] = pdf == 'W' + results['well_file_number'] + '.pdf'
            except KeyError :
                pass
            print(results, file=sys.stderr)
            writer.writerow(results)
        
