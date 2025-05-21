import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest import mock
from contestImageGenerator import ContestImageGenerator

class TestContestImageGenerator(unittest.TestCase):
    def setUp(self):
        """Set up a ContestImageGenerator instance with sample parameters."""
        self.generator = ContestImageGenerator(
            contestId=2109,
            descText="TOP 5 - Overall",
            imageSelected=1,
            regex=r"^(2023|2024|2022).{9}$",
            overrideContestName=False,
            overrideText="CODEFORCES Div. 2 Round 1025"
        )

    @mock.patch('contestImageGenerator.requests.get') # so this basically edits what the actual requests.get thing does in the contestImageGenerator class
    def test_fetchDatabase(self, mock_get):
        """Test whether fetchDatabase correctly retrieves and parses API data."""
        # Mock API response
        mock_get.return_value.json.return_value = [
            {'name': 'Prakhar Bhandari', 'cfid': 'Darelife', 'bitsid': '2023A7PS0458G'}
        ]

        data = self.generator.fetchDatabase()

        # Check if data length and content are correct
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Prakhar Bhandari')

    def test_filterEntries(self):
        """Test whether filterEntries correctly filters entries by bitsid regex."""
        data = [
            {'name': 'Prakhar Bhandari', 'cfid': 'Darelife', 'bitsid': '2023A7PS0458G'},  #* Matches regex
            {'name': 'Bob', 'cfid': 'bob456', 'bitsid': '2010A7PS0001G'}       #! Does not match
        ]
        filtered = self.generator.filterEntries(data)

        # Expect only Alice to remain after filtering
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0][0], 'Prakhar Bhandari')

    def test_real_fetchDatabase(self):
        """Test real fetchDatabase call (integration test, hits the actual API)."""
        data = self.generator.fetchDatabase()
        self.assertIsInstance(data, list)
