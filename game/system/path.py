class FSPath:
    def __init__(self, path_str: str):
        if not isinstance(path_str, str):
            raise TypeError("path_str must be a string")
        self.raw_path = path_str
        self.components = self._parse(path_str)

    def _parse(self, path_str: str) -> list[str]:
        # Normalize: remove trailing slashes unless it's the root "/"
        normalized_path = path_str.rstrip('/')
        if not normalized_path and path_str.startswith('/'): # Handles root "/"
            return [] 
        
        # Split and filter empty components that might arise from multiple slashes
        return [p for p in normalized_path.lstrip('/').split('/') if p]

    def is_root(self) -> bool:
        return not self.components

    def parent(self) -> 'FSPath':
        if self.is_root():
            return self  # Parent of root is root
        
        parent_path_str = self.raw_path.rstrip('/')
        if not self.components: # Should be caught by is_root, but defensive
             return FSPath("/")

        # Find the last slash before the last component
        last_slash_idx = parent_path_str.rfind('/')
        if last_slash_idx == -1: # No slashes, e.g. "file.txt"
            if self.raw_path.startswith("/"): # e.g. "/file.txt"
                 return FSPath("/")
            else: # relative path, parent is effectively "." which we'll treat as root for simplicity here
                 return FSPath("/") # Or handle relative paths differently if needed
        elif last_slash_idx == 0: # e.g. "/foo" -> parent is "/"
            return FSPath("/")
        
        return FSPath(parent_path_str[:last_slash_idx] or "/")


    def name(self) -> str:
        if self.is_root():
            return ""  # Root has no name in this context or could be "/"
        return self.components[-1]

    def __str__(self) -> str:
        return "/" + "/".join(self.components) if self.raw_path.startswith('/') or self.is_root() else "/".join(self.components)
    
    def __repr__(self) -> str:
        return f"FSPath('{self.__str__()}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, FSPath):
            return self.components == other.components and self.is_absolute() == other.is_absolute()
        if isinstance(other, str):
            return str(self) == other
        return False
        
    def is_absolute(self) -> bool:
        return self.raw_path.startswith('/')
