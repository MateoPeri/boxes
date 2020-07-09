# Boxes
A searchable library to keep track of things.
Inspired by [this post](https://www.reddit.com/r/Coding_for_Teens/comments/hmqvp2/i_want_to_make_a_searchable_library/?utm_source=share&utm_medium=ios_app&utm_name=iossmf).

## Docs
### Commands
The commands follow the following structure: <command> <flag_1> <value_1> ... <flag_n> <value_n>. The flag order does not matter.
To pass a value that contains spaces (ie "Cool object"), put it between single quotes. To pass a list, do it like so: '[a, b, c]'.

#### Flags
* The flag `i` (and variants like `i1` or `i2`), corresponds to an ID of a Box/Object.
* `n` references a name of a Box/Object.
* `d` references a description of a Box/Object.
* `t` references a list of tags of a Box/Object.
* `ls [--i]`: Displays the contents of the given box in a tree-like structure. If `i` is not provided (or it's an Object instead of a Box), the contents of the root folder are displayed.
* `mkbox/mkobj --n [--d] [--t] [--i]`: Creates a new Box/Object with the given name, description and tags. The flag `i` references the Box where the thing will be created. If it is not provided, the object is created in the root folder.
* `tag --i [--t]`: **Adds** the given tags to the Box/Object's tags.
* `edit --i [--n] [--d] [--t]`: Edits the given object, modifying the passed parameters (name, description and tags).
* `rm --i`: Removes a given Box/Object. If the passed object is a Box, all its contents will be removed.
* `cp --i1 --i2`: Copies the `i1` Box/Object to the `i2` **Box**. If `i1` is a Box, the contents will be copied recursively as well.
* `mv --i1 --i2`: Moves the `i1` Box/Object to the `i2` **Box**. What it really does is copy, then remove the original.
* `info --i`: Provides more details about the object, like type, name, description, tags and path.
* `path --i`: Gives the path of Boxes to get a specific Box/Object.
* `search [--n] [--d] [--t]`: Searches all Boxes and matches the given parameters. They must match **all** parameters. Examples:
  * `search --n pen` will return all Boxes/Objects that contain 'pen' in their names.
  * `search --d cool` will return all Boxes/Objects that contain 'cool' in their descriptions.
  * `search --t '[school, stuff]'` will return all Boxes/Objects that contain the tags 'school' **and** 'stuff'.


## Improvements and future
* Use a database to permanently store data.
* More advanced search queries.
* More command options.
* More errors and warnings to inform user.
* Help pages for commands (`<command> --h`).
