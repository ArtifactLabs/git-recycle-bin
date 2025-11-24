import os
import mimetypes
from itertools import takewhile

def nca_path(pathA, pathB):
    """ Get nearest common ancestor of two paths """

    # Get absolute paths. Inputs may be relative.
    components1 = os.path.abspath(pathA).split(os.sep)
    components2 = os.path.abspath(pathB).split(os.sep)

    # Use zip to iterate over pairs of components
    # Stop when components differ, thanks to the use of itertools.takewhile
    common_components = list(takewhile(lambda x: x[0]==x[1], zip(components1, components2)))

    # The common path is the joined common components
    common_path = os.sep.join([x[0] for x in common_components])
    return common_path


def rel_dir(pfrom, pto):
    """ Get relative path to `pto` from `pfrom` """
    abs_pfrom = os.path.abspath(pfrom)
    abs_pto = os.path.abspath(pto)
    return os.path.relpath(abs_pto, abs_pfrom)


def classify_path(binpath: str) -> str:
    """ Determine what the path is, a file or directory. If file, what file """
    if os.path.isfile(binpath): return mimetypes.guess_type(binpath)
    elif os.path.isdir(binpath): return "directory"
    elif os.path.islink(binpath): return "link"
    elif os.path.ismount(binpath): return "mount"
    else: return "unknown"
