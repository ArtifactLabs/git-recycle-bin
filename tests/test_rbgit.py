import pytest

from rbgit import RbGit

class DummyRbGit:
    def cmd(self, *args, **kwargs):
        if args[:2] == ("ls-tree", "-lr"):
            return (
                "100644 blob aaaaaa 123\tfile1\n"
                "100644 blob bbbbbb 456\tfile2\n"
            )
        raise RuntimeError("Unexpected command")

def test_tree_size_sum():
    dummy = DummyRbGit()
    size = RbGit.tree_size(dummy, "HEAD")
    assert size == 579
