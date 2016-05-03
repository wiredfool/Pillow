from helper import unittest, PillowTestCase, hopper
from PIL import Image


class TestImagingCoreResize(PillowTestCase):
    # see https://github.com/python-pillow/Pillow/issues/1710
    def test_overflow(self):
        im = hopper('L')
        xsize = 0x100000008 // 4
        ysize = 1000  # unimportant
        try:
            # any resampling filter will do here
            im.im.resize((xsize, ysize), Image.LINEAR)
            self.fail("Resize should raise MemoryError on invalid xsize")
        except MemoryError:
            self.assertTrue(True, "Should raise MemoryError")

    def test_invalid_size(self):
        im = hopper()

        im.resize((100, 100))
        self.assertTrue(True, "Should not Crash")

        try:
            im.resize((-100, 100))
            self.fail("Resize should raise a value error on x negative size")
        except ValueError:
            self.assertTrue(True, "Should raise ValueError")

        try:
            im.resize((100, -100))
            self.fail("Resize should raise a value error on y negative size")
        except ValueError:
            self.assertTrue(True, "Should raise ValueError")


class CoreResampleConsistencyTest(PillowTestCase):

    def test_8u(self):
        im = Image.new('RGB', (512, 9), (0, 64, 255))
        im = im.resize((9, 512), Image.LANCZOS)
        r, g, b = im.split()

        for channel, color in [(r, 0), (g, 64), (b, 255)]:
            px = channel.load()
            for x in range(channel.size[0]):
                for y in range(channel.size[1]):
                    if px[x, y] != color:
                        message = "{} != {} for pixel {}".format(
                            px[x, y], color, (x, y))
                        self.assertEqual(px[x, y], color, message)


if __name__ == '__main__':
    unittest.main()
