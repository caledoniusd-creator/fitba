

from os import system, name


def clear_console():
    """
    Clears the console screen (OS agnostic).
    """
    system("cls" if name == "nt" else "clear")