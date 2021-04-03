from unittest import TestCase, main
from unittest.mock import patch

from runcast import prompt


class TestPrompt(TestCase):
    @patch('runcast.input', return_value='*')
    def test_select_all(self, input):
        self.assertEqual(prompt(9), list(range(9)))

    @patch('runcast.input', return_value='')
    def test_select_none(self, input):
        self.assertEqual(prompt(9), [])

    @patch('runcast.input', return_value='3')
    def test_select_one(self, input):
        self.assertEqual(prompt(9), [2])

    @patch('runcast.input', return_value='1 5')
    def test_select_two(self, input):
        self.assertEqual(prompt(9), [0, 4])

    @patch('runcast.input', return_value='1-5')
    def test_select_range(self, input):
        self.assertEqual(prompt(9), [0, 1, 2, 3, 4])

    @patch('runcast.input', return_value='1 3-5 4,10')
    def test_complex_selection(self, input):
        self.assertEqual(prompt(9), [0, 2, 3, 4, 9])


if __name__ == '__main__':
    main()
