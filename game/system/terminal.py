from enum import Enum
type TerminalBuffer = list[list[str]]

class TerminalPosition:
    def __init__(self, init_x = 0, init_y = 0):
        self.x = init_x
        self.y = init_y

class Terminal:
    def __init__(self, size_x: int, size_y: int):
        self.size_x = size_x
        self.size_y = size_y
        self.buffer: TerminalBuffer = [[' ' for _ in range(size_x)] for _ in range(size_y)]
        self.next_buffer: TerminalBuffer = [[' ' for _ in range(size_x)] for _ in range(size_y)]
        self.cursor_pos = TerminalPosition()

        self.flush() # To ensure the cursor is visible on the initial buffer

    def flush(self):
        # Deep copy next_buffer to buffer to store the content
        self.buffer = [row[:] for row in self.next_buffer]
        # Then, draw the cursor on the (display) buffer
        if 0 <= self.cursor_pos.y < self.size_y and \
           0 <= self.cursor_pos.x < self.size_x:
            self.buffer[self.cursor_pos.y][self.cursor_pos.x] = '_'

    def set_char(self, char: str, x: int = -1, y: int = -1):
        if x == -1:
            x = self.cursor_pos.x
        if y == -1:
            y = self.cursor_pos.y

        if 0 <= y < self.size_y and 0 <= x < self.size_x:
            self.next_buffer[y][x] = char
    
    def shift_cursor(self, offset = 1):
        new_x_total = self.cursor_pos.x + offset
        new_y = self.cursor_pos.y + (new_x_total // self.size_x)
        new_x = new_x_total % self.size_x

        # Scroll if cursor goes out of vertical bounds
        while new_y >= self.size_y:
            # Remove first row
            self.next_buffer.pop(0)
            # Append new empty row at bottom
            self.next_buffer.append([' ' for _ in range(self.size_x)])
            new_y -= 1  # Keep cursor inside bounds

        self.cursor_pos.x = new_x
        self.cursor_pos.y = new_y

    def clear(self):
        self.next_buffer = [[' ' for _ in range(self.size_x)] for _ in range(self.size_y)]
        self.cursor_pos = TerminalPosition()
        self.flush() # To make the cleared screen and new cursor position visible

    def print(self, text: str):
        for char in text:
            if char == "\n":
                self.shift_cursor(self.size_x - self.cursor_pos.x)
            elif char == "\b":
                self.shift_cursor(-1)
                self.set_char(' ')
            else:
                self.set_char(char)
                self.shift_cursor(1)
        
        self.flush()

