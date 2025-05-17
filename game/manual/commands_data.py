from typing import Dict

def load_commands() -> Dict[str, Dict[str, str]]:
    """Load all commands, their descriptions, and examples."""
    commands = {
        "ls": {
            "desc": "list files/directories where you are.",
            "example": "ls"
        },
        "pwd": {
            "desc": "prints current directory",
            "example": "pwd"
        },
        "cd": {
            "desc": "changes the current directory. Use '..' to go up a level",
            "example": "'cd islands' 'cd ..' 'cd'"
        },
        "cp": {
            "desc": "copies a file/directory. Has restrictions on what can be copied",
            "example": "'cp file.txt destination' 'cp folder destination'"
        },
        "exit": {
            "desc": "closes the game",
            "example": "exit"
        },
        "cat": {
            "desc": "prints out a file. Shows the contents of things in the game",
            "example": "cat file.txt"
        },
        "rm": {
            "desc": "deletes a file/directory ('drops' the file into the water)",
            "example": "'rm file.txt' 'rm directory'"
        },
        "clear": {
            "desc": "wipes the CLI text",
            "example": "clear"
        },
        "egg": {
            "desc": "...",
            "example": "???"
        },
        "fish lore": {
            "desc": "fish lore...",
            "example": "fish lore"
        },
        "fish": {
            "desc": "fish for items. You need to be in a fish pond.",
            "example": "fish"
        },
        "flee": {
            "desc": "flee the scene. You need to have your boat ready!",
            "example": "flee"
        }
    }
    return commands 