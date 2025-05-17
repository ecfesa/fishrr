class Path:
    def __init__(self, path: str, cwd: str):
        self.trailing_slash = path.endswith('/')
        self.path = self._resolve_path(path, cwd)

    # Move up one directory
    def up(self):
        if self.path == "/":
            return self  # Root directory has no parent
        
        parent_path = self.path.rsplit('/', 1)[0]
        if not parent_path:  # Handle case where we're one level below root
            parent_path = "/"
            
        result = Path(parent_path, "/")  # Create a new Path with the parent path
        return result

    def _resolve_path(self, path_str: str, cwd: str) -> str:
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
            if cwd == '/':
                full_path = '/' + path_str # Avoids '//file'
            else:
                full_path = cwd + '/' + path_str # e.g., "/home" + "/" + "file"

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

    def __str__(self):
        return self.path
