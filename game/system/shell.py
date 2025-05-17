from game.system.terminal import Terminal
from enum import Enum
import random
from game.state import GAME_STATE_INSTANCE
from game.system.history import CommandHistory

class ShellMode(Enum):
    DIRECT = 1
    AUTO = 2

class Shell:
    def __init__(self, terminal: Terminal):
        self.terminal = terminal
        self.cwd = "/"
        self.mode = ShellMode.DIRECT
        self.cmd = ""
        self.cmds = {}
        self.auto_text = ""
        self.history = CommandHistory()
        self.print_shell_prompt()

    def backspace(self):
        if len(self.cmd) > 0:
            self.cmd = self.cmd[:-1]
            self.terminal.print('\b')
        
    def print_shell_prompt(self):
        self.terminal.print(f"fisher@pc {self.cwd} > ")

    def add_auto_text(self, text: str):
        self.auto_text += text
        self.mode = ShellMode.AUTO

    def _process_input_auto(self, char: str):
        if not self.auto_text:
            self.mode = ShellMode.DIRECT
            self._process_input_direct(char)
            return

        # Stops auto-writing for the user to confirm the command
        if self.auto_text[0] == '\r':
            if char == '\r':
                self.auto_text = self.auto_text[1:]
                self.execute_cmd()
                return
            else:
                return


        # Get each command (if any) from auto_text
        commands = self.auto_text.split('\r')

        # Determine the maximum number of characters to attempt to process from auto_text in this step
        max_chunk_size = random.randint(1, 4)
        
        # Take a chunk from auto_text, up to max_chunk_size
        # Ensure we don't take more than what's available
        actual_chunk_size = min(max_chunk_size, len(commands[0]))
        chunk = commands[0][:actual_chunk_size]

        # Print the chunk
        self.terminal.print(chunk)
        self.cmd += chunk

        # Remove the chunk from auto_text
        self.auto_text = self.auto_text[actual_chunk_size:]

        # If auto_text is empty, switch to DIRECT mode
        if not self.auto_text:
            self.mode = ShellMode.DIRECT


    def _process_input_direct(self, char: str):
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

    def process_input(self, char: str):
        if self.mode == ShellMode.DIRECT:
            self._process_input_direct(char)
        elif self.mode == ShellMode.AUTO:
            self._process_input_auto(char)
    def clear(self):
        self.cmd = ""
        self.terminal.clear()
        self.print_shell_prompt()

    def execute_cmd(self):
        self.cmd = self.cmd.strip()

        if self.cmd == "" or self.cmd[0] == "#":
            self.terminal.print("\n")
            self.print_shell_prompt()
            self.cmd = ""
            return


        bin = self.cmd.split(" ")[0]
        args = self.cmd.split(" ")[1:]

        self.history.add(bin, args, self.cwd)

        self.terminal.print("\n")
        if bin == 'clear':
            self.terminal.clear()
        elif bin in self.cmds.keys():
            self.cmds[bin](*args)
        else:
            self.terminal.print(f"Unknown command: {bin}\n")

        self.cmd = ""
        self.print_shell_prompt()

        GAME_STATE_INSTANCE.update(self.history)
    
    def register_cmd(self, cmd: str, func):
        self.cmds[cmd] = func
