from enum import Enum
from game.system.path import Path

class Node:
    def __init__(self, name: str, parent = None, password: str | None = None):
        self.name: str = name
        self.parent: Node | None = parent
        self.password: str | None = password
    
    def add_child(self, child):
        child.parent = self
        self.children.append(child)

class Directory(Node):
    def __init__(self, name: str, parent = None, children: list[Node] = [], password: str | None = None):
        super().__init__(name, parent, password)
        self.children: list[Node] = children

class File(Node):
    def __init__(self, name: str, parent = None, contents: str = "", password: str | None = None):
        super().__init__(name, parent, password)
        self.contents = contents

class FileSystem:
    def __init__(self, root: Directory):
        self.root = root
    
    def copy_path(self, in_path, out_path):
        """
        Copy a node from in_path to out_path.
        
        Parameters:
        - in_path: Path or str - Path to the source node
        - out_path: Path or str - Path to the destination directory
        
        Returns:
        - bool: True if successful, False otherwise
        """
        # Convert path strings to strings if they're Path objects
        in_path_str = in_path.path if hasattr(in_path, 'path') else in_path
        out_path_str = out_path.path if hasattr(out_path, 'path') else out_path
        
        in_node = self.get_node(in_path_str)
        if in_node is None:
            return False
        
        out_node = self.get_node(out_path_str)
        if out_node is None:
            return False
        
        if not isinstance(out_node, Directory):
            return False
        
        # Create a copy of the node instead of reusing the same reference
        if isinstance(in_node, File):
            # Always create a new node with the original name (not replacing)
            new_node = File(in_node.name, out_node, in_node.contents, in_node.password)
            out_node.children.append(new_node)
        elif isinstance(in_node, Directory):
            # Create a new directory with same properties
            new_node = Directory(in_node.name, out_node, [], in_node.password)
            out_node.children.append(new_node)
            
            # Recursively copy all children
            for child in in_node.children:
                if isinstance(child, File):
                    child_copy = File(child.name, new_node, child.contents, child.password)
                    new_node.children.append(child_copy)
                elif isinstance(child, Directory):
                    # For directories, we need to handle them recursively
                    self._copy_directory(child, new_node)
        
        return True
        
    def _copy_directory(self, src_dir: Directory, dst_parent: Directory):
        """Helper method to recursively copy directory contents"""
        # Create new directory node
        new_dir = Directory(src_dir.name, dst_parent, [], src_dir.password)
        
        # Check if a directory with the same name already exists
        existing_dir_index = None
        for i, child in enumerate(dst_parent.children):
            if child.name == new_dir.name:
                existing_dir_index = i
                break
        
        if existing_dir_index is not None:
            # Replace existing directory
            dst_parent.children[existing_dir_index] = new_dir
        else:
            # Add as new directory
            dst_parent.children.append(new_dir)
        
        # Copy all children
        for child in src_dir.children:
            if isinstance(child, File):
                file_copy = File(child.name, new_dir, child.contents, child.password)
                
                # Check if a file with the same name already exists
                existing_file_index = None
                for i, existing_child in enumerate(new_dir.children):
                    if existing_child.name == file_copy.name:
                        existing_file_index = i
                        break
                
                if existing_file_index is not None:
                    # Replace existing file
                    new_dir.children[existing_file_index] = file_copy
                else:
                    # Add as new file
                    new_dir.children.append(file_copy)
            elif isinstance(child, Directory):
                self._copy_directory(child, new_dir)

    def get_node(self, path: Path) -> Node | None:
        if not path: # Handles empty string path
            return None

        if path == "/":
            return self.root
        
        # Filters out empty strings from multiple slashes e.g. "/foo//bar" -> ["foo", "bar"]
        # or leading/trailing slashes for non-root paths e.g. "/foo/" -> ["foo"]
        parts = [part for part in path.split('/') if part]

        # If after stripping and splitting, parts is empty, but path wasn't just "/", it's invalid (e.g. "///")
        if not parts and path != "/":
             return None

        current_node = self.root
        for part in parts:
            if not isinstance(current_node, Directory):
                # Current segment is not a directory, so cannot traverse further.
                return None

            found_child_node = None
            for child in current_node.children:
                if child.name == part:
                    found_child_node = child
                    break
            
            if found_child_node is not None:
                current_node = found_child_node
            else:
                # Path component (part) not found in current_node's children.
                return None
        
        return current_node
    
    def create_node(self, full_path: str, node_instance: Node) -> Node | None:
        # node_instance is the File or Directory object to insert.
        # Its .name will be set based on the last component of full_path.
        # Its .parent will be set to the resolved parent directory from full_path.

        normalized_full_path = full_path.strip()
        if not normalized_full_path or normalized_full_path == "/":
            # Cannot create at root this way, or an invalid empty path.
            return None 

        path_parts = [p for p in normalized_full_path.split('/') if p]
        if not path_parts: # e.g. path was "///" or similar, resulting in no valid parts
            return None

        new_node_name = path_parts[-1]
        parent_path_segments = path_parts[:-1]

        # Traverse to find the parent directory
        parent_dir_node = self.root
        for segment_name in parent_path_segments:
            if not isinstance(parent_dir_node, Directory):
                # A segment of the parent path is a file, or path is malformed.
                return None

            found_next_dir_segment = None
            for child_node in parent_dir_node.children:
                if child_node.name == segment_name:
                    if isinstance(child_node, Directory):
                        found_next_dir_segment = child_node
                        break
                    else: 
                        # A segment of the parent path is a file.
                        return None 
            
            if found_next_dir_segment is not None:
                parent_dir_node = found_next_dir_segment
            else:
                # Intermediate directory in the parent path does not exist.
                return None
        
        # parent_dir_node is now the directory where the new node should be created.
        # Ensure it's actually a Directory (should be, due to logic above).
        if not isinstance(parent_dir_node, Directory):
             return None 

        # Check if a node with new_node_name already exists in the parent directory
        for existing_child in parent_dir_node.children:
            if existing_child.name == new_node_name:
                # Node with the same name already exists at the target path.
                return None

        # Configure the provided node_instance
        node_instance.name = new_node_name
        node_instance.parent = parent_dir_node
        
        # If the node_instance is a Directory, ensure its children list is initialized.
        # For a new directory, this list should typically be empty.
        # The caller should provide a Directory instance with children=[] if that's intended.
        if isinstance(node_instance, Directory):
            if node_instance.children is None: # Defensive check
                node_instance.children = []

        parent_dir_node.children.append(node_instance)
        return node_instance

    def create_file(self, path: str, contents: str = "") -> Node | None:
        file_node = File(path.split("/")[-1], None, contents)
        return self.create_node(path, file_node)
    
    def create_directory(self, path: str) -> Node | None:
        dir_node = Directory(path.split("/")[-1], None)
        return self.create_node(path, dir_node)

    def delete_node(self, path: str) -> bool:
        node = self.get_node(path)
        if node is None:
            return False
        node.parent.children = [child for child in node.parent.children if child.name != node.name]
        return True
