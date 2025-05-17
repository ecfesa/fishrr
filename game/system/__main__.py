import sys
import os

from game.system.terminal import Terminal
from game.system.shell import Shell
from game.system.system import System

# Detect platform
IS_WINDOWS = os.name == 'nt'

if IS_WINDOWS:
    import msvcrt

    def clear():
        os.system('cls')

    def read_char():
        return msvcrt.getwch()
else:
    import tty
    import termios

    def clear():
        os.system('clear')
    def read_char():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

def print_terminal(terminal, char):
    clear() 
    for row in terminal.buffer:
        print(''.join(row))
    print(f"\nCursor at: ({terminal.cursor_pos.x}, {terminal.cursor_pos.y})")
    print(f"Last input: {char} ord: {ord(char)}")

if __name__ == '__main__':
    system = System()
    print("Type to write to the terminal. Press ESC to exit.")

    while True:
        char = read_char()
        if ord(char) == 27:  # ESC key
            break
        system.process_input(char)
        print_terminal(system.terminal, char)
