from enum import Enum
from game.system.path import FSPath # Import FSPath

# Como o código funciona?
# Nunca saberemos porque nunca leremos.
#   - Sábio Murilo

class Result:
    def __init__(self, success: bool, value=None, error: str | None = None):
        self.success: bool = success
        self.value = value
        self.error: str | None = error
        
    @classmethod
    def ok(cls, value=None) -> 'Result':
        return cls(True, value=value)
        
    @classmethod
    def err(cls, error: str) -> 'Result':
        return cls(False, error=error)

    def __repr__(self) -> str:
        if self.success:
            return f"Result.ok(value={self.value})"
        return f"Result.err(error='{self.error}')"

class Node:
    def __init__(self, name: str, parent: 'Directory | None' = None, metadata: dict[str, any] | None = None):
        self.name: str = name
        self.parent: Directory | None = parent
        self.metadata: dict[str, any] = metadata if metadata is not None else {}

    def get_path(self) -> str:
        if self.parent is None: # Should be root
            return "/" if self.name == "" or self.name == "root" else f"/{self.name}" # Special handling for root
        
        # Handle root's name potentially being empty or "root"
        parent_path = self.parent.get_path()
        if parent_path == "/":
            return f"/{self.name}"
        return f"{parent_path}/{self.name}"
    
    def accept(self, visitor: 'FSVisitor'):
        # To be implemented by subclasses
        raise NotImplementedError


class Directory(Node):
    def __init__(self, name: str, parent: 'Directory | None' = None, children: list[Node] | None = None, metadata: dict[str, any] | None = None):
        super().__init__(name, parent, metadata)
        self.children: list[Node] = children if children is not None else []

    def find_child(self, name: str) -> Node | None:
        for child in self.children:
            if child.name == name:
                return child
        return None

    def add_child(self, node: Node) -> bool:
        if self.find_child(node.name):
            return False # Child with same name already exists
        node.parent = self
        self.children.append(node)
        return True

    def remove_child(self, name: str) -> bool:
        child_to_remove = self.find_child(name)
        if child_to_remove:
            self.children.remove(child_to_remove)
            child_to_remove.parent = None
            return True
        return False
    
    def accept(self, visitor: 'FSVisitor'):
        visitor.visit_directory(self)


class File(Node):
    def __init__(self, name: str, parent: Directory | None = None, contents: str = "", metadata: dict[str, any] | None = None):
        super().__init__(name, parent, metadata)
        self.contents: str = contents
    
    def accept(self, visitor: 'FSVisitor'):
        visitor.visit_file(self)


