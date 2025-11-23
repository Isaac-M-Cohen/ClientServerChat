import sys
import select
import termios
import tty
import atexit

# Save original terminal settings
fd = sys.stdin.fileno()
orig_settings = termios.tcgetattr(fd)

# Put terminal into cbreak mode once
tty.setcbreak(fd)

# Make sure terminal is restored when program exits
def restore_terminal():
    termios.tcsetattr(fd, termios.TCSADRAIN, orig_settings)

atexit.register(restore_terminal)


def kbhit():
    """Return True if a key was pressed."""
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    return bool(dr)


def getch():
    """Read one character (no enter needed)."""
    ch = sys.stdin.read(1)
    return ch
