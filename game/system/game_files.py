from game.system.filesystem import Directory, File, Node

def _find(parent: Directory, name: str) -> Node | None:
    for child in parent.children:
        if child.name == name:
            return child
    return None

GAME_ROOT = Directory("root", None)
GAME_ROOT.children = [
    # System directories, just for show
    Directory("bin", GAME_ROOT, password="unguessable"),
    Directory("etc", GAME_ROOT, password="unguessable"),
    Directory("usr", GAME_ROOT, password="unguessable"),
    Directory("var", GAME_ROOT, password="unguessable"),
    Directory("dev", GAME_ROOT, password="unguessable"),

    # Temporary directory
    Directory("tmp", GAME_ROOT),

    # Islands
    Directory("islands", GAME_ROOT),

    # Backpack
    Directory("backpack", GAME_ROOT),

    # User directories
    Directory("home", GAME_ROOT),
]

tmp = _find(GAME_ROOT, "tmp")

tmp.children = [
    File("test.txt", tmp, """This is a temporary file.         
You can ignore it. Seriously!""")
]

backpack = _find(GAME_ROOT, "backpack")
backpack.children = [
    File("backpack.txt", backpack, """Good old backpack. It stores your stuff.
         
You can move, copy and delete files or directories into or from it.
Try it out!
Copy the test file into the backpack:
   $ cp /tmp/test.txt /backpack/test.txt
Now check the backpack:
   $ ls /backpack"""),
]


islands = _find(GAME_ROOT, "islands")
islands.children = [
    Directory("island1", islands, password="bemyguest"),
]

island1 = _find(islands, "island1")
island1.children = [
    File("island1.txt", island1, """This is a temporary file.         
You can ignore it. Seriously!"""),
    Directory("ground", island1),
    Directory("forest", island1),
    Directory("fish_pond", island1),
]

# Add ground items
ground = _find(island1, "ground")
ground.children = [
    File("fishing_rod.item", ground, """A sturdy fishing rod."""),
    File("fishing_line.item", ground, """Strong fishing line."""),
    File("bucket.item", ground, """A metal bucket for carrying things."""),
]

# Add forest items
forest = _find(island1, "forest")
forest.children = [
    File("wood.item", forest, """Pieces of wood collected from the forest."""),
    File("can_of_worms.item", forest, """A tin can full of wriggling worms. Perfect for fishing."""),
    File("sail.item", forest, """A large piece of cloth that could be used as a sail."""),
]

# Add fish_pond directory (empty folder for fishes)
fish_pond = _find(island1, "fish_pond")
fish_pond.children = [
    Directory("fishes", fish_pond),
]