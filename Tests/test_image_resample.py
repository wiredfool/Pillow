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

    def make_case(self, mode, fill):
        im = Image.new(mode, (512, 9), fill)
        return (im.resize((9, 512), Image.LANCZOS), im.load()[0, 0])

    def run_case(self, case):
        channel, color = case
        px = channel.load()
        for x in range(channel.size[0]):
            for y in range(channel.size[1]):
                if px[x, y] != color:
                    message = "{} != {} for pixel {}".format(
                        px[x, y], color, (x, y))
                    self.assertEqual(px[x, y], color, message)

    def test_8u(self):
        im, color = self.make_case('RGB', (0, 64, 255))
        r, g, b = im.split()
        self.run_case((r, color[0]))
        self.run_case((g, color[1]))
        self.run_case((b, color[2]))
        self.run_case(self.make_case('L', 12))

    def test_32i(self):
        self.run_case(self.make_case('I', 12))
        self.run_case(self.make_case('I', 0x7fffffff))
        self.run_case(self.make_case('I', -12))
        self.run_case(self.make_case('I', -1 << 31))

    def test_32f(self):
        self.run_case(self.make_case('F', 1))
        self.run_case(self.make_case('F', 3.40282306074e+38))
        self.run_case(self.make_case('F', 1.175494e-38))
        self.run_case(self.make_case('F', 1.192093e-07))


if __name__ == '__main__':
    unittest.main()
