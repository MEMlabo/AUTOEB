from .iohandler import TreeIOHandler
from .newick import NewickIOHandler

newick: TreeIOHandler = NewickIOHandler()
"""newickフォーマットのI/Oを扱います。
"""
