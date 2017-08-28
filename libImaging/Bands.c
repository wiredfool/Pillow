/*
 * The Python Imaging Library
 * $Id$
 *
 * stuff to extract and paste back individual bands
 *
 * history:
 * 1996-03-20 fl   Created
 * 1997-08-27 fl   Fixed putband for single band targets.
 * 2003-09-26 fl   Fixed getband/putband for 2-band images (LA, PA).
 *
 * Copyright (c) 1997-2003 by Secret Labs AB.
 * Copyright (c) 1996-1997 by Fredrik Lundh.
 *
 * See the README file for details on usage and redistribution.
 */


#include "Imaging.h"


#define CLIP(x) ((x) <= 0 ? 0 : (x) < 256 ? (x) : 255)


#ifdef WORDS_BIGENDIAN
    #define MAKE_UINT32(u0, u1, u2, u3) (u3 | (u2<<8)  | (u1<<16)  | (u0<<24))
#else
    #define MAKE_UINT32(u0, u1, u2, u3) (u0 | (u1<<8)  | (u2<<16)  | (u3<<24))
#endif


Imaging
ImagingGetBand(Imaging imIn, int band)
{
    Imaging imOut;
    int x, y;

    /* Check arguments */
    if (!imIn || imIn->type != IMAGING_TYPE_UINT8)
        return (Imaging) ImagingError_ModeError();

    if (band < 0 || band >= imIn->bands)
        return (Imaging) ImagingError_ValueError("band index out of range");

    /* Shortcuts */
    if (imIn->bands == 1)
        return ImagingCopy(imIn);

    /* Special case for LXXA etc */
    if (imIn->bands == 2 && band == 1)
        band = 3;

    imOut = ImagingNewDirty("L", imIn->xsize, imIn->ysize);
    if (!imOut)
        return NULL;

    /* Extract band from image */
    for (y = 0; y < imIn->ysize; y++) {
        UINT8* in = (UINT8*) imIn->image[y] + band;
        UINT8* out = imOut->image8[y];
        x = 0;
        for (; x < imIn->xsize - 3; x += 4) {
            *((UINT32*) (out + x)) = MAKE_UINT32(in[0], in[4], in[8], in[12]);
            in += 16;
        }
        for (; x < imIn->xsize; x++) {
            out[x] = *in;
            in += 4;
        }
    }

    return imOut;
}