class FileSystem:
    def __init__(self):
        # The root directory's name is effectively empty for path purposes,
        # or could be considered "root" internally if needed for the Node object itself.
        # FSPath("/") will have an empty `name` and empty `components`.
        self.root: Directory = Directory("", parent=None) # Root node's name is empty for path logic

    def _resolve_path(self, path_str: str, create_parents: bool = False, must_be_dir: bool | None = None, target_must_exist: bool = True) -> Result:
        """
        Resolves a path string to a Node.
        path_str: The string representation of the path.
        create_parents: If True, creates missing parent directories.
        must_be_dir: If True, the resolved node must be a Directory. If False, must be a File. If None, can be either.
        target_must_exist: If True, the final component of the path must exist. If False, resolves to the parent of the final component.
        """
        if not path_str:
            return Result.err("Path cannot be empty.")

        fspath = FSPath(path_str)
        
        current_node: Node = self.root

        components_to_traverse = fspath.components
        if not target_must_exist: # If we are creating the target, we resolve to its would-be parent
            if not components_to_traverse: # e.g. creating "/foo" from "/", target is foo, parent is root
                 if fspath.is_root(): # Trying to "create" root?
                     return Result.err("Cannot get parent of root to create it.")
                 # This case means we are trying to create something directly under root.
                 # The loop below will be skipped, current_node remains self.root.
            else:
                components_to_traverse = fspath.components[:-1]


        for i, component_name in enumerate(components_to_traverse):
            if not isinstance(current_node, Directory):
                return Result.err(f"Path component '{component_name}' in '{fspath}' is not a directory.")
            
            next_node = current_node.find_child(component_name)
            
            if next_node is None:
                if create_parents and target_must_exist: # Only create parents if resolving target that should exist
                    new_dir = Directory(component_name, current_node)
                    current_node.add_child(new_dir)
                    current_node = new_dir
                elif create_parents and not target_must_exist and i < len(fspath.components) -1 : # creating parents for a new node
                    new_dir = Directory(component_name, current_node)
                    current_node.add_child(new_dir)
                    current_node = new_dir
                else:
                    return Result.err(f"Path component '{component_name}' not found in '{fspath}'.")
            else:
                current_node = next_node

        # After loop, current_node is the parent if !target_must_exist, or the target itself if target_must_exist
        if target_must_exist:
            resolved_node = current_node
            # If fspath.components is empty, it means fspath was root.
            # The loop is skipped, current_node is self.root.
            if not fspath.components and fspath.is_root():
                 resolved_node = self.root
            elif fspath.components and resolved_node.name != fspath.name() and resolved_node == self.root:
                # This can happen if path is like "/file" and root has no children
                # or if path is just "file" (relative) and we are at root
                # We need to find the actual child if it exists
                final_target = self.root.find_child(fspath.name())
                if final_target:
                    resolved_node = final_target
                else:
                    return Result.err(f"Path '{fspath}' not found.")


        else: # We resolved the parent for a new node
            resolved_node = current_node # This is the parent directory

        # Type checking for the final resolved node (if target_must_exist)
        if target_must_exist:
            if must_be_dir is True and not isinstance(resolved_node, Directory):
                return Result.err(f"Path '{fspath}' exists but is not a directory.")
            if must_be_dir is False and not isinstance(resolved_node, File):
                return Result.err(f"Path '{fspath}' exists but is not a file.")
        
        return Result.ok(resolved_node)

    def read_file(self, path_str: str) -> Result:
        resolve_result = self._resolve_path(path_str, must_be_dir=False, target_must_exist=True)
        if not resolve_result.success:
            return resolve_result
        
        file_node = resolve_result.value
        if not isinstance(file_node, File): # Should be caught by must_be_dir=False
             return Result.err(f"Path '{path_str}' is not a file.")
        return Result.ok(file_node.contents)

    def write_file(self, path_str: str, contents: str, create_parents: bool = False, metadata: dict[str, any] | None = None) -> Result:
        fspath = FSPath(path_str)
        if fspath.is_root():
            return Result.err("Cannot write to root path directly as a file.")
        
        file_name = fspath.name()
        parent_path_str = str(fspath.parent())

        # Resolve parent directory, creating if necessary
        parent_resolve_result = self._resolve_path(parent_path_str, create_parents=create_parents, must_be_dir=True, target_must_exist=True)
        if not parent_resolve_result.success:
            return parent_resolve_result
        
        parent_dir = parent_resolve_result.value
        if not isinstance(parent_dir, Directory): # Should be caught by must_be_dir=True
             return Result.err(f"Parent path for '{path_str}' is not a directory.")

        existing_node = parent_dir.find_child(file_name)
        if existing_node:
            if isinstance(existing_node, File):
                existing_node.contents = contents
                return Result.ok(existing_node)
            else:
                return Result.err(f"Path '{path_str}' already exists and is a directory.")
        else:
            new_file = File(name=file_name, parent=parent_dir, contents=contents, metadata=metadata)
            parent_dir.add_child(new_file)
            return Result.ok(new_file)

    def mkdir(self, path_str: str, create_parents: bool = False, metadata: dict[str, any] | None = None) -> Result:
        fspath = FSPath(path_str)
        if fspath.is_root():
            return Result.ok(self.root) # Making root directory is idempotent

        dir_name = fspath.name()
        parent_path_str = str(fspath.parent())

        # Resolve parent directory
        parent_resolve_result = self._resolve_path(parent_path_str, create_parents=create_parents, must_be_dir=True, target_must_exist=True)
        if not parent_resolve_result.success:
            # This error occurs if create_parents is False and parent doesn't exist,
            # or if a component of the parent path is a file.
            return parent_resolve_result
        
        parent_dir = parent_resolve_result.value
        if not isinstance(parent_dir, Directory):
             return Result.err(f"Could not find or create parent directory for '{path_str}'. Path component is not a directory.")


        existing_node = parent_dir.find_child(dir_name)
        if existing_node:
            if isinstance(existing_node, Directory):
                return Result.ok(existing_node) # Directory already exists
            else:
                return Result.err(f"Path '{path_str}' already exists and is a file.")
        else:
            new_dir = Directory(name=dir_name, parent=parent_dir, metadata=metadata)
            parent_dir.add_child(new_dir)
            return Result.ok(new_dir)

    def exists(self, path_str: str) -> bool:
        return self._resolve_path(path_str, target_must_exist=True).success

    def is_file(self, path_str: str) -> bool:
        resolve_result = self._resolve_path(path_str, must_be_dir=False, target_must_exist=True)
        return resolve_result.success and isinstance(resolve_result.value, File)

    def is_dir(self, path_str: str) -> bool:
        resolve_result = self._resolve_path(path_str, must_be_dir=True, target_must_exist=True)
        return resolve_result.success and isinstance(resolve_result.value, Directory)

    def list_dir(self, path_str: str) -> Result:
        resolve_result = self._resolve_path(path_str, must_be_dir=True, target_must_exist=True)
        if not resolve_result.success:
            return resolve_result
        
        dir_node = resolve_result.value
        if not isinstance(dir_node, Directory): # Should be caught by must_be_dir=True
             return Result.err(f"Path '{path_str}' is not a directory.")
        return Result.ok([child.name for child in dir_node.children])

    def get_directory_details(self, path_str: str) -> Result:
        resolve_result = self._resolve_path(path_str, must_be_dir=True, target_must_exist=True)
        if not resolve_result.success:
            return resolve_result
        
        dir_node = resolve_result.value
        # Ensured by must_be_dir=True in _resolve_path, but double check for safety
        if not isinstance(dir_node, Directory):
            return Result.err(f"Path '{path_str}' is not a directory.")
            
        return Result.ok({}) # No password to return, return empty dict or specific details later

    def _deep_copy_node(self, node: Node, new_parent: Directory) -> Node:
        if isinstance(node, File):
            return File(name=node.name, parent=new_parent, contents=node.contents, metadata=node.metadata.copy())
        elif isinstance(node, Directory):
            new_dir = Directory(name=node.name, parent=new_parent, children=[], metadata=node.metadata.copy())
            for child in node.children:
                copied_child = self._deep_copy_node(child, new_dir)
                new_dir.children.append(copied_child) # Directly append, parent set in _deep_copy_node
            return new_dir
        raise TypeError("Unknown node type")


    def copy(self, src_path_str: str, dst_path_str: str) -> Result:
        src_resolve_result = self._resolve_path(src_path_str, target_must_exist=True)
        if not src_resolve_result.success:
            return Result.err(f"Source path '{src_path_str}' not found. Error: {src_resolve_result.error}")
        src_node = src_resolve_result.value

        dst_fspath = FSPath(dst_path_str)
        
        # Determine the actual destination parent directory and the name for the new node
        dst_parent_path_str: str
        new_node_name: str

        # Try to resolve dst_path_str as a directory first.
        # If it resolves to a directory, that's our target parent. New node keeps its original name.
        dst_as_dir_resolve = self._resolve_path(dst_path_str, must_be_dir=True, create_parents=False, target_must_exist=True)

        if dst_as_dir_resolve.success: # Destination is an existing directory
            dst_parent_dir = dst_as_dir_resolve.value
            new_node_name = src_node.name # Copy into this directory with original name
        else:
            # Destination is not an existing directory.
            # It could be a new name in an existing directory, or needs parent creation.
            dst_parent_fspath = dst_fspath.parent()
            new_node_name = dst_fspath.name()
            
            # Resolve the parent of the destination path
            dst_parent_resolve_result = self._resolve_path(str(dst_parent_fspath), create_parents=True, must_be_dir=True, target_must_exist=True)
            if not dst_parent_resolve_result.success:
                return Result.err(f"Could not resolve or create destination parent directory '{dst_parent_fspath}'. Error: {dst_parent_resolve_result.error}")
            dst_parent_dir = dst_parent_resolve_result.value

        if not isinstance(dst_parent_dir, Directory):
             return Result.err(f"Destination parent '{dst_parent_dir.get_path()}' is not a directory.")


        if dst_parent_dir.find_child(new_node_name):
            return Result.err(f"Destination path '{dst_parent_dir.get_path()}/{new_node_name}' already exists.")

        # Ensure src is not an ancestor of dst_parent_dir if src is a directory (to prevent recursive copy into self)
        if isinstance(src_node, Directory):
            temp_parent = dst_parent_dir
            while temp_parent is not None:
                if temp_parent == src_node:
                    return Result.err("Cannot copy a directory into itself or one of its subdirectories.")
                # Check if temp_parent.parent is None, which means it's the root's direct child or the root itself.
                # The root node in this implementation has parent=None.
                if temp_parent.parent is None and temp_parent != self.root : # Should not happen if structure is correct
                    break 
                if temp_parent == self.root and src_node != self.root: # temp_parent is root, check if src_node is also root
                     break # Reached root, src_node is not an ancestor
                if temp_parent == self.root and src_node == self.root: # Copying root into a subdir of root
                    return Result.err("Cannot copy a directory into itself or one of its subdirectories.")

                temp_parent = temp_parent.parent


        copied_node = self._deep_copy_node(src_node, dst_parent_dir)
        copied_node.name = new_node_name # Ensure the copied node has the correct target name
        
        # Detach the copied_node from the parent it was assigned during _deep_copy_node
        # as add_child will re-establish this relationship.
        # This is a bit of a workaround for _deep_copy_node setting parent.
        # A cleaner way would be for _deep_copy_node not to set parent,
        # and let the caller (copy method) do it.
        copied_node.parent = None # Temporarily detach for add_child to work cleanly

        if dst_parent_dir.add_child(copied_node):
            return Result.ok(copied_node)
        else:
            # This should ideally not happen if the previous check for existence was correct.
            return Result.err(f"Failed to add copied node to destination '{dst_parent_dir.get_path()}'. A node with name '{new_node_name}' might have been created concurrently or check logic error.")


    def move(self, src_path_str: str, dst_path_str: str) -> Result:
        src_resolve_result = self._resolve_path(src_path_str, target_must_exist=True)
        if not src_resolve_result.success:
            return Result.err(f"Source path '{src_path_str}' not found. Error: {src_resolve_result.error}")
        src_node = src_resolve_result.value
        
        if src_node == self.root:
            return Result.err("Cannot move the root directory.")

        original_parent = src_node.parent
        if not original_parent: # Should not happen for non-root nodes
            return Result.err(f"Source node '{src_path_str}' has no parent, cannot move.")

        dst_fspath = FSPath(dst_path_str)
        
        # Determine the actual destination parent directory and the name for the new node
        dst_parent_path_str: str
        new_node_name: str

        dst_as_dir_resolve = self._resolve_path(dst_path_str, must_be_dir=True, create_parents=False, target_must_exist=True)

        if dst_as_dir_resolve.success: # Destination is an existing directory
            dst_parent_dir = dst_as_dir_resolve.value
            new_node_name = src_node.name 
        else:
            # Destination is not an existing directory.
            dst_parent_fspath = dst_fspath.parent()
            new_node_name = dst_fspath.name()
            
            dst_parent_resolve_result = self._resolve_path(str(dst_parent_fspath), create_parents=False, must_be_dir=True, target_must_exist=True) # No create_parents for move dest parent
            if not dst_parent_resolve_result.success:
                return Result.err(f"Destination parent directory '{dst_parent_fspath}' does not exist. Error: {dst_parent_resolve_result.error}")
            dst_parent_dir = dst_parent_resolve_result.value
        
        if not isinstance(dst_parent_dir, Directory):
             return Result.err(f"Destination parent '{dst_parent_dir.get_path()}' is not a directory.")

        if dst_parent_dir.find_child(new_node_name):
            return Result.err(f"Destination path '{dst_parent_dir.get_path()}/{new_node_name}' already exists.")

        # Prevent moving a directory into itself or a subdirectory
        if isinstance(src_node, Directory):
            temp_parent = dst_parent_dir
            while temp_parent is not None:
                if temp_parent == src_node:
                    return Result.err("Cannot move a directory into itself or one of its subdirectories.")
                if temp_parent.parent is None and temp_parent != self.root: break
                if temp_parent == self.root: break
                temp_parent = temp_parent.parent
        
        # Perform the move
        if not original_parent.remove_child(src_node.name):
             return Result.err(f"Failed to remove source node '{src_node.name}' from original parent '{original_parent.get_path()}'. This indicates an internal inconsistency.") # Should not happen

        src_node.name = new_node_name # Update name if dst_path_str implies a rename
        # src_node.parent will be set by add_child
        if dst_parent_dir.add_child(src_node):
            return Result.ok(src_node)
        else:
            # Rollback: try to add it back to original parent if adding to new parent failed
            # This is a simplified rollback, a more robust one might be needed for complex scenarios.
            src_node.name = original_parent.find_child(src_node.name) # Revert name if it was changed for new dest
            original_parent.add_child(src_node)
            return Result.err(f"Failed to add node to destination '{dst_parent_dir.get_path()}'. Move operation failed and attempted to rollback.")


    def delete(self, path_str: str, recursive: bool = False) -> Result:
        resolve_result = self._resolve_path(path_str, target_must_exist=True)
        if not resolve_result.success:
            return resolve_result
        
        node_to_delete = resolve_result.value

        if node_to_delete == self.root:
            return Result.err("Cannot delete the root directory.")
            
        if node_to_delete.parent is None: # Should only be root, caught above
            return Result.err(f"Node '{path_str}' has no parent. Cannot delete.")

        parent_dir = node_to_delete.parent
        
        if isinstance(node_to_delete, Directory):
            if node_to_delete.children and not recursive:
                return Result.err(f"Directory '{path_str}' is not empty. Use recursive=True to delete.")
        
        if parent_dir.remove_child(node_to_delete.name):
            return Result.ok()
        else:
            # This case should ideally not be reached if resolve_path and find_child work correctly.
            return Result.err(f"Failed to delete node '{path_str}'. Node not found in parent's children list.")

    def set_metadata(self, path_str: str, key: str, value: any) -> Result:
        resolve_result = self._resolve_path(path_str, target_must_exist=True)
        if not resolve_result.success:
            return resolve_result
        node = resolve_result.value
        node.metadata[key] = value
        return Result.ok()

    def get_metadata(self, path_str: str, key: str) -> Result:
        resolve_result = self._resolve_path(path_str, target_must_exist=True)
        if not resolve_result.success:
            return resolve_result
        node = resolve_result.value
        if key not in node.metadata:
            return Result.err(f"Metadata key '{key}' not found for '{path_str}'.")
        return Result.ok(node.metadata[key])

    def remove_metadata(self, path_str: str, key: str) -> Result:
        resolve_result = self._resolve_path(path_str, target_must_exist=True)
        if not resolve_result.success:
            return resolve_result
        node = resolve_result.value
        if key not in node.metadata:
            return Result.err(f"Metadata key '{key}' not found for '{path_str}'.")
        del node.metadata[key]
        return Result.ok()

    def get_all_metadata(self, path_str: str) -> Result:
        resolve_result = self._resolve_path(path_str, target_must_exist=True)
        if not resolve_result.success:
            return resolve_result
        node = resolve_result.value
        return Result.ok(node.metadata.copy()) # Return a copy to prevent external modification

class FSVisitor:
    def visit_file(self, file_node: File):
        pass
        
    def visit_directory(self, directory_node: Directory):
        pass

# Example Visitor
class PrintVisitor(FSVisitor):
    def __init__(self, indent_char: str = "  "):
        self.current_indent = ""
        self.indent_char = indent_char

    def visit_file(self, file_node: File):
        print(f"{self.current_indent}File: {file_node.name} (Path: {file_node.get_path()})")
        
    def visit_directory(self, directory_node: Directory):
        print(f"{self.current_indent}Dir: {directory_node.name} (Path: {directory_node.get_path()})")
        
        original_indent = self.current_indent
        self.current_indent += self.indent_char
        for child in directory_node.children:
            child.accept(self) # Polymorphic call to accept
        self.current_indent = original_indent

# Old FileSystem methods to be removed or adapted:
# copy_path, _copy_directory, get_node (replaced by _resolve_path), create_node, create_file, create_directory, delete_node
# The old methods were removed by replacing the entire FileSystem class.
# The original Node, Directory, File classes have been modified at the top.
