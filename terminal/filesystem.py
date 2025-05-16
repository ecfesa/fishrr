from enum import Enum

class Node:
    def __init__(self, name: str, parent):
        self.name: str = name
        self.parent: Node | None = parent

class Directory(Node):
    def __init__(self, name: str, parent: Node | None, children: list[Node] | None = None):
        super().__init__(name, parent)
        self.children: list[Node] = children if children is not None else []

class File(Node):
    def __init__(self, name: str, parent: Node | None, contents: str):
        super().__init__(name, parent)
        self.contents = contents

class FileSystem:
    def __init__(self):
        self.root = Directory("/", None, [])

    def get_node(self, path: str) -> Node | None:
        normalized_path = path.strip()
        if not normalized_path: # Handles empty string path
            return None

        if normalized_path == "/":
            return self.root
        
        # Filters out empty strings from multiple slashes e.g. "/foo//bar" -> ["foo", "bar"]
        # or leading/trailing slashes for non-root paths e.g. "/foo/" -> ["foo"]
        parts = [part for part in normalized_path.split('/') if part]
        
        # If after stripping and splitting, parts is empty, but path wasn't just "/", it's invalid (e.g. "///")
        if not parts and normalized_path != "/":
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
