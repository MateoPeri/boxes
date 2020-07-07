class Object():
    def __init__(self, name, desc='', tags=[]):
        self.name = name
        self.desc = desc
        self.tags = tags

    def __str__(self):
        return '[O] ' + self.name

class Box(Object):
    def __init__(self, name, desc='', tags=[]):
        super().__init__(name, desc, tags)
        self.things = []

    def add_things(self, t):
        self.things.append(t)

    def __str__(self):
        return '[B] ' + self.name



class BoxManager():
    def __init__(self):
        self.boxes = []
        
    def add_box(self, box):
        exists = [box.name in b.name for b in self.boxes]
        if not exists:
            self.boxes.append(box)

    def traverse_all(self):
        for b in boxes:
            traverse_box(b)

    def traverse_box(self, lst, level=0, indent=4):
        print('    ' * (level - 1) + '+--- ' * (level > 0) + str(lst))
        for l in lst.things[:]:
            if type(l) is Box:
                self.print_list(l, level + 1)
            else:
                print(' ' * indent * level + '+--- ' + str(l))

# TEST
bm = BoxManager()
my_room = Box('My room')
my_room.add_things(Object('Pencil'))
shelf = Box('Shelf', desc='On the left wall')
shelf.add_things(Object('Book', desc='A nice book!'))
my_room.add_things(shelf)

bm.add_box(my_room)

bm.traverse_box(shelf)
