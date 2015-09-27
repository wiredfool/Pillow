from helper import unittest, PillowTestCase, hopper

from PIL import ImageOps, Image


class TestImageOps(PillowTestCase):

    class Deformer(object):
        def getmesh(self, im):
            x, y = im.size
            return [((0, 0, x, y), (0, 0, x, 0, x, y, y, 0))]

    deformer = Deformer()

    def test_sanity(self):

        ImageOps.autocontrast(hopper("L"))
        ImageOps.autocontrast(hopper("RGB"))

        ImageOps.autocontrast(hopper("L"), cutoff=10)
        ImageOps.autocontrast(hopper("L"), ignore=[0, 255])

        ImageOps.autocontrast_preserve(hopper("L"))
        ImageOps.autocontrast_preserve(hopper("RGB"))

        ImageOps.autocontrast_preserve(hopper("L"), cutoff=10)
        ImageOps.autocontrast_preserve(hopper("L"), ignore=[0, 255])

        ImageOps.colorize(hopper("L"), (0, 0, 0), (255, 255, 255))
        ImageOps.colorize(hopper("L"), "black", "white")

        ImageOps.crop(hopper("L"), 1)
        ImageOps.crop(hopper("RGB"), 1)

        ImageOps.deform(hopper("L"), self.deformer)
        ImageOps.deform(hopper("RGB"), self.deformer)

        ImageOps.equalize(hopper("L"))
        ImageOps.equalize(hopper("RGB"))

        ImageOps.expand(hopper("L"), 1)
        ImageOps.expand(hopper("RGB"), 1)
        ImageOps.expand(hopper("L"), 2, "blue")
        ImageOps.expand(hopper("RGB"), 2, "blue")

        ImageOps.fit(hopper("L"), (128, 128))
        ImageOps.fit(hopper("RGB"), (128, 128))

        ImageOps.flip(hopper("L"))
        ImageOps.flip(hopper("RGB"))

        ImageOps.grayscale(hopper("L"))
        ImageOps.grayscale(hopper("RGB"))

        ImageOps.invert(hopper("L"))
        ImageOps.invert(hopper("RGB"))

        ImageOps.mirror(hopper("L"))
        ImageOps.mirror(hopper("RGB"))

        ImageOps.posterize(hopper("L"), 4)
        ImageOps.posterize(hopper("RGB"), 4)

        ImageOps.solarize(hopper("L"))
        ImageOps.solarize(hopper("RGB"))

    def test_1pxfit(self):
        # Division by zero in equalize if image is 1 pixel high
        newimg = ImageOps.fit(hopper("RGB").resize((1, 1)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

        newimg = ImageOps.fit(hopper("RGB").resize((1, 100)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

        newimg = ImageOps.fit(hopper("RGB").resize((100, 1)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

    def test_pil163(self):
        # Division by zero in equalize if < 255 pixels in image (@PIL163)

        i = hopper("RGB").resize((15, 16))

        ImageOps.equalize(i.convert("L"))
        ImageOps.equalize(i.convert("P"))
        ImageOps.equalize(i.convert("RGB"))

    def test_autocontrast_preserve_gradient(self):
        from PIL import _imaging as core
        gradient = Image.Image()._new(core.linear_gradient('L'))

        # test with a grayscale gradient that extends to 0,255.
        # Should be a noop.
        out = ImageOps.autocontrast_preserve(gradient, 0)
        self.assert_image_equal(gradient, out)

        # cutoff the top and bottom
        # autocontrast should make the first and list histogram entries equal
        # and should be 10% of the image pixels (+-, because integers)
        out = ImageOps.autocontrast_preserve(gradient, 10)
        hist = out.histogram()
        self.assertEqual(hist[0], hist[-1])
        self.assertEqual(hist[-1], 256*round(256*0.10))

        # in rgb
        img = gradient.convert('RGB')
        out = ImageOps.autocontrast_preserve(img, 0)
        self.assert_image_equal(img, out)

        # Gradient one channel
        img = Image.merge('RGB', [gradient,
                                  Image.new('L', (256,256), 127),
                                  Image.new('L', (256,256), 127)])
        out = ImageOps.autocontrast_preserve(img, 0)
        self.assert_image_equal(img, out)



    def test_autocontrast_preserve_onecolor(self):
        def _test_one_color(color):
            img = Image.new('RGB', (10,10), color)

            # single color images shouldn't change
            out = ImageOps.autocontrast_preserve(img, 0)
            #remove when production
            print (img.getpixel((0,0)),out.getpixel((0,0)))
            self.assert_image_equal(img, out) # single color, no cutoff

            # even if there is a cutoff
            out = ImageOps.autocontrast_preserve(img, 10) # single color 10 cutoff
            self.assert_image_equal(img, out)

        #succeeding
        _test_one_color((255,255,255))
        _test_one_color((127,255,0))
        #failing
        _test_one_color((127,127,127))
        _test_one_color((0,0,0))        
        

if __name__ == '__main__':
    unittest.main()

# End of file
