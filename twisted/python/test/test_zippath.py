# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases covering L{twisted.python.zippath}.
"""

from __future__ import print_function, division, absolute_import

import os, zipfile
import shutil

from twisted.test.test_paths import AbstractFilePathTests
from twisted.python.zippath import ZipArchive
from twisted.python.filepath import FilePath


def _zipit(dirname, zfname):
    """
    Create a zipfile on zfname, containing the contents of dirname'
    """
    z = FilePath(zfname).asTextMode().open("w")
    shutil.make_archive(z.name, "zip", dirname)


def zipit(dirname, zfname):
    """
    Create a zipfile on zfname, containing the contents of dirname'
    """

    def path_wrapper(p, mode=None):
        # need to avoid fs specific filepath encoding rules
        if mode:
            with FilePath(p).asTextMode().open(mode) as f:
                return f.name
        else:
            with FilePath(p).asTextMode().open() as f:
                return f.name

    file_obj = path_wrapper(zfname, "w")
    zf = zipfile.ZipFile(file_obj, "w")
    for root, ignored, files, in os.walk(dirname):
        for fname in files:
            fspath = path_wrapper(os.path.join(root, fname))
            arcpath = fspath[len(dirname)+1:]
            zf.write(fspath, arcpath)
    zf.close()



class ZipFilePathTests(AbstractFilePathTests):
    """
    Test various L{ZipPath} path manipulations as well as reprs for L{ZipPath}
    and L{ZipArchive}.
    """
    def setUp(self):
        AbstractFilePathTests.setUp(self)
        zipit(self.cmn, self.cmn + b'.zip')
        self.path = ZipArchive(self.cmn + b'.zip')
        self.root = self.path
        self.all = [x.replace(self.cmn, self.cmn + b'.zip') for x in self.all]


    def test_zipPathRepr(self):
        """
        Make sure that invoking ZipPath's repr prints the correct class name
        and an absolute path to the zip file.
        """
        child = self.path.child("foo")
        pathRepr = "ZipPath(%r)" % (
            os.path.abspath(self.cmn + b".zip" + os.sep + 'foo'),)

        # Check for an absolute path
        self.assertEqual(repr(child), pathRepr)

        # Create a path to the file rooted in the current working directory
        relativeCommon = self.cmn.replace(os.getcwd() + os.sep, "", 1) + ".zip"
        relpath = ZipArchive(relativeCommon)
        child = relpath.child("foo")

        # Check using a path without the cwd prepended
        self.assertEqual(repr(child), pathRepr)


    def test_zipPathReprParentDirSegment(self):
        """
        The repr of a ZipPath with C{".."} in the internal part of its path
        includes the C{".."} rather than applying the usual parent directory
        meaning.
        """
        child = self.path.child("foo").child("..").child("bar")
        pathRepr = "ZipPath(%r)" % (
            self.cmn + ".zip" + os.sep.join(["", "foo", "..", "bar"]))
        self.assertEqual(repr(child), pathRepr)


    def test_zipPathReprEscaping(self):
        """
        Bytes in the ZipPath path which have special meaning in Python
        string literals are escaped in the ZipPath repr.
        """
        child = self.path.child("'")
        path = self.cmn + ".zip" + os.sep.join(["", "'"])
        pathRepr = "ZipPath('%s')" % (path.encode('string-escape'),)
        self.assertEqual(repr(child), pathRepr)


    def test_zipArchiveRepr(self):
        """
        Make sure that invoking ZipArchive's repr prints the correct class
        name and an absolute path to the zip file.
        """
        pathRepr = 'ZipArchive(%r)' % (os.path.abspath(self.cmn + '.zip'),)

        # Check for an absolute path
        self.assertEqual(repr(self.path), pathRepr)

        # Create a path to the file rooted in the current working directory
        relativeCommon = self.cmn.replace(os.getcwd() + os.sep, "", 1) + ".zip"
        relpath = ZipArchive(relativeCommon)

        # Check using a path without the cwd prepended
        self.assertEqual(repr(relpath), pathRepr)


    def test_zipFileIsADir(self):
        self.assertTrue(self.path.isdir())
