from game.system.dialog import thinking_texts
from game.system.history import CommandHistory

class GameState:
    def __init__(self):
        self.thinking_text = thinking_texts[0]
        self.discovered_commands = {"ls", "pwd", "cd", "exit", "cat", "help", "clear", "man"}
        self.think_index = 0
        self.show_bulb = False

    def next_thinking_text(self):
        self.think_index += 1
        self.show_bulb = True
        if self.think_index < len(thinking_texts):
            self.thinking_text = thinking_texts[self.think_index]
        else:
            self.thinking_text = thinking_texts[-1]

    def get_thinking_text(self) -> str:
        return self.thinking_text

    def add_discovered_command(self, command: str):
        self.discovered_commands.add(command)

    def get_discovered_commands(self) -> set:
        return self.discovered_commands

    def update(self, history: CommandHistory):
        if self.think_index == 0:
            if history.has_run_man():
                self.next_thinking_text()
        elif self.think_index == 1:
            pass
        elif self.think_index == 2:
            pass
                
GAME_STATE_INSTANCE = GameState()