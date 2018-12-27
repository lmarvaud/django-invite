"""
test invite.join_and

Created by lmarvaud on 01/01/2019
"""
from unittest import TestCase

from invite.join_and import join_and


class TestJoinAnd(TestCase):
    """
    test invite.join_and function
    """
    def test_join_and_empty(self):
        """test invite.join_and function without names"""
        self.assertEqual(join_and([]), "")

    def test_join_and_one(self):
        """test invite.join_and function with one name"""
        self.assertEqual(join_and(["Pierre"]), "Pierre")

    def test_join_and_two(self):
        """test invite.join_and function with two names"""
        self.assertEqual(join_and(["Pierre", "Marie"]), "Pierre and Marie")

    def test_join_and_three(self):
        """test invite.join_and function with more than two names"""
        self.assertEqual(join_and(["Pierre", "Marie", "Jean"]), "Pierre, Marie and Jean")
        self.assertEqual(join_and(["Pierre", "Marie", "Jean", "Françoise"]),
                         "Pierre, Marie, Jean and Françoise")
