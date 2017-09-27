from helper import unittest, PillowTestCase, hopper

from PIL import Image, ImageFile

from io import BytesIO

try:
    from PIL import _webp
except ImportError:
    # Skip in setUp()
    pass


class TestFileWebp(PillowTestCase):

    def setUp(self):
        try:
            from PIL import _webp
        except ImportError:
            self.skipTest('WebP support not installed')

    def test_version(self):
        _webp.WebPDecoderVersion()
        _webp.WebPDecoderBuggyAlpha()

    def test_read_rgb(self):

        file_path = "Tests/images/hopper.webp"
        image = Image.open(file_path)

        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        # generated with:
        # dwebp -ppm ../../Tests/images/hopper.webp -o hopper_webp_bits.ppm
        target = Image.open('Tests/images/hopper_webp_bits.ppm')
        self.assert_image_similar(image, target, 20.0)

    def test_write_rgb(self):
        """
        Can we write a RGB mode file to webp without error.
        Does it have the bits we expect?
        """

        temp_file = self.tempfile("temp.webp")

        hopper("RGB").save(temp_file)

        image = Image.open(temp_file)
        image.load()

        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, (128, 128))
        self.assertEqual(image.format, "WEBP")
        image.load()
        image.getdata()

        # If we're using the exact same version of WebP, this test should pass.
        # but it doesn't if the WebP is generated on Ubuntu and tested on
        # Fedora.

        # generated with: dwebp -ppm temp.webp -o hopper_webp_write.ppm
        # target = Image.open('Tests/images/hopper_webp_write.ppm')
        # self.assert_image_equal(image, target)

        # This test asserts that the images are similar. If the average pixel
        # difference between the two images is less than the epsilon value,
        # then we're going to accept that it's a reasonable lossy version of
        # the image. The old lena images for WebP are showing ~16 on
        # Ubuntu, the jpegs are showing ~18.
        target = hopper("RGB")
        self.assert_image_similar(image, target, 12)

    def test_write_unsupported_mode(self):
        temp_file = self.tempfile("temp.webp")

        im = hopper("L")
        self.assertRaises(IOError, im.save, temp_file)

    def test_WebPEncode_with_invalid_args(self):
        self.assertRaises(TypeError, _webp.WebPEncode)

    def test_WebPDecode_with_invalid_args(self):
        self.assertRaises(TypeError, _webp.WebPDecode)

    def test_truncated(self):
        assert False == ImageFile.LOAD_TRUNCATED_IMAGES
        with open('Tests/images/flower.webp', 'rb') as fp:
            full_data = fp.read()
        # Truncate in the middle (VP8 chunk).
        half_data = full_data[:len(full_data)//2]
        im = Image.open(BytesIO(half_data))
        self.assertRaises(IOError, im.load)
        im = Image.open(BytesIO(half_data))
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            im.load()
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False
        original = Image.open(BytesIO(full_data))
        width, height = original.size
        # Check we decoded at least part of the image (top).
        top_area = (0, 0, width-1, 31)
        self.assert_image_equal(im.crop(top_area), original.crop(top_area))
        # Bottom should be blank.
        bottom_area = (width-33, height-33, width-1, height-1)
        self.assert_image_equal(im.crop(bottom_area), Image.new(original.mode, (32, 32)))
        # Truncate at the end (EXIF chunk).
        most_data = full_data[:-4*1024]
        self.assertRaises(IOError, Image.open, BytesIO(most_data))
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            im = Image.open(BytesIO(most_data))
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False
        im.load()
        # Check we decoded the whole image.
        self.assert_image_equal(im, original)

    def test_info_compression(self):
        for name, compression in (
            ('flower2'           , 'lossy'),
            ('flower'            , 'lossy'),
            ('hopper'            , 'lossy'),
            ('lossless-no-vp8x'  , 'lossless'),
            ('lossless-with-vp8x', 'lossless'),
            ('transparent'       , 'lossy'),
        ):
            image = Image.open('Tests/images/%s.webp' % name)
            self.assertEqual(image.info['compression'], compression)


if __name__ == '__main__':
    unittest.main()
