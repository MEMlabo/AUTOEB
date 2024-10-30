from argparse import ArgumentError
from sys import stderr

from .cui import CommandArguments
from .operation_manager import OperationManager


def main(args: list[str]) -> int:
    """メイン関数

    Args:
        args (list[str]): 引数

    Returns:
        int: Exit Code
    """
    if len(args) == 0:
        print("Arguments is not specified", file=stderr)
        CommandArguments.get_arg_parser().print_help()
        return 1
    arguments = CommandArguments(args)
    manager = OperationManager(arguments)

    try:
        manager.execute()
    except ArgumentError as e:
        print(e.message, file=stderr)
        return 1

    return 0
