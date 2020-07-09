import json

class Object():
    def __init__(self, name, desc='', tags=[]):
        self.name = name
        self.desc = desc
        self.tags = tags
        self.id = 0

    def __str__(self):
        return '[O_' + str(self.id) + '] ' + self.name

    def details(self):
        return self.name + ' [Object]\nDescription: ' + self.desc + \
    '\nTags: ' + ', '.join(self.tags)

    def as_dict(self, recursive=False):
        return {"name": self.name, "desc": self.desc, "tags": self.tags}

    def delete(self):
        del self

class Box(Object):
    def __init__(self, name, desc='', tags=[]):
        super().__init__(name, desc, tags)
        self.things = []

    def add_things(self, t):
        self.things.append(t)
        return 'Added ' + str(t) + ' to ' + str(self)

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
        d["things"] = ts
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

    def look_for(self, thing, lst):
        if thing in self.things:
            lst.append(self)
            return True
        if thing in self.get_all_children(-1):
            lst.append(self)
        for t in self.things:
            if type(t) is Box:
                a = t.look_for(thing, lst)
                if a:
                    return a
        return False

class BoxManager():
    def __init__(self, file):
        self.file = file
        self.root = None #
        self.load()

    def set_root(self, r=None):
        self.root = r
        self.reload()

    def parse_file(self, data):
        thing = None
        if 'things' in data:
            thing = Box(data['name'], desc=data['desc'], tags=data['tags'])
            for t in data['things']:
                print(t)
                thing.things.append(self.parse_file(t))
        else:
            thing = Object(data['name'], desc=data['desc'], tags=data['tags'])
        return thing

    def save(self):
        with open(self.file, 'w') as f:
            f.write(json.dumps((self.root.as_dict(recursive=True))))
            f.close()

    def load(self):
        with open(self.file, 'r') as f:
            try:
                data = json.load(f)
            except:
                with open(self.file, 'w') as nf:
                    data = {}
                    nf.write(json.dumps(data))
                    nf.close()
                    
            f.close()
        self.root = self.parse_file(data)

        if self.root is None:
            self.set_root(Box('root', desc='Root folder'))
        self.reload()

    def reload(self):
        if self.root:
            count = 0
            for o in self.get_all():
                o.id = count
                count += 1
        self.save()

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

    def traverse_box(self, box, level=0, indent=4):
        print(' ' * indent * (level - 1) + '+---' * (level > 0) + str(box))
        for t in box.things:
            if type(t) is Box:
                self.traverse_box(t, level + 1)
            else:
                print(' ' * indent * level + '+---' + str(t))

    def get_path(self, i):
        lst = []
        b = self.from_id(i)
        if b is None:
            return False
        if not self.root.look_for(b, lst):
            return False
        lst.append(b)
        return ' > '.join([str(x) for x in lst])


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
