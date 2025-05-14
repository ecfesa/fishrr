class Manual:
    """
    Armazena páginas do manual; cada página traz explicação básica e hint.
    """
    pages = {
        1: {
            "content": "BASIC COMMANDS\n--------------\nhelp: Show available commands\nfish: Start the fishing minigame\ntodo: Show tasks for the current island\nman <page>: Show manual page",
            "hint": "Try 'man 2' to learn about fishing."
        },
        2: {
            "content": "FISHING GUIDE\n------------\nFishing is the main activity on Fish Island. To fish:\n- Use the 'fish' command to start fishing\n- Press SPACE to cast your line\n- Press SPACE again when you get a bite\n- Collect 5 fish to complete the challenge",
            "hint": "The better your timing, the better your catch!"
        },
        3: {
            "content": "ISLAND NAVIGATION\n----------------\nThe game consists of several islands, each with unique challenges.\nTo navigate between islands, you need to:\n1. Complete the current island's tasks\n2. Earn the password to the next island\n3. Use the password to unlock new areas",
            "hint": "If you're stuck, check your 'todo' list for guidance."
        }
    }

    @classmethod
    def get_page(cls, num):
        return cls.pages.get(num, {"content": "Page not found.", "hint": "Try 'man 1' for basic commands."})