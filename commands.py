import re

def ls(x):
    print('ls')
    return
    if x == None:
        bm.traverse_all()
    else:
        bm.traverse_box(x)

commands = {
    'ls [--d]': 'ls',
    'mkbox --n [--d] [--]': 'mkbox'
}

cmd_reg = '''(?P<CMD>^\S*) (?P<FLAGS>--\w{1}) (?P<VAL>\w+)'''

def parse_command(cmd):
    ms = re.findall(cmd_reg, cmd)
    flags = {}
    for m in ms:
        print(m)
        if m.group() == 'FLAG':
            flags.append(m)

if __name__ == '__main__':
    while True:
        workdir = '/'
        inp = input('Command: ')
        parse_command(inp)
