import re
import starnet_cleanup


def converter(in_file: str, out_file: str):


    '''Script which takes in a report file from a 12d field file and converts it to
    a format that is readable by StarNet.'''
    # in_file = 'BR06 Control.rpt'
    # out_file = 'BR06_out.txt'

    coords_line = re.compile(
        r'Coordinate:\s+Name:\s+(?P<name>.*)[^X]+X:\s+(?P<X>[0-9.]+)[^Y]+Y:\s+(?P<Y>[0-9.]+)[^Z]+Z:\s+(?P<Z>[0-9.]+)', re.I)
    measurement_line = re.compile(
        r'''\s+Measurement:\s+H:\s+(?P<h_degrees>[0-9]+).\s+(?P<h_minutes>[0-9]+)'\s+(?P<h_seconds>[0-9]+)"\s+V:\s+(?P<v_degrees>[0-9]+).\s+(?P<v_minutes>[0-9]+)'\s+(?P<v_seconds>[0-9]+)"\s+S:\s+(?P<S>[0-9]+\.[0-9]+)''', re.M)

    attributes_line = re.compile(
        r'''N:pu_id\s+V:(?P<attribute>.*(?=\n))''', re.S)
    instrument_height = re.compile(
        r'''is_hi\s+V:(?P<instrument_height>[0-9]+\.[0-9]+)''')
    target_height = re.compile(
        r'''N:target_height V:(?P<target_height>[0-9]+\.[0-9]+)''')

    with open(out_file, 'w') as out_file:
        coords_info = []
        with open(in_file, encoding='utf-8') as greg:
            for line in greg:
                m = coords_line.search(line)
                if m:
                    if not m.group('name') in coords_info:
                        coords_info.append(m.group('name'))
                        print('C', m.group('name'), m.group('X'),
                              m.group('Y'), m.group('Z'), file=out_file)
            print(file=out_file)

        current_coords = None
        with open(in_file, encoding='utf-8') as file:
            for line in file:

                m = coords_line.search(line)
                if m:
                    if current_coords:
                        print('DE\n', file=out_file)
                    current_coords = m.group('name')
                    print('DB', m.group('name'), file=out_file)

                n = measurement_line.search(line)
                if n:
                    recent_horizontal = (n.group('h_degrees'), n.group('h_minutes'), n.group(
                        'h_seconds'), n.group('S'), n.group('v_degrees'), n.group('v_minutes'), n.group('v_seconds'))

                i = instrument_height.search(line)
                if i:
                    recent_instrument_height = (i.group('instrument_height'))

                o = attributes_line.search(line)
                if o:
                    attribute = o.group('attribute')
                    if attribute[0] in '0123456789':
                        attribute = 'CH' + attribute

                t = target_height.search(line)
                if t:
                    recent_target_height = (t.group('target_height'))
                    print('DM', attribute, '{}-{}-{} {} {}-{}-{} {}/{}'.format(*recent_horizontal,
                                                                               recent_instrument_height, recent_target_height), file=out_file)

            print('DE\n', file=out_file)


if __name__ == '__main__':

    try:
        in_file = input('File to clean: ')
    except ValueError as err:
        print('File in must be a string.')

    try:
        out_file = input('File to output from cleaning: ')
    except ValueError as err:
        print('File out must be a string.')

    converter(in_file, out_file)
    starnet_cleanup.clean_output(out_file, out_file + '_cleaned_')