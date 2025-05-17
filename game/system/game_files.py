from game.system.filesystem import FileSystem

# The FileSystem instance will manage the entire file structure.
# The old GAME_ROOT and _find function are no longer needed in the same way.
fs = FileSystem() # Assuming root itself doesn't have a password as per old code.

def create_initial_filesystem(fs_instance: FileSystem):
    # System directories
    fs_instance.mkdir("/bin")
    fs_instance.mkdir("/etc")
    fs_instance.mkdir("/usr")
    fs_instance.mkdir("/var")
    fs_instance.mkdir("/dev")

    # Temporary directory
    fs_instance.mkdir("/tmp")
    fs_instance.write_file("/tmp/test.txt", """This is a temporary file.         
You can ignore it. Seriously!""")

    # Islands directory
    fs_instance.mkdir("/islands")

    # Backpack directory
    fs_instance.mkdir("/backpack")
    fs_instance.write_file("/backpack/backpack.txt", """Good old backpack. It stores your stuff.
         
You can move, copy and delete files or directories into or from it.
Try it out!
Copy the test file into the backpack:
   $ cp /tmp/test.txt /backpack/test.txt
Now check the backpack:
   $ ls /backpack""")

    # User directories
    fs_instance.mkdir("/home")

    # Island1 specific content
    fs_instance.mkdir("/islands/island1")
    fs_instance.write_file("/islands/island1/island1.txt", """This is a temporary file.         
You can ignore it. Seriously!""")
    fs_instance.mkdir("/islands/island1/ground")
    fs_instance.mkdir("/islands/island1/forest")
    fs_instance.mkdir("/islands/island1/fish_pond")

    # Add ground items for island1
    fs_instance.write_file("/islands/island1/ground/fishing_rod.item", """A sturdy fishing rod.""")
    fs_instance.write_file("/islands/island1/ground/fishing_line.item", """Strong fishing line.""")
    fs_instance.write_file("/islands/island1/ground/bucket.item", """A metal bucket for carrying things.""")

    # Add forest items for island1
    fs_instance.write_file("/islands/island1/forest/wood.item", """Pieces of wood collected from the forest.""")
    fs_instance.write_file("/islands/island1/forest/can_of_worms.item", """A tin can full of wriggling worms. Perfect for fishing.""")
    fs_instance.write_file("/islands/island1/forest/sail.item", """A large piece of cloth that could be used as a sail.""")

    # Add fish_pond directory for island1 (empty folder for fishes)
    fs_instance.mkdir("/islands/island1/fish_pond/fishes")

# Create the filesystem structure when this module is loaded.
create_initial_filesystem(fs)

# To use the filesystem elsewhere in your game, you would import `fs` from this module:
# from game.system.game_files import fs

# Example of how you might verify (optional, for testing during development):
# if __name__ == "__main__":
#     print("Verifying filesystem structure:")
#     result_ls_root = fs.list_dir("/")
#     if result_ls_root.success:
#         print(f"Root contents: {result_ls_root.value}")
#     else:
#         print(f"Error listing root: {result_ls_root.error}")

#     result_ls_tmp = fs.list_dir("/tmp")
#     if result_ls_tmp.success:
#         print(f"/tmp contents: {result_ls_tmp.value}")
#     else:
#         print(f"Error listing /tmp: {result_ls_tmp.error}")

#     result_cat_tmp_test = fs.read_file("/tmp/test.txt")
#     if result_cat_tmp_test.success:
#         print(f"Contents of /tmp/test.txt: {result_cat_tmp_test.value[:30]}...")
#     else:
#         print(f"Error reading /tmp/test.txt: {result_cat_tmp_test.error}")

#     result_ls_island1_ground = fs.list_dir("/islands/island1/ground")
#     if result_ls_island1_ground.success:
#         print(f"/islands/island1/ground contents: {result_ls_island1_ground.value}")
#     else:
#         print(f"Error listing /islands/island1/ground: {result_ls_island1_ground.error}")