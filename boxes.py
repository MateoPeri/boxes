class Object():
    def __init__(self, name, desc='', tags=[]):
        self.name = name
        self.desc = desc
        self.tags = tags
        self.id = 0

    def __str__(self):
        return '[O_' + str(self.id) + '] ' + self.name

    def details(self):
        return self.name + ' [Box]\nDescription: ' + self.desc + \
    '\nTags: ' + ', '.join(self.tags)

    def as_dict(self, recursive=False):
        return {'name': self.name, 'desc': self.desc, 'tags': self.tags}

    def delete(self):
        del self

class Box(Object):
    def __init__(self, name, desc='', tags=[]):
        super().__init__(name, desc, tags)
        self.things = []

    def add_things(self, t):
        self.things.append(t)
        print('Added', t, 'to', self)

    def __str__(self):
        return '[B_' + str(self.id) + '] ' + self.name

    def details(self):
        return '\n' + self.name + ' [Box]\nDescription: ' + self.desc + \
    '\nTags: ' + ', '.join(self.tags) + '\n'

    def as_dict(self, recursive=False):
        d = super().as_dict()
        if recursive:
            ts = [t.as_dict(recursive) for t in self.things]
        else:
            ts = [str(t) for t in self.things]
        d['things'] = ts
        return d

    def get_all_children(self, max_lvl=0, level=0):
        res = []
        for t in self.things:
            res.append(t)
            if type(t) is Box and (max_lvl > level or max_lvl==-1):
                res += t.get_all_children(level + 1)
        return res

    def delete_child(self, thing):
        if thing in self.things:
            self.things.remove(thing)

class BoxManager():
    def __init__(self, db):
        self.set_root()
        self.db = db
        self.last_id = 0

    def set_root(self, r=None):
        self.root = r
        self.reload()

    def reload(self):
        if self.root:
            count = 0
            for o in self.get_all():
                o.id = count
                count += 1

    def get_all(self):
        return [self.root] + self.root.get_all_children(-1)
            
    def from_id(self, _id):
        l = [o for o in self.get_all() if o.id == int(_id)]
        return l[0] if l else None

    def delete(self, _id):
        o = self.from_id(_id)
        for i in self.get_all():
            if type(i) is Box:
                i.delete_child(o)
            
    
    def traverse_all(self):
        self.traverse_box(self.root)

    def traverse_box(self, lst, level=0, indent=4):
        print('    ' * (level - 1) + '+--- ' * (level > 0) + str(lst))
        for l in lst.things[:]:
            if type(l) is Box:
                self.traverse_box(l, level + 1)
            else:
                print(' ' * indent * level + '+--- ' + str(l))

    def search(self, name='', desc='', tags=[]):
        results = [self.root] + self.root.get_all_children(-1)
        # Name
        f_name = [x for x in results if name.lower() in x.name.lower()] if name != '' else results
        # Desc
        f_desc = [x for x in results if desc.lower() in x.desc.lower()] if desc != '' else results
        # Tags
        f_tag = [x for x in results if all([y in x.tags for y in tags])] if len(tags) > 0 else results

        results = [item for item in results
                   if item in f_name and
                   item in f_desc and
                   item in f_tag]
        return results
