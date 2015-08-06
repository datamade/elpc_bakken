import csv
import re
import sys
import os

percent = re.compile('.*?(?<!\S)([0-9]{1,2}(\.\d+)?)[%.]*(?!\S)')


def strip_tags(value):
    """Returns the given HTML with all tags stripped."""
    return re.sub(r'<[^>]*?>', '', value)

def make_statewide_flare() :
    state_wide_counter = 0
    def parser(line) :
        nonlocal state_wide_counter
        if any(trigger in line.lower() 
               for trigger in 
               ('statewide', 'state flare')) :
            m = percent.match(strip_tags(line))
            if m and 'estimated to reduce' not in line :
                state_wide_count = 0
                return ('statewide_flare', m.group(1))
            else :
                state_wide_counter += 1

        if state_wide_counter :
            m = percent.match(strip_tags(line))
            if m :
                return ('statewide_flare', m.group(1))
            state_wide_counter += 1

        if state_wide_counter > 6 :
            state_wide_counter = 0

    return parser

def gas_capture(line) :
    if 'capture' in line.lower() :
        return ('capture_plan?', True)

def lines(base_dir) :
    for filename in os.listdir(base_dir) :
        if filename.endswith('html') :
            with open('%s/%s' % (base_dir, filename)) as f :
                for line in f :
                    yield filename, line

if __name__ == '__main__' :

    statewide_flare = make_statewide_flare()

    writer = csv.writer(sys.stdout) 
    writer.writerow(['filename', 'capture_plan?', 'statewide_flare'])

    for base_dir in sys.argv[1:] :
        extractors = [gas_capture, statewide_flare]

        results = []
        pages = []

        for filename, line in lines(base_dir) :
            for extractor in extractors[:] :
                result = extractor(line)
                if result :
                    pages.append(filename)
                    results.append(result)
                    extractors.remove(extractor)
            if not extractors :
                break

        print(list(zip(results, pages)), file=sys.stderr)
        results = dict(results)

        writer.writerow([base_dir.replace('_text', '') + '.pdf',
                         results.get('capture_plan?', False),
                         results.get('statewide_flare', None)])

    

