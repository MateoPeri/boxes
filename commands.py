import re, warnings, copy
import boxes
from boxes import Object, Box, BoxManager
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
        if 'h' in x.keys():
            self.help() # ?
            return True
        if len(miss) > 0:
            warnings.warn('[ERROR] Missing required argument(s): ' + ','.join(miss))
            return False
        return True

class ls(Command):
    def run(self, x):
        if super().run(x):
            if len(x) == 0:
                self.bm.traverse_all()
            else:
                self.bm.traverse_box(self.bm.from_id(x['i']))
        
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
                dest = bm.from_id(x['i'])
                if type(dest) is not Box:
                    warnings.warn('[ERROR] The given ID corresponds to an Object, not a Box.')
                    dest = self.bm.root
            else:
                dest = self.bm.root
            dest.add_things(ret)
            bm.reload()

class mkobj(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['n']
        self.help = '''Create a new object.
--n: Name of the object.
--i: parent box of the object. Default is root.'''
    
    def run(self, x):
        if super().run(x):
            if 'd' in x.keys(): d = x['d']
            else: d = ''
            ret = Object(x['n'], desc=d)
            if 'i' in x.keys():
                dest = bm.from_id(x['i'])
                if type(dest) is not Box:
                    warnings.warn('[ERROR] The given ID corresponds to an Object, not a Box.')
                    dest = self.bm.root
            else:
                dest = self.bm.root
            dest.add_things(ret)
            bm.reload()

class tag(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            b = bm.from_id(x['i'])
            if 't' in x.keys():
                b.tags += parse_list(x['t'])

class edit(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            b = bm.from_id(x['i'])
            if 'n' in x.keys():
                b.name = x['n']
            if 'd' in x.keys():
                b.desc = x['d']
            if 't' in x.keys():
                b.tags = parse_list(x['t'])

class rm(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
        
    def run(self, x):
        if super().run(x):
            bm.delete(x['i'])
            bm.reload()
            
class cp(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i1']
        
    def run(self, x):
        if super().run(x):
            b1 = bm.from_id(x['i1'])
            if 'i2' in x.keys():
                dest = bm.from_id(x['i2'])
                if type(dest) is not Box:
                    warnings.warn('[ERROR] The given ID corresponds to an Object, not a Box.')
                    dest = self.bm.root
            else:
                dest = self.bm.root

            
            if type(b1) is Box:
                b2 = Box(b1.name, b1.desc, b1.tags)
                things = b1.things.copy()
            else:
                b2 = Object(b1.name, b1.desc, b1.tags)
            
            dest.add_things(b2)
            bm.reload()
            if type(b2) is Box:
                print('adding', b1, 'to', dest)
                for t in things:
                    cp(bm).run({'i1': t.id, 'i2': b2.id})
                
class mv(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i1', 'i2']

    def run(self, x):
        if super().run(x):
            cp(bm).run(x)
            rm(bm).run({'i': x['i1']})

class info(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            print('\n')
            if 'i' in x.keys():
                print(bm.from_id(x['i']).details())
            print(path(bm).run(x))
            print('\n')

class path(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            if 'i' in x.keys():
                print(bm.from_id(x['i']).details())

class search(Command):
    def __init__(self, bm):
        super().__init__(bm)
    
    def run(self, x):
        if super().run(x):
            n = d = ''
            ts = []
            di = {}
            if 'n' in x.keys():
                n = x['n']
                di['name'] = n
            if 'd' in x.keys():
                d = x['d']
                di['description'] = d
            if 't' in x.keys():
                ts = parse_list(x['t'])
                di['tags'] = ts
            s = bm.search(name=n, desc=d, tags=ts)
            
            print('\nShowing results for ' + str(di) + ':')
            print([str(x) for x in s])

cmd_reg = '''(?P<CMD>^\S*)*(((?P<FLAGS>--\w+) (?P<VAL>(\'(.+)\'|[^\s]+)))*)'''

def parse_list(s):
    return s.strip('][').split(', ')

def parse_command(cmd):
    matches = re.finditer(cmd_reg, cmd, re.MULTILINE)
    flags = {}
    for match in matches:
        if match.group('CMD'):
            c = match.group('CMD')
        f = match.group('FLAGS')
        if f:
            f = f[2:] # remove dashes
            flags[f] = match.group('VAL').strip().strip("'")
    return (c, flags)

def run_command(x):
    commands[x[0]].run(x[1])

# TEST
bm = BoxManager(TinyDB('boxes.json'))
my_room = Box('My room')
my_room.add_things(Object('Red Pencil', desc='My writing pencil!', tags=['school']))
my_room.add_things(Object('Blue Pencil', desc='My drawing pencil!', tags=['school']))
my_room.add_things(Object('Pen', desc='For note taking!', tags=['school']))
shelf = Box('Shelf', desc='On the left wall')
shelf.add_things(Object('Book', desc='A nice book!', tags=['school', 'books']))
my_room.add_things(shelf)

bm.set_root(my_room)

commands = {
    'ls': ls(bm),
    'mkbox': mkbox(bm),
    'mkobj': mkobj(bm),
    'tag': tag(bm),
    'edit': edit(bm),
    'info': info(bm),
    'rm': rm(bm),
    'mv': mv(bm),
    'cp': cp(bm),
    'search': search(bm),
    'path': path(bm) # TODO
}

#bm.traverse_box(shelf)
s = bm.search(name='pen', tags=['school'])
print([str(x) for x in s])

if __name__ == '__main__':
    while True:
        inp = input('Command: ')
        cmd = parse_command(inp)
        run_command(cmd)
    
