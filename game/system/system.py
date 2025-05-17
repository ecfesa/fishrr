from game.system.filesystem import FileSystem, Node, Directory, File
from game.system.shell import Shell
from game.system.terminal import Terminal
from game.system.path import Path
from game.system.game_files import GAME_ROOT

class System:
    def __init__(self, size_x: int, size_y: int):
        self.filesystem = FileSystem(GAME_ROOT)
        self.terminal = Terminal(size_x, size_y)
        self.shell = Shell(self.terminal)
        self.shell.register_cmd("ls", self.ls)
        self.shell.register_cmd("pwd", self.pwd)
        self.shell.register_cmd("cd", self.cd)
        self.shell.register_cmd("touch", self.touch)
        self.shell.register_cmd("mkdir", self.mkdir)
        self.shell.register_cmd("rm", self.rm)
        self.shell.register_cmd("cp", self.cp)
        self.shell.register_cmd("mv", self.mv)
        self.shell.register_cmd("cat", self.cat)
        self.shell.register_cmd("tree", self.tree)

    def get_buffer(self):
        return self.terminal.buffer

    def process_input(self, char: str):
        self.shell.process_input(char)
    
    def clear(self):
        self.shell.clear()

    def _resolve_path(self, path_str: str) -> str:
        """
        Resolves a given path string to an absolute path, handling CWD
        and cleaning up redundant slashes like '//' or trailing '/'.
        This method resolves '.' and '..'.
    
        Assumes path_str is not empty, as callers should check first.
        """
        
        full_path: str
        if path_str.startswith('/'):
            full_path = path_str
        else:
            # Relative path
            if self.shell.cwd == '/':
                full_path = '/' + path_str # Avoids '//file'
            else:
                full_path = self.shell.cwd + '/' + path_str # e.g., "/home" + "/" + "file"

        # Normalize the path:
        # Split by '/', filter out empty components (this handles multiple slashes),
        # then rejoin with single slashes, and ensure it starts with a single '/'.
        components = [comp for comp in full_path.split('/') if comp]
        
        # Resolve '.' and '..'
        resolved_components = []
        for component in components:
            if component == '.':
                continue
            elif component == '..':
                if resolved_components: # Check if there's a component to pop
                    resolved_components.pop()
            else:
                resolved_components.append(component)

        if not resolved_components:
            # This means the path was effectively root (e.g., input "/", "///", or resolved to it).
            return "/" 
        
        # Reconstruct with a leading slash and single slashes between components.
        normalized_path = "/" + "/".join(resolved_components)
        
        return normalized_path

    def touch(self, user_path: str = "", *args, **kwargs):
        if not user_path:
            self.terminal.print("Error: path is required.\n")
            return

        resolved_path = self._resolve_path(user_path)
        self.filesystem.create_file(resolved_path)
        self.terminal.print(f"Created file: {resolved_path}\n")

    def cat(self, user_path: str = "", *args, **kwargs):
        if not user_path:
            self.terminal.print("Error: path is required.\n")
            return
        
        resolved_path = self._resolve_path(user_path)
        node = self.filesystem.get_node(resolved_path)
        if node is None:
            self.terminal.print("Error: path does not exist.\n")
            return
        
        if isinstance(node, File):
            if node.contents == "":
                self.terminal.print("< file is empty >\n")
            else:
                self.terminal.print(node.contents + "\n")
        else:
            self.terminal.print("Error: path is not a file.\n")

    def mkdir(self, user_path: str = "", *args, **kwargs):
        if not user_path:
            self.terminal.print("Error: path is required.\n")
            return
        
        resolved_path = self._resolve_path(user_path)

        # Check if path already exists
        if self.filesystem.get_node(resolved_path) is not None:
            self.terminal.print("Error: path already exists.\n")
            return

        self.filesystem.create_directory(resolved_path)
        self.terminal.print(f"Created directory: {resolved_path}\n")

    def rm(self, user_path: str = "", *args, **kwargs):
        if not user_path:
            self.terminal.print("Error: path is required.\n")
            return

        resolved_path = self._resolve_path(user_path)

        if resolved_path == "/":
            self.terminal.print("Error: cannot delete root directory.\n")
            return
        
        if not self.filesystem.delete_node(resolved_path):
            self.terminal.print("Error: path does not exist.\n")
        else:
            self.terminal.print(f"Deleted: {resolved_path}\n")

    def ls(self, *args, **kwargs):
        out = ""
        node = self.filesystem.get_node(self.shell.cwd)
        if isinstance(node, Directory):
            children = node.children
            for child in children:
                if isinstance(child, Directory):
                    out += "📁 " + child.name + "\n"
                elif isinstance(child, File):
                    out += "🗎 " + child.name + "\n"
        elif node is None:
            out = "Error: current directory not found.\n"
        else:
            out = "Error: current path is not a directory.\n"
        if out != "":
            self.terminal.print(out)
        else:
            self.terminal.print("< directory is empty >\n")

    def cd(self, user_path: str = "/", password: str = "", *args, **kwargs):
        # An empty user_path (e.g. from `cd ""`) will be resolved to the current directory
        # by _resolve_path, which is acceptable though not standard for `cd ""`.
        # `cd` with no args defaults user_path to "/", which is correctly handled.
        resolved_path = self._resolve_path(user_path)

        node = self.filesystem.get_node(resolved_path)
        # Check if path exists
        if node is None:
            self.terminal.print("Error: path does not exist.\n")
            return
        
        # Check if path is a directory
        if not isinstance(node, Directory):
            self.terminal.print("Error: path is not a directory.\n")
            return

        if node.password is not None and password == "":
            self.terminal.print("Error: password is required to access this directory.\n")
            self.terminal.print("Usage: cd <path> <password>\n")
            return

        if node.password is not None and node.password != password:
            self.terminal.print("Error: incorrect password.\n")
            return
        
        self.shell.cwd = resolved_path

    def pwd(self, *args, **kwargs):
        self.terminal.print(self.shell.cwd + "\n")
    
    # Not the real tree command. Shows the game map instead.
    def tree(self, *args, **kwargs):
        self.terminal.print("Not implemented.\n")

    def cp(self, in_path_str: str = "", out_path_str: str = "", *args, **kwargs):
        if not in_path_str or not out_path_str:
            self.terminal.print("Error: both source and destination paths are required.\n")
            return

        in_path = Path(in_path_str, self.shell.cwd)
        out_path = Path(out_path_str, self.shell.cwd)

        in_node = self.filesystem.get_node(in_path.path)
        if in_node is None:
            self.terminal.print(f"Error: source path '{in_path.path}' does not exist.\n")
            return
        
        out_node = self.filesystem.get_node(out_path.path)
        
        # Determine the target path for the copy operation
        if out_node is None:
            # Check if the parent directory exists (for creating new file/dir)
            parent_path = out_path.up().path
            parent_node = self.filesystem.get_node(parent_path)
            
            if parent_node is None:
                self.terminal.print(f"Error: destination directory '{parent_path}' does not exist.\n")
                return
                
            if not isinstance(parent_node, Directory):
                self.terminal.print(f"Error: destination '{parent_path}' is not a directory.\n")
                return
                
            # If out_path doesn't exist but its parent does, we're copying to a new node with the name from out_path
            # For this case, we'll use copy_path with the parent directory as the destination
            # and then rename the copied node to match the last part of out_path
            
            # Get the name for the new node from the last part of out_path
            new_name = out_path.path.split('/')[-1] if out_path.path != '/' else in_node.name
            
            # Copy to the parent directory
            if not self.filesystem.copy_path(in_path.path, parent_path):
                self.terminal.print(f"Error: could not copy '{in_path.path}' to '{parent_path}'.\n")
                return
                
            # Get the newly created node (which has the same name as source)
            copied_node = None
            for child in parent_node.children:
                if child.name == in_node.name:
                    copied_node = child
                    break
                    
            # Rename it to match the desired name
            if copied_node:
                copied_node.name = new_name
                self.terminal.print(f"Copied '{in_path.path}' to '{out_path.path}'.\n")
            
        else:
            # If out_node exists
            if isinstance(out_node, Directory):
                # Copy to inside the directory
                if self.filesystem.copy_path(in_path.path, out_path.path):
                    self.terminal.print(f"Copied '{in_path.path}' to '{out_path.path}/{in_node.name}'.\n")
                else:
                    self.terminal.print(f"Error: could not copy '{in_path.path}' to '{out_path.path}'.\n")
            else:
                # Can't copy directory to file
                if isinstance(in_node, Directory) and isinstance(out_node, File):
                    self.terminal.print(f"Error: cannot overwrite file '{out_path.path}' with directory '{in_path.path}'.\n")
                    return
                
                # Copy to parent directory and overwrite out_node
                parent_path = out_path.up().path
                if self.filesystem.copy_path(in_path.path, parent_path):
                    # Get the parent node
                    parent_node = self.filesystem.get_node(parent_path)
                    
                    # Find the copied node in parent's children
                    for i, child in enumerate(parent_node.children):
                        if child.name == in_node.name:
                            # Rename to match destination file name
                            child.name = out_path.path.split('/')[-1]
                            self.terminal.print(f"Copied '{in_path.path}' to '{out_path.path}'.\n")
                            return
                    
                    self.terminal.print(f"Error: copy operation succeeded but unable to find copied node.\n")
                else:
                    self.terminal.print(f"Error: could not copy '{in_path.path}' to '{out_path.path}'.\n")
        
    def mv(self, in_path_str: str = "", out_path_str: str = "", *args, **kwargs):
        if not in_path_str or not out_path_str:
            self.terminal.print("Error: both source and destination paths are required.\n")
            return

        in_path = Path(in_path_str, self.shell.cwd)
        out_path = Path(out_path_str, self.shell.cwd)

        in_node = self.filesystem.get_node(in_path.path)
        if in_node is None:
            self.terminal.print(f"Error: source path '{in_path.path}' does not exist.\n")
            return

        # Cannot move the root directory
        if in_path.path == "/":
            self.terminal.print("Error: cannot move root directory.\n")
            return
        
        out_node = self.filesystem.get_node(out_path.path)
        
        # Special case for rename in the same directory
        if out_node is None and in_path.up().path == out_path.up().path:
            # This is a rename operation in the same directory
            parent_path = in_path.up().path
            parent_node = self.filesystem.get_node(parent_path)
            
            if parent_node is None:
                self.terminal.print(f"Error: parent directory '{parent_path}' does not exist.\n")
                return
                
            # Simply rename the node
            new_name = out_path.path.split('/')[-1]
            for child in parent_node.children:
                if child.name == in_node.name:
                    child.name = new_name
                    self.terminal.print(f"Moved '{in_path.path}' to '{out_path.path}'.\n")
                    return
                    
            self.terminal.print(f"Error: failed to rename '{in_path.path}'.\n")
            return
        
        # Special case for overwriting a file in the same directory
        if out_node is not None and not isinstance(out_node, Directory) and in_path.up().path == out_path.up().path:
            # This is an overwrite operation in the same directory
            parent_path = in_path.up().path
            parent_node = self.filesystem.get_node(parent_path)
            
            # Remove the destination node first
            for i, child in enumerate(parent_node.children):
                if child.name == out_node.name:
                    # If source is a directory and destination is a file, error out
                    if isinstance(in_node, Directory) and isinstance(child, File):
                        self.terminal.print(f"Error: cannot overwrite file '{out_path.path}' with directory '{in_path.path}'.\n")
                        return
                    
                    # Remove the destination node
                    parent_node.children.pop(i)
                    break
            
            # Now rename the source node to the destination name
            for i, child in enumerate(parent_node.children):
                if child.name == in_node.name:
                    child.name = out_path.path.split('/')[-1]
                    self.terminal.print(f"Moved '{in_path.path}' to '{out_path.path}'.\n")
                    return
                    
            self.terminal.print(f"Error: failed to move '{in_path.path}'.\n")
            return
        
        # Determine the target path for the move operation
        if out_node is None:
            # Check if the parent directory exists (for moving to a new path)
            parent_path = out_path.up().path
            parent_node = self.filesystem.get_node(parent_path)
            
            if parent_node is None:
                self.terminal.print(f"Error: destination directory '{parent_path}' does not exist.\n")
                return
                
            if not isinstance(parent_node, Directory):
                self.terminal.print(f"Error: destination '{parent_path}' is not a directory.\n")
                return
                
            # Get the name for the new node from the last part of out_path
            new_name = out_path.path.split('/')[-1] if out_path.path != '/' else in_node.name
            
            # Copy to the parent directory
            if not self.filesystem.copy_path(in_path.path, parent_path):
                self.terminal.print(f"Error: could not move '{in_path.path}' to '{parent_path}'.\n")
                return
                
            # Get the newly created node (which has the same name as source)
            moved_node = None
            for child in parent_node.children:
                if child.name == in_node.name:
                    moved_node = child
                    break
                    
            # Rename it to match the desired name
            if moved_node:
                moved_node.name = new_name
                
                # Delete the original node
                if self.filesystem.delete_node(in_path.path):
                    self.terminal.print(f"Moved '{in_path.path}' to '{out_path.path}'.\n")
                else:
                    self.terminal.print(f"Warning: copied to '{out_path.path}' but failed to remove original '{in_path.path}'.\n")
            
        else:
            # If out_node exists
            if isinstance(out_node, Directory):
                # Move to inside the directory
                if self.filesystem.copy_path(in_path.path, out_path.path):
                    # Delete the original node
                    if self.filesystem.delete_node(in_path.path):
                        self.terminal.print(f"Moved '{in_path.path}' to '{out_path.path}/{in_node.name}'.\n")
                    else:
                        self.terminal.print(f"Warning: copied to '{out_path.path}/{in_node.name}' but failed to remove original '{in_path.path}'.\n")
                else:
                    self.terminal.print(f"Error: could not move '{in_path.path}' to '{out_path.path}'.\n")
            else:
                # Can't move directory to file
                if isinstance(in_node, Directory) and isinstance(out_node, File):
                    self.terminal.print(f"Error: cannot overwrite file '{out_path.path}' with directory '{in_path.path}'.\n")
                    return
                
                # Move to parent directory and overwrite out_node
                parent_path = out_path.up().path
                if self.filesystem.copy_path(in_path.path, parent_path):
                    # Get the parent node
                    parent_node = self.filesystem.get_node(parent_path)
                    
                    # Find the copied node in parent's children
                    for i, child in enumerate(parent_node.children):
                        if child.name == in_node.name:
                            # Rename to match destination file name
                            child.name = out_path.path.split('/')[-1]
                            
                            # Delete the original node
                            if self.filesystem.delete_node(in_path.path):
                                self.terminal.print(f"Moved '{in_path.path}' to '{out_path.path}'.\n")
                            else:
                                self.terminal.print(f"Warning: copied to '{out_path.path}' but failed to remove original '{in_path.path}'.\n")
                            return
                    
                    self.terminal.print(f"Error: move operation partially succeeded but unable to find moved node.\n")
                else:
                    self.terminal.print(f"Error: could not move '{in_path.path}' to '{out_path.path}'.\n")
        
        
        
