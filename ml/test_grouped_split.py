import unittest
from pathlib import Path
from unittest.mock import patch

from ml.grouped_split import build_groups, split_groups


class GroupedSplitTests(unittest.TestCase):
    def test_transitive_links_and_singleton(self):
        a, b, c, d = map(Path, ('a', 'b', 'c', 'd'))
        self.assertEqual(build_groups([d, c, b, a], [(a, b), (b, c)]), [[a, b, c], [d]])

    def test_unknown_pair_rejected(self):
        with self.assertRaises(ValueError):
            build_groups([Path('a')], [(Path('a'), Path('missing'))])

    def test_indivisible_groups_and_reproducibility(self):
        groups = [[Path(f'{i}-{j}') for j in range(2)] for i in range(30)]
        with patch('ml.grouped_split.get_image_classes', return_value=set(range(10))):
            splits = split_groups(groups)
            self.assertEqual(splits, split_groups(list(reversed(groups))))
        assignment = {p: name for name, paths in splits.items() for p in paths}
        self.assertEqual(len(assignment), 60)
        for group in groups:
            self.assertEqual(len({assignment[p] for p in group}), 1)
        self.assertTrue(all(splits.values()))

    def test_insufficient_independent_groups_rejected(self):
        with patch('ml.grouped_split.get_image_classes', return_value=set(range(10))):
            with self.assertRaises(ValueError):
                split_groups([[Path('a'), Path('b'), Path('c')]])


if __name__ == '__main__':
    unittest.main()
