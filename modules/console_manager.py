RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE  = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"

RESET = "\033[0m"

JUMP_LINE = "\n"
def printf(message: str):
    print(
        JUMP_LINE +
        RESET +
        f"> {message}"
    )

def warning(message: str):
    print(
       YELLOW +
        F">> {message}" +
        RESET
    )


def success(message: str):
    print(
        GREEN +
        F">> {message}" +
        RESET
    )

def error(message: str):
    print(
        RED +
        F">>> {message}" +
        RESET
    )