from helper import unittest, PillowTestCase

from PIL import Image
import os

base = os.path.join('Tests', 'images', 'bmp', 'g')

class TestBmpCropCrash(PillowTestCase):
    def _testone(self,f):
        print('testing %s for crop crash'%f)
        try:
            im = Image.open(os.path.join(base,f))
        except IOError: return
        im = im.crop((1,1,10,10))
        # should not crash
        im.load()

    def test_rgb(self):
        for f in os.listdir(base):
            self._testone(f)
        
