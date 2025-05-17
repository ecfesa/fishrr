from typing import Dict

def load_commands() -> Dict[str, Dict[str, str]]:
    """Load all commands, their descriptions, and examples."""
    commands = {
        "ls": {
            "desc": "list files/directories in cwd. Shows disk usage for each file",
            "example": "ls\nls -la\nls /home/user"
        },
        "pwd": {
            "desc": "prints current directory",
            "example": "pwd"
        },
        "tree": {
            "desc": "shows file tree. Supposed to show everything available",
            "example": "tree\ntree -L 2"
        },
        "cd": {
            "desc": "changes the current directory, supports passworded folders",
            "example": "cd /path/to/dir\ncd ..\ncd ~"
        },
        "cp": {
            "desc": "copies a file/directory. Has restrictions on what can be copied",
            "example": "cp file.txt destination/\ncp -r folder/ destination/"
        },
        "exit": {
            "desc": "closes the game",
            "example": "exit"
        },
        "cat": {
            "desc": "prints out a file. Shows the contents of things in the game",
            "example": "cat file.txt\ncat -n file.txt"
        },
        "help": {
            "desc": "displays a help prompt with simple useful commands",
            "example": "help\nhelp command"
        },
        "rm": {
            "desc": "deletes a file/directory ('drops' the file into the water)",
            "example": "rm file.txt\nrm -rf directory/"
        },
        "reboot": {
            "desc": "resets the game",
            "example": "reboot"
        },
        "clear": {
            "desc": "wipes the CLI text",
            "example": "clear"
        },
        "egg": {
            "desc": "...",
            "example": "???"
        },
        "ps": {
            "desc": "lists running processes",
            "example": "ps\nps aux"
        },
        "kill": {
            "desc": "kills a process",
            "example": "kill 1234\nkill -9 5678"
        },
        "df": {
            "desc": "shows current disk usage",
            "example": "df\ndf -h"
        },
        "fish lore": {
            "desc": "fish lore...",
            "example": "fish lore"
        }
    }
    return commands 