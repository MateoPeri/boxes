import os, json
from boxes import Object, Box, BoxManager
import commands as cmds

# TEST - Uncomment for test objects and boxes. Can be removed safely
def test():
    my_room = bm.root
    my_room.add_things(Object('Red Pencil', desc='My writing pencil!', tags=['school']))
    my_room.add_things(Object('Blue Pencil', desc='My drawing pencil!', tags=['school']))
    my_room.add_things(Object('Pen', desc='For note taking!', tags=['school']))
    shelf = Box('Shelf', desc='On the left wall')
    shelf.add_things(Object('Book', desc='A nice book!', tags=['school', 'books']))
    drawer = Box('Drawer')
    drawer.add_things(Box('Other Box'))
    shelf.add_things(drawer)

    a = Box('Box')
    a.add_things(Object('Obj'))
    shelf.add_things(a)

    my_room.add_things(shelf)
    drawer.add_things(Object('Test Object :)'))

    bm.set_root(my_room)


file = 'boxes.json'
if __name__ == '__main__':
    bm = BoxManager(os.path.abspath(file))
    #test() # Uncomment for test objects and boxes. Can be removed safely
    print('\n')
    bm.traverse_all()
    while True:
        inp = input('\nCommand: ')
        cmd = cmds.parse_command(inp)
        res = cmds.run_command(cmd, bm)
        if res:
            print(res)
