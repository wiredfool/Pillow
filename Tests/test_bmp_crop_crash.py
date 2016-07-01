from helper import unittest, PillowTestCase

from PIL import Image
import os

base = os.path.join('Tests', 'images', 'bmp', 'g')

class TestBmpCropCrash(PillowTestCase):
    def _testone(self,f):
        print('testing %s for crop crash'%f)
        im = Image.open(os.path.join(base,f))
        im = im.crop((1,1,10,10))
        # should not crash
        im.load()

    def test_rgb(self):
        for f in ['rgb16.bmp', 'rgb24.bmp', 'rgb32.bmp']:
            self._testone(f)
        
