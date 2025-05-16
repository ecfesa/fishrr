from terminal import Terminal
from enum import Enum

class ShellMode(Enum):
    DIRECT = 1

class Shell:
    def __init__(self, terminal: Terminal):
        self.terminal = terminal
        self.cwd = "/"
        self.mode = ShellMode.DIRECT
        self.cmd = ""
        self.cmds = {}
        self.print_shell_prompt()

    def backspace(self):
        if len(self.cmd) > 0:
            self.cmd = self.cmd[:-1]
            self.terminal.print('\b')
        
    def print_shell_prompt(self):
        self.terminal.print(f"fisher@pc {self.cwd} > ")

    def process_input(self, char: str):
        if self.mode == ShellMode.DIRECT:
            if char == "\r": # Enter
                self.execute_cmd()
            elif ord(char) == 3: # Ctrl+C
                self.cmd = ""
                self.terminal.print("\n")
                self.print_shell_prompt()
            elif ord(char) == 127 or ord(char) == 8 or ord(char) == '\b': # Backspace
                self.backspace()
            else:
                self.cmd += char
                self.terminal.print(char)

    def execute_cmd(self):
        if self.cmd == "":
            self.terminal.print("\n")
            self.print_shell_prompt()
            return

        bin = self.cmd.split(" ")[0]
        args = self.cmd.split(" ")[1:]
        self.terminal.print("\n")
        if bin == 'clear':
            self.terminal.clear()
        elif bin in self.cmds.keys():
            self.cmds[bin](*args)
        else:
            self.terminal.print(f"Unknown command: {self.cmd}\n")

        self.cmd = ""
        self.print_shell_prompt()
    
    def register_cmd(self, cmd: str, func):
        self.cmds[cmd] = func
