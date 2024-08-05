import os
from unittest import TestLoader, TestSuite
from unittest.runner import TextTestRunner

if __name__ == "__main__":
    dir: str = os.path.dirname(__file__)

    # モジュール内の大文字アルファベットで始まる.pyファイルのテストを実行
    test: TestSuite = TestLoader().discover(dir, "[a-z]*.py")
    TextTestRunner().run(test)
