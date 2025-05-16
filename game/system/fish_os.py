from game.system.filesystem import FileSystem, Node, Directory, File
from game.system.shell import Shell
from game.system.terminal import Terminal

class System:
    def __init__(self, size_x: int, size_y: int):
        self.filesystem = FileSystem()
        self.terminal = Terminal(size_x, size_y)
        self.shell = Shell(self.terminal)
        self.shell.register_cmd("ls", self.ls)
        self.shell.register_cmd("pwd", self.pwd)
        self.shell.register_cmd("cd", self.cd)
        self.shell.register_cmd("touch", self.touch)
        self.shell.register_cmd("mkdir", self.mkdir)
        self.shell.register_cmd("rm", self.rm)
        self.shell.register_cmd("cat", self.cat)

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
        This method does not resolve '.' or '..'.
        """
        # This method assumes path_str is not empty, as callers should check first.
        
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

        if not components:
            # This means the path was effectively root (e.g., input "/", "///", or resolved to it).
            return "/" 
        
        # Reconstruct with a leading slash and single slashes between components.
        normalized_path = "/" + "/".join(components)
        
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
                    out += "[DIR] " + child.name + "\n"
                elif isinstance(child, File):
                    out += "[FILE] " + child.name + "\n"
        elif node is None:
            out = "Error: current directory not found.\n"
        else:
            out = "Error: current path is not a directory.\n"
        if out != "":
            self.terminal.print(out)
        else:
            self.terminal.print("< directory is empty >\n")

    def cd(self, user_path: str = "/", *args, **kwargs):
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
        
        self.shell.cwd = resolved_path

    def pwd(self, *args, **kwargs):
        self.terminal.print(self.shell.cwd + "\n")
    

