from sys import argv

from .main import main

if __name__ == "__main__":
    exit_code: int = main(argv[1:])
    exit(exit_code)
