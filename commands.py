import re, warnings, copy
from boxes import Object, Box, BoxManager

class Command():
    def __init__(self, bm):
        self.req = []
        self.help_msg = ''
        self.bm = bm

    def help(self):
        print(self.help_msg)
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
            if 'i' in x.keys():
                self.bm.traverse_box(self.bm.from_id(x['i']))
            else:
                self.bm.traverse_all()
        
class mkbox(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['n']
        self.help_msg = '''Create a new box. --n: Name of the box. --i: parent of the box. Default is root.'''
    
    def run(self, x):
        if super().run(x):
            if 'd' in x.keys(): d = x['d']
            else: d = ''
            if 't' in x.keys(): tags = parse_list(x['t'])
            else: tags = []
            ret = Box(x['n'], desc=d, tags=tags)
            if 'i' in x.keys():
                dest = self.bm.from_id(x['i'])
                if type(dest) is not Box:
                    warnings.warn('[ERROR] The given ID corresponds to an Object, not a Box.')
                    dest = self.bm.root
            else:
                dest = self.bm.root
            print(dest.add_things(ret))
            self.bm.reload()

class mkobj(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['n']
        self.help_msg = '''Create a new object. --n: Name of the object. --i: parent box of the object. Default is root.'''
    
    def run(self, x):
        if super().run(x):
            if 'd' in x.keys(): d = x['d']
            else: d = ''
            if 't' in x.keys(): tags = parse_list(x['t'])
            else: tags = []
            ret = Object(x['n'], desc=d, tags=tags)
            if 'i' in x.keys():
                dest = self.bm.from_id(x['i'])
                if type(dest) is not Box:
                    warnings.warn('[ERROR] The given ID corresponds to an Object, not a Box.')
                    dest = self.bm.root
            else:
                dest = self.bm.root
            print(dest.add_things(ret))
            self.bm.reload()

class tag(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            b = self.bm.from_id(x['i'])
            if 't' in x.keys():
                b.tags += parse_list(x['t'])

class edit(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            b = self.bm.from_id(x['i'])
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
            b = self.bm.from_id(x['i'])
            self.bm.delete(x['i'])
            self.bm.reload()
            print('Removing', b)
            
class cp(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i1']
        
    def run(self, x):
        if super().run(x):
            b1 = self.bm.from_id(x['i1'])
            if 'i2' in x.keys():
                dest = self.bm.from_id(x['i2'])
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
            self.bm.reload()
            if type(b2) is Box:
                print('Copying', b1, 'to', dest)
                for t in things:
                    cp(self.bm).run({'i1': t.id, 'i2': b2.id})
                
class mv(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i1', 'i2']

    def run(self, x):
        if super().run(x):
            cp(self.bm).run(x)
            rm(self.bm).run({'i': x['i1']})

class info(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            det = '\n'
            if 'i' in x.keys():
                det += self.bm.from_id(x['i']).details()
            det += '\n' + path(self.bm).run(x)
            return det

class path(Command):
    def __init__(self, bm):
        super().__init__(bm)
        self.req = ['i']
    
    def run(self, x):
        if super().run(x):
            if 'i' in x.keys():
                return 'Path: ' + self.bm.get_path(x['i'])

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
            s = self.bm.search(name=n, desc=d, tags=ts)
            
            print('\nShowing results for ' + str(di) + ':')
            print([str(x) for x in s])

class load(Command):
    pass

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
            f = f.strip('-')
            flags[f] = match.group('VAL').strip().strip("'")
    return (c, flags)

def run_command(x, bm):
    return commands[x[0]](bm).run(x[1])

cmd_reg = r'(?P<CMD>^\S*)*(((?P<FLAGS>--\w+) (?P<VAL>(\'(.+)\'|[^\s]+)))*)'

commands = {
    'ls': ls,
    'mkbox': mkbox,
    'mkobj': mkobj,
    'tag': tag,
    'edit': edit,
    'info': info,
    'rm': rm,
    'mv': mv,
    'cp': cp,
    'search': search,
    'path': path
}
