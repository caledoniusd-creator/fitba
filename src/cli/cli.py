from os import system, name


# UI Constants
line_length = 80
max_lines = 25
seperator, blank_line = "=" * line_length, " " * line_length


def clear_console():
    """
    Clears the console screen (OS agnostic).
    """
    system("cls" if name == "nt" else "clear")
