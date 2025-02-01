import re


def clean_output(in_file : str, out_file : str):


    fix_minutes = re.compile(r'(\d{2,3})-(\d)-(\d{1,2})')

    fix_seconds = re.compile(r'(\d{2,3})-(\d{2})-(\d\s)')

    with open(out_file, 'w') as o:
        with open(in_file, 'r') as f:
            s = f.read()
            s = fix_minutes.sub(r'''\1-0\2-\3''', s)
            s = fix_seconds.sub(r'''\1-\2-0\3''', s)
            print(s, file=o)


if __name__ == '__main__':
    try:
        in_file = input('File to clean: ')
    except ValueError as err:
        print('File in must be a string.')
    
    try:
        out_file = input('File to output from cleaning: ')
    except ValueError as err:
        print('File out must be a string.')
    
    clean_output(in_file, out_file)