from filesystem import FileSystem, Node, Directory, File
from shell import Shell
from terminal import Terminal

class System:
    def __init__(self):
        self.filesystem = FileSystem()
        self.terminal = Terminal(40, 20)
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

    def touch(self, path: str = ""):
        if path == "":
            self.terminal.print("Error: path is required.\n")
            return

        # Check if path is absolute
        if not path.startswith("/"):
            path = self.shell.cwd + "/" + path

        self.filesystem.create_file(path)

    def cat(self, path: str = ""):
        if path == "":
            self.terminal.print("Error: path is required.\n")
            return
        
        # Check if path is absolute
        if not path.startswith("/"):
            path = self.shell.cwd + "/" + path

        node = self.filesystem.get_node(path)
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

    def mkdir(self, path: str = ""):
        if path == "":
            self.terminal.print("Error: path is required.\n")
            return
        self.filesystem.create_directory(path)

    def rm(self, path: str = ""):
        if path == "":
            self.terminal.print("Error: path is required.\n")
            return

        if path == "/":
            self.terminal.print("Error: cannot delete root directory.\n")
            return
        
        # Check if path is absolute
        if not path.startswith("/"):
            path = self.shell.cwd + "/" + path

        if not self.filesystem.delete_node(path):
            self.terminal.print("Error: path does not exist.\n")

    def ls(self):
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
        self.terminal.print(out)

    def cd(self, path: str = "/"):
        # Check if path is absolute
        if not path.startswith("/"):
            path = self.shell.cwd + "/" + path

        node = self.filesystem.get_node(path)
        # Check if path exists
        if node is None:
            self.terminal.print("Error: path does not exist.\n")
            return
        
        # Check if path is a directory
        if not isinstance(node, Directory):
            self.terminal.print("Error: path is not a directory.\n")
            return
        
        self.shell.cwd = path

    def pwd(self):
        self.terminal.print(self.shell.cwd + "\n")
    

