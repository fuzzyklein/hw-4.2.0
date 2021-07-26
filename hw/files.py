"""@package files

Define a function `file` that returns an object that knows what type of file it
represents and acts accordingly when its methods are called.
"""

from functools import singledispatch, singledispatchmethod
import os
from os import listdir
from pathlib import Path, PosixPath, WindowsPath

from walkdir import filtered_walk

SRC_FILE_EXTS = ("py", "js", "c", 'htm', 'html', "css", "sql", "php",)
PICT_FILE_EXTS = ("png", "jpg", "gif",)
IMG_FILE_EXTS = ('jpg', 'jpeg', 'png', 'gif', 'tiff', 'psd', 'bmp',)
VEC_IMG_EXTS = ('svg', 'eps', 'pdf',)
MSDOC_FILE_EXTS = ('doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',)
OODOC_FILE_EXTS = ('odt', 'ods',)
TEXT_FILE_EXTS = ('txt',)

RUNNING_WINDOWS = os.name == 'nt'
SUPER_TYPE = WindowsPath if RUNNING_WINDOWS else PosixPath

class File(SUPER_TYPE):
    """Define a subclass for all the other file types."""
    def __init__(self, *args, **kwargs):
        """Initialize the `File` object."""
        SUPER_TYPE.__init__(*args, **kwargs)

    def glob(self, *args, **kwargs):
        """Only a `Directory` can be `glob`bed, so this function does nothing."""
        raise NotImplementedError("`glob` function only available to a Directory")

    #
    @singledispatchmethod
    def chmod(self, mode, *args, **kwargs):
        """Irrelevant on Windows because no such thing exists."""
        raise NotImplementedError("`chmod`: bad argument type")

    @chmod.register
    def _(self, mode: int, *args, **kwargs):
        return None if RUNNING_WINDOWS else super().chmod(mode)

    @chmod.register
    def _(self, mode: str, *args, **kwargs):
        # raise NotImplementedError("TODO: Parse a `str` to an `int` for `chmod`.")
        return self.chmod(int(mode))

    @singledispatchmethod
    def lchmod(self, mode, *args, **kwargs):
        raise NotImplementedError("`chmod`: bad argument type")

    @lchmod.register
    def _(self, mode: int, *args, **kwargs):
        return super().lchmod(mode)

    @lchmod.register
    def _(self, mode: str, *args, **kwargs):
        raise NotImplementedError("TODO: Parse a `str` to an `int` for `lchmod`.")

    def iterdir(self):
        raise NotImplementedError("`iterdir` function only available to a Directory")

    def mkdir(self, *args, **kwargs):
        raise NotImplementedError("`mkdir` function only available to a file that DoesNotExist")

    @property
    def owner(self):
#         print("Getting file owner...")
        return super().owner()

    @owner.setter
    def owner(self, user):
        run(f"chown {user} {self.name}")

    @property
    def group(self):
        return super().group()

    @group.setter
    def group(self, g):
        bash(f"chgrp {g} {self.name}")

    @property
    def parent(self):
        return file(super().parent)

    @property
    def parents(self):
        return [ file(p) for p in super().parents ]

    @property
    def mimetype(self):
        with file.Magic() as m:
            value = m.file(self.name)
        return value

class Directory(File):
    def glob(self, pattern, recursive=False):
        globber = Path.rglob if recursive else Path.glob
        return [file(p) for p in globber(self, pattern)]

    def iterdir(self):
        return (file(p) for p in Path.iterdir(self))

    def is_empty(self):
        return bool(listdir(self))

    def ls(self, follow=False):
        if self.is_empty():
            print(f"Directory {self} is empty.")
        else:
            print(f"Directory listing for {self}:")
            for w in filtered_walk(self, depth=0, followlinks=follow):
                print("Subdirectories:")
                columnize(w[1])
                print("Files:")
                columnize(w[2])
        return w

class AppFile(File):
    pass

class MediaFile(File):
    def play(self):
        pass

class AudioFile(MediaFile):
    pass

class FontFile(File):
    pass

class ImageFile(MediaFile):
    pass

class INodeFile(File):
    pass

class MessageFile(File):
    pass

class ModelFile(File):
    pass

class MultiPartFile(File):
    pass

class VideoFile(MediaFile):
    pass

class XContentFile(File):
    pass

class XEpocFile(File):
    pass

class Device(File):
    pass

class BlockDevice(File):
    pass

class CharDevice(File):
    pass

class FIFO(File):
    pass

class RegFile(File):
    pass

class TextFile(File):
    pass

class SourceFile(File):
    pass

class CSVFile(File):
    pass

class BinaryFile(File):
    pass

class PictFile(File):
    pass

class Mount(File):
    pass

class Socket(File):
    pass

class SymLink(File):
    pass

class DoesNotExist(File):
    def mkdir(self):
        return mkdir(self)

def home():
    return file(Path.home())

def cwd():
    return file(Path.cwd())

@singledispatch
def mkdir(p, *args, **kwargs):
    raise NotImplementedError("first arg to `mkdir` must be `str` or `Path`")

@mkdir.register
def _(p: str, *args, **kwargs):
    print("executing `mkdir(str)`")
    return mkdir(Path(p))

@mkdir.register
def _(p: Path, *args, **kwargs):
    print("executing `mkdir(Path)`")
    p.mkdir()
    return file(p)
