class CommandHistory:
    def __init__(self):
        self.history = []

    def add(self, bin: str, args: list, cwd: str):
        self.history.append((bin, args, cwd))

    def has_run_man(self):
        for cmd in self.history:
            if cmd[0] == 'man':
                return True
        return False