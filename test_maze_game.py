import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import maze_game


class MazeGameImportTests(unittest.TestCase):
    def test_module_imports(self):
        self.assertTrue(hasattr(maze_game, "Game"))

    def test_answer_checker_normalizes_input(self):
        self.assertTrue(maze_game.check_answer("  MOUNTAIN  ", "mountain"))


if __name__ == "__main__":
    unittest.main()