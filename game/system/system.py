from game.system.filesystem import FileSystem, Directory, File
from game.system.shell import Shell
from game.system.terminal import Terminal
from game.system.game_files import fs as game_fs_instance
import game.manual as manual
import game.globals as g # Import globals

class System:
    def __init__(self, size_x: int, size_y: int):
        self.filesystem: FileSystem = game_fs_instance
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
        self.shell.register_cmd("man", self.man)

    def get_buffer(self):
        return self.terminal.buffer

    def process_input(self, char: str):
        self.shell.process_input(char)
    
    def clear(self):
        self.shell.clear()

    def _resolve_path(self, path_str: str) -> str:
        """
        Resolves a given path string (potentially relative) to an absolute path string
        from the perspective of the filesystem's root, using the current shell.cwd.
        Handles '.', '..', and normalizes slashes.
        """
        if not path_str: # Handle empty path_str, e.g. "cd " vs "cd"
            path_str = "." 

        full_path: str
        if path_str.startswith('/'):
            full_path = path_str
        else:
            # Relative path
            if self.shell.cwd == '/':
                full_path = '/' + path_str
            else:
                # Ensure no trailing slash on cwd before appending, unless cwd is just "/"
                cwd_normalized = self.shell.cwd.rstrip('/') if self.shell.cwd != '/' else '/'
                full_path = (cwd_normalized or '/') + '/' + path_str


        # Normalize the path:
        # Split by '/', filter out empty components (this handles multiple slashes),
        # then rejoin with single slashes, and ensure it starts with a single '/'.
        
        # Pre-normalize to handle cases like "///" or "/foo//"
        if '//' in full_path:
            import re
            full_path = re.sub(r'/+', '/', full_path)

        # Special case: if full_path became empty or just slashes after stripping, it's root.
        if not full_path.strip('/'):
            return "/"

        components = [comp for comp in full_path.split('/') if comp]
        
        resolved_components = []
        for component in components:
            if component == '.':
                continue
            elif component == '..':
                if resolved_components:
                    resolved_components.pop()
            else:
                resolved_components.append(component)

        if not resolved_components:
            return "/" 
        
        normalized_path = "/" + "/".join(resolved_components)
        
        return normalized_path

    def touch(self, user_path: str = "", *args, **kwargs):
        if not user_path:
            self.terminal.print("touch: missing file operand")
            return

        resolved_path = self._resolve_path(user_path)
        # Attempt to write an empty file. If it exists as a dir, write_file will fail.
        # If it exists as a file, its content will be set to empty (classic touch doesn't truncate, but this is fine).
        result = self.filesystem.write_file(resolved_path, "", create_parents=False) # create_parents=False for touch

        if not result.success:
            # If it's because it's a directory, write_file error will say so.
            # If it's because parent path doesn't exist, it will also error out.
            # 'touch' usually updates timestamps. Here, we ensure a file exists.
            # If the error is "path already exists and is a directory", that's not what touch does.
            # Let's check if it exists as a file. If so, it's a success for "touch" (timestamp update)
            if self.filesystem.is_file(resolved_path):
                # self.terminal.print(f"Updated timestamp for: {resolved_path}\n") # No actual timestamp
                pass # It's fine, file exists
            else:
                self.terminal.print(f"touch: cannot touch '{user_path}': {result.error}\n")


    def cat(self, user_path: str = "", *args, **kwargs):
        if not user_path:
            self.terminal.print("cat: missing file operand")
            return
        
        resolved_path = self._resolve_path(user_path)
        result = self.filesystem.read_file(resolved_path)

        if result.success:
            if result.value == "":
                # self.terminal.print("< file is empty >") # Consistent with typical cat
                pass # cat on empty file produces no output
            else:
                self.terminal.print(result.value + ("" if result.value.endswith("\n") else "\n"))
        else:
            self.terminal.print(f"cat: {user_path}: {result.error}")

    def mkdir(self, user_path: str = "", *args, **kwargs):
        if not user_path:
            self.terminal.print("mkdir: missing operand")
            return
        
        resolved_path = self._resolve_path(user_path)
        result = self.filesystem.mkdir(resolved_path, create_parents=False) # Standard mkdir doesn't create parents by default

        if not result.success:
            self.terminal.print(f"mkdir: cannot create directory '{user_path}': {result.error}\n")
        # else:
            # self.terminal.print(f"Created directory: {resolved_path}") # No output on success for mkdir usually

    def rm(self, user_path: str = "", *args, **kwargs): # Add -r later
        if not user_path:
            self.terminal.print("rm: missing operand")
            return

        resolved_path = self._resolve_path(user_path)

        if resolved_path == "/":
            self.terminal.print("rm: cannot remove root directory '/'")
            return
        
        # For 'rm' on a directory, it should fail if not empty, unless -r is specified.
        # The `delete` method's `recursive` flag handles this.
        # We need to know if it's a directory to decide on the recursive flag.
        is_dir = self.filesystem.is_dir(resolved_path)
        
        # Default to non-recursive for files, and non-recursive for dirs (will fail if not empty)
        # This matches standard 'rm' behavior without flags.
        result = self.filesystem.delete(resolved_path, recursive=False) 

        if not result.success:
            self.terminal.print(f"rm: cannot remove '{user_path}': {result.error}\n")
        # else:
            # self.terminal.print(f"Deleted: {resolved_path}") # No output on success

    def ls(self, user_ls_path: str = "", *args, **kwargs):
        target_path_str = self.shell.cwd
        if user_ls_path:
            target_path_str = self._resolve_path(user_ls_path)

        list_result = self.filesystem.list_dir(target_path_str)

        if not list_result.success:
            self.terminal.print(f"ls: cannot access '{user_ls_path or '.'}': {list_result.error}")
            return

        if not list_result.value: # Empty directory
            # self.terminal.print("< directory is empty >") # ls on empty dir produces no output
            return

        out_lines = []
        for name in sorted(list_result.value): # Sort alphabetically like typical ls
            # Construct full path for is_dir check
            # Path components must be joined carefully
            
            # Path for checks needs to be absolute from root
            path_for_check = ""
            if target_path_str == "/":
                path_for_check = "/" + name
            else:
                path_for_check = target_path_str.rstrip('/') + "/" + name
            
            if self.filesystem.is_dir(path_for_check):
                out_lines.append(f"[D] {name}")
            else: # If not a dir and it's in list_dir, assume file
                out_lines.append(f"[F] {name}")
        
        if out_lines:
            self.terminal.print("\n".join(out_lines) + "\n")


    def cd(self, user_path: str = "/", *args, **kwargs):
        # Handle `cd` (no args) -> go to home, but we don't have a user/home concept yet. Default to root.
        # current `cd` with no args `user_path` defaults to "/" which is fine.
        
        resolved_path = self._resolve_path(user_path)
        
        # Check if it's a directory first
        if not self.filesystem.is_dir(resolved_path):
            if self.filesystem.exists(resolved_path): # It exists but not a dir
                 self.terminal.print(f"cd: {user_path}: Not a directory\n")
            else: # It does not exist
                 self.terminal.print(f"cd: {user_path}: No such file or directory\n")
            return

        # No password check needed anymore
        # details_result = self.filesystem.get_directory_details(resolved_path)
        # if not details_result.success: # Should not happen if is_dir was true, but good practice
        #     self.terminal.print(f"cd: cannot access '{user_path}': {details_result.error}\n")
        #     return
        
        # dir_password = details_result.value.get('password')

        # if dir_password is not None:
        #     if password == "": # The user must provide the second arg for password
        #         self.terminal.print(f"cd: {user_path}: Password required\n")
        #         # self.terminal.print("Usage: cd <path> <password>") # Maybe too verbose
        #         return
        #     if dir_password != password:
        #         self.terminal.print(f"cd: {user_path}: Incorrect password\n")
        #         return
        
        self.shell.cwd = resolved_path
        # No output on successful cd

    def pwd(self, *args, **kwargs):
        self.terminal.print(self.shell.cwd + "\n")
    
    def tree(self, *args, **kwargs): # Remains not implemented
        self.terminal.print("tree: Not implemented.\n")

    def cp(self, in_path_str: str = "", out_path_str: str = "", *args, **kwargs):
        if not in_path_str or not out_path_str:
            self.terminal.print("cp: missing file operand\n") # or "cp: missing destination file operand after..."
            return

        resolved_in_path = self._resolve_path(in_path_str)
        resolved_out_path = self._resolve_path(out_path_str)

        if resolved_in_path == resolved_out_path:
            self.terminal.print(f"cp: '{in_path_str}' and '{out_path_str}' are the same file\n")
            return

        copy_result = self.filesystem.copy(resolved_in_path, resolved_out_path)

        if not copy_result.success:
            # Provide more specific error messages if possible, based on standard cp behavior
            # e.g. if source does not exist, or dest parent does not exist.
            # The filesystem.copy() error messages are quite generic.
            
            # Check if source exists
            if not self.filesystem.exists(resolved_in_path):
                self.terminal.print(f"cp: cannot stat '{in_path_str}': No such file or directory\n")
            # Check if dest is a dir and src is a dir trying to overwrite it (not standard)
            # The current copy does not overwrite. if resolved_out_path exists, it's an error from fs.copy
            elif "already exists" in copy_result.error and self.filesystem.is_dir(resolved_in_path) and self.filesystem.is_file(resolved_out_path):
                 self.terminal.print(f"cp: cannot overwrite non-directory '{out_path_str}' with directory '{in_path_str}'\n")
            else:
                self.terminal.print(f"cp: error copying '{in_path_str}' to '{out_path_str}': {copy_result.error}\n")
        # else: No output on success for cp

    def mv(self, in_path_str: str = "", out_path_str: str = "", *args, **kwargs):
        if not in_path_str or not out_path_str:
            self.terminal.print("mv: missing file operand\n")
            return

        resolved_in_path = self._resolve_path(in_path_str)
        resolved_out_path = self._resolve_path(out_path_str)

        if resolved_in_path == resolved_out_path:
            self.terminal.print(f"mv: '{in_path_str}' and '{out_path_str}' are the same file\n")
            return
        
        if resolved_in_path == "/":
            self.terminal.print("mv: cannot move root directory '/'\n")
            return

        move_result = self.filesystem.move(resolved_in_path, resolved_out_path)

        if not move_result.success:
            if not self.filesystem.exists(resolved_in_path):
                self.terminal.print(f"mv: cannot stat '{in_path_str}': No such file or directory\n")
            # Add more specific mv errors if needed here, similar to cp
            elif "already exists" in move_result.error and self.filesystem.is_dir(resolved_in_path) and self.filesystem.is_file(resolved_out_path):
                 self.terminal.print(f"mv: cannot overwrite non-directory '{out_path_str}' with directory '{in_path_str}'\n")
            elif "directory into itself" in move_result.error: # Error from filesystem.move
                self.terminal.print(f"mv: cannot move '{in_path_str}' to a subdirectory of itself, '{out_path_str}'\n")
            else:
                self.terminal.print(f"mv: error moving '{in_path_str}' to '{out_path_str}': {move_result.error}\n")
        # else: No output on success for mv

    def man(self, *args, **kwargs):
        self.terminal.print("Launching manual...\n")
        # manual.run() # Old way

        g.GAME_STATE = g.GAME_STATE_MANUAL
        if g.MANUAL_VIEW_INSTANCE is None:
            # We need the dimensions of the main display surface (g.WIN)
            # These are g.WIDTH and g.HEIGHT from globals.py
            g.MANUAL_VIEW_INSTANCE = manual.create_command_list_instance(
                g.DISCOVERED_COMMANDS, 
                g.WIDTH, 
                g.HEIGHT
            )
        # Potentially, we might want to re-initialize if discovered commands change
        # or pass the surface dimensions if they can change dynamically (not the case here).
        
