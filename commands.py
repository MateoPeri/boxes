import re
import boxes
from boxes import Object, Box, BoxManager
import warnings
from tinydb import TinyDB, Query

class Command():
    def __init__(self, bm):
        self.req = []
        self.help = ''
        self.bm = bm

    def help(self):
        print(self.help)
        print('Required Args: ' + ', '.join(self.req))
    
    def run(self, x):
        miss = [r for r in self.req if r not in x.keys()]
        if len(miss) > 0:
            warnings.warn('[ERROR] Missing required argument(s): ' + ','.join(miss))
            return False
        return True

class ls(Command):
    def run(self, x):
        if super().run(x):
            print('ls', x)
            if len(x) == 0:
                self.bm.traverse_all()
            else:
                b = self.bm.search(x['d'])
                self.bm.traverse_box(x)
        
class mkbox(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['n']
        self.help = '''Create a new box.
--n: Name of the box.
--i: parent of the box. Default is root.'''
    
    def run(self, x):
        if super().run(x):
            if 'd' in x.keys(): d = x['d']
            else: d = ''
            ret = Box(x['n'], desc=d)
            if 'i' in x.keys():
                dest = bm.from_guid(x['i'])
            else:
                dest = self.bm.root
            dest.add_things(dest)
            print('Added', ret, 'to', dest)

class tag(Command):
    def run(self, x):
        if super().run(x):
            pass

class edit(Command):
    def __init__(self):
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            if 'n' in x.keys():
                n = x['n']
            if 'd' in x.keys(): d = x['d']
            else: d = ''

cmd_reg = '''(?P<CMD>^\S*)*(((?P<FLAGS>--\w{1}) (?P<VAL>\w+))*)'''

def parse_command(cmd):
    matches = re.finditer(cmd_reg, cmd, re.MULTILINE)
    flags = {}
    for match in matches:
        if match.group('CMD'):
            c = match.group('CMD')
        f = match.group('FLAGS')
        if f:
            f = f[2:] # remove dashes
            flags[f] = match.group('VAL')
    return (c, flags)

def run_command(x):
    commands[x[0]].run(x[1])

# TEST
bm = BoxManager(TinyDB('boxes.json'))
my_room = Box('My room')
my_room.add_things(Object('Pencil'))
shelf = Box('Shelf', desc='On the left wall')
shelf.add_things(Object('Book', desc='A nice book!'))
my_room.add_things(shelf)

bm.root = my_room

commands = {
    'ls': ls(bm),
    'mkbox': mkbox(bm)
}

s = bm.search()
print([str(x) for x in s])

#bm.traverse_box(shelf)

if __name__ == '__main__':
    while True:
        break
        workdir = '/'
        inp = input('Command: ')
        cmd = parse_command(inp)
        run_command(cmd)
    
