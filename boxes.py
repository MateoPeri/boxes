class Object():
    def __init__(self, name, desc='', tags=[]):
        self.name = name
        self.desc = desc
        self.tags = tags
        self.guid = 0

    def __str__(self):
        return '[O] ' + self.name

    def as_dict(self, recursive=False):
        return {'name': self.name, 'desc': self.desc, 'tags': self.tags}

class Box(Object):
    def __init__(self, name, desc='', tags=[]):
        super().__init__(name, desc, tags)
        self.things = []

    def add_things(self, t):
        self.things.append(t)

    def __str__(self):
        return '[B] ' + self.name

    def as_dict(self, recursive=False):
        d = super().as_dict()
        if recursive:
            ts = [t.as_dict(recursive) for t in self.things]
        else:
            ts = [str(t) for t in self.things]
        d['things'] = ts
        return d

    def get_all_children(self, mx_lvl=0, level=0):
        res = []
        for t in self.things:
            res.append(t)
            if type(t) is Box and (mx_lvl > level or mx_lvl==-1):
                res += t.get_all_children(level + 1)
        return res



class BoxManager():
    def __init__(self, db):
        self.root = None
        self.db = db

    def from_guid(self, guid):
        return self.db.search(Query().guid == guid)

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
        f_name = [x for x in results if name.lower() == x.name.lower()] if name != '' else results
        # Desc
        f_desc = [x for x in results if desc.lower() in x.desc.lower()] if desc != '' else results
        # Tags
        f_tag = [x for x in results if any([y for y in tags if y in x.tags])] if len(tags) > 0 else results
        results = [item for item in results
                   if item in f_tag and
                   item in f_name and
                   item in f_tag]
        return results