int
ImagingSplit(Imaging imIn, Imaging bands[4])
{
    int i, j, x, y;

    /* Check arguments */
    if (!imIn || imIn->type != IMAGING_TYPE_UINT8) {
        (Imaging) ImagingError_ModeError();
        return 0;
    }

    /* Shortcuts */
    if (imIn->bands == 1) {
        bands[0] = ImagingCopy(imIn);
        return imIn->bands;
    }

    for (i = 0; i < imIn->bands; i++) {
        bands[i] = ImagingNew("L", imIn->xsize, imIn->ysize);
        if ( ! bands[i]) {
            for (j = 0; j < i; ++j) {
                ImagingDelete(bands[j]);
            }
            return 0;
        }
    }

    /* Extract bands from image */
    if (imIn->bands == 2) {
        for (y = 0; y < imIn->ysize; y++) {
            UINT8* in = (UINT8*) imIn->image[y];
            UINT8* out0 = bands[0]->image8[y];
            UINT8* out1 = bands[1]->image8[y];
            x = 0;
            for (; x < imIn->xsize - 3; x += 4) {
                *((UINT32*) (out0 + x)) = MAKE_UINT32(in[0], in[4], in[8], in[12]);
                *((UINT32*) (out1 + x)) = MAKE_UINT32(in[0+3], in[4+3], in[8+3], in[12+3]);
                in += 16;
            }
            for (; x < imIn->xsize; x++) {
                out0[x] = in[0];
                out1[x] = in[3];
                in += 4;
            }
        }
    } else if (imIn->bands == 3) {
        for (y = 0; y < imIn->ysize; y++) {
            UINT8* in = (UINT8*) imIn->image[y];
            UINT8* out0 = bands[0]->image8[y];
            UINT8* out1 = bands[1]->image8[y];
            UINT8* out2 = bands[2]->image8[y];
            x = 0;
            for (; x < imIn->xsize - 3; x += 4) {
                *((UINT32*) (out0 + x)) = MAKE_UINT32(in[0], in[4], in[8], in[12]);
                *((UINT32*) (out1 + x)) = MAKE_UINT32(in[0+1], in[4+1], in[8+1], in[12+1]);
                *((UINT32*) (out2 + x)) = MAKE_UINT32(in[0+2], in[4+2], in[8+2], in[12+2]);
                in += 16;
            }
            for (; x < imIn->xsize; x++) {
                out0[x] = in[0];
                out1[x] = in[1];
                out2[x] = in[2];
                in += 4;
            }
        }
    } else {
        for (y = 0; y < imIn->ysize; y++) {
            UINT8* in = (UINT8*) imIn->image[y];
            UINT8* out0 = bands[0]->image8[y];
            UINT8* out1 = bands[1]->image8[y];
            UINT8* out2 = bands[2]->image8[y];
            UINT8* out3 = bands[3]->image8[y];
            x = 0;
            for (; x < imIn->xsize - 3; x += 4) {
                *((UINT32*) (out0 + x)) = MAKE_UINT32(in[0], in[4], in[8], in[12]);
                *((UINT32*) (out1 + x)) = MAKE_UINT32(in[0+1], in[4+1], in[8+1], in[12+1]);
                *((UINT32*) (out2 + x)) = MAKE_UINT32(in[0+2], in[4+2], in[8+2], in[12+2]);
                *((UINT32*) (out3 + x)) = MAKE_UINT32(in[0+3], in[4+3], in[8+3], in[12+3]);
                in += 16;
            }
            for (; x < imIn->xsize; x++) {
                out0[x] = in[0];
                out1[x] = in[1];
                out2[x] = in[2];
                out3[x] = in[3];
                in += 4;
            }
        }
    }

    return imIn->bands;
}


Imaging
ImagingPutBand(Imaging imOut, Imaging imIn, int band)
{
    int x, y;

    /* Check arguments */
    if (!imIn || imIn->bands != 1 || !imOut)
        return (Imaging) ImagingError_ModeError();

    if (band < 0 || band >= imOut->bands)
        return (Imaging) ImagingError_ValueError("band index out of range");

    if (imIn->type  != imOut->type  ||
        imIn->xsize != imOut->xsize ||
        imIn->ysize != imOut->ysize)
        return (Imaging) ImagingError_Mismatch();

    /* Shortcuts */
    if (imOut->bands == 1)
        return ImagingCopy2(imOut, imIn);

    /* Special case for LXXA etc */
    if (imOut->bands == 2 && band == 1)
        band = 3;

    /* Insert band into image */
    for (y = 0; y < imIn->ysize; y++) {
        UINT8* in = imIn->image8[y];
        UINT8* out = (UINT8*) imOut->image[y] + band;
        for (x = 0; x < imIn->xsize; x++) {
            *out = in[x];
            out += 4;
        }
    }

    return imOut;
}

Imaging
ImagingFillBand(Imaging imOut, int band, int color)
{
    int x, y;

    /* Check arguments */
    if (!imOut || imOut->type != IMAGING_TYPE_UINT8)
        return (Imaging) ImagingError_ModeError();

    if (band < 0 || band >= imOut->bands)
        return (Imaging) ImagingError_ValueError("band index out of range");

    /* Special case for LXXA etc */
    if (imOut->bands == 2 && band == 1)
        band = 3;

    color = CLIP(color);

    /* Insert color into image */
    for (y = 0; y < imOut->ysize; y++) {
        UINT8* out = (UINT8*) imOut->image[y] + band;
        for (x = 0; x < imOut->xsize; x++) {
            *out = (UINT8) color;
            out += 4;
        }
    }

    return imOut;
}
