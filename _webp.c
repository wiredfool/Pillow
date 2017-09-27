#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "Imaging.h"
#include "py3.h"
#include <webp/encode.h>
#include <webp/decode.h>
#include <webp/types.h>

#ifdef HAVE_WEBPMUX
#include <webp/mux.h>
#endif

static PyObject* WebPEncode_wrapper(PyObject* self, PyObject* args)
{
    int width;
    int height;
    int lossless;
    float quality_factor;
    uint8_t *rgb;
    uint8_t *icc_bytes;
    uint8_t *exif_bytes;
    uint8_t *output;
    char *mode;
    Py_ssize_t size;
    Py_ssize_t icc_size;
    Py_ssize_t  exif_size;
    size_t ret_size;

    if (!PyArg_ParseTuple(args, PY_ARG_BYTES_LENGTH"iiifss#s#",
                (char**)&rgb, &size, &width, &height, &lossless, &quality_factor, &mode,
                &icc_bytes, &icc_size, &exif_bytes, &exif_size)) {
        return NULL;
    }
    if (strcmp(mode, "RGBA")==0){
        if (size < width * height * 4){
            Py_RETURN_NONE;
        }
        #if WEBP_ENCODER_ABI_VERSION >= 0x0100
        if (lossless) {
            ret_size = WebPEncodeLosslessRGBA(rgb, width, height, 4* width, &output);
        } else
        #endif
        {
            ret_size = WebPEncodeRGBA(rgb, width, height, 4* width, quality_factor, &output);
        }
    } else if (strcmp(mode, "RGB")==0){
        if (size < width * height * 3){
            Py_RETURN_NONE;
        }
        #if WEBP_ENCODER_ABI_VERSION >= 0x0100
        if (lossless) {
            ret_size = WebPEncodeLosslessRGB(rgb, width, height, 3* width, &output);
        } else
        #endif
        {
            ret_size = WebPEncodeRGB(rgb, width, height, 3* width, quality_factor, &output);
        }
    } else {
        Py_RETURN_NONE;
    }

#ifndef HAVE_WEBPMUX
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize((char*)output, ret_size);
        free(output);
        return ret;
    }
#else
   {
    /* I want to truncate the *_size items that get passed into webp
       data. Pypy2.1.0 had some issues where the Py_ssize_t items had
       data in the upper byte. (Not sure why, it shouldn't have been there)
    */
    int i_icc_size = (int)icc_size;
    int i_exif_size = (int)exif_size;
    WebPData output_data = {0};
    WebPData image = { output, ret_size };
    WebPData icc_profile = { icc_bytes, i_icc_size };
    WebPData exif = { exif_bytes, i_exif_size };
    WebPMuxError err;
    int dbg = 0;

    int copy_data = 0;  // value 1 indicates given data WILL be copied to the mux
                        // and value 0 indicates data will NOT be copied.

    WebPMux* mux = WebPMuxNew();
    WebPMuxSetImage(mux, &image, copy_data);

    if (dbg) {
        /* was getting %ld icc_size == 0, icc_size>0 was true */
        fprintf(stderr, "icc size %d, %d \n", i_icc_size, i_icc_size > 0);
    }

    if (i_icc_size > 0) {
        if (dbg) {
            fprintf (stderr, "Adding ICC Profile\n");
        }
        err = WebPMuxSetChunk(mux, "ICCP", &icc_profile, copy_data);
        if (dbg && err == WEBP_MUX_INVALID_ARGUMENT) {
            fprintf(stderr, "Invalid ICC Argument\n");
        } else if (dbg && err == WEBP_MUX_MEMORY_ERROR) {
            fprintf(stderr, "ICC Memory Error\n");
        }
    }

    if (dbg) {
        fprintf(stderr, "exif size %d \n", i_exif_size);
    }
    if (i_exif_size > 0) {
        if (dbg){
            fprintf (stderr, "Adding Exif Data\n");
        }
        err = WebPMuxSetChunk(mux, "EXIF", &exif, copy_data);
        if (dbg && err == WEBP_MUX_INVALID_ARGUMENT) {
            fprintf(stderr, "Invalid Exif Argument\n");
        } else if (dbg && err == WEBP_MUX_MEMORY_ERROR) {
            fprintf(stderr, "Exif Memory Error\n");
        }
    }

    WebPMuxAssemble(mux, &output_data);
    WebPMuxDelete(mux);
    free(output);

    ret_size = output_data.size;
    if (ret_size > 0) {
        PyObject *ret = PyBytes_FromStringAndSize((char*)output_data.bytes, ret_size);
        WebPDataClear(&output_data);
        return ret;
    }
    }
#endif
    Py_RETURN_NONE;
}

// Return the decoder's version number, packed in hexadecimal using 8bits for
// each of major/minor/revision. E.g: v2.5.7 is 0x020507.
static PyObject* WebPDecoderVersion_wrapper(PyObject* self, PyObject* args){
    return Py_BuildValue("i", WebPGetDecoderVersion());
}


int WebPDecoderBuggyAlpha(void) {
    return WebPGetDecoderVersion()==0x0103;
}

/*
 * The version of webp that ships with (0.1.3) Ubuntu 12.04 doesn't handle alpha well.
 * Files that are valid with 0.3 are reported as being invalid.
 */

static PyObject* WebPDecoderBuggyAlpha_wrapper(PyObject* self, PyObject* args){
    return Py_BuildValue("i", WebPDecoderBuggyAlpha());
}

static PyMethodDef webpMethods[] =
{
    {"WebPEncode", WebPEncode_wrapper, METH_VARARGS, "WebPEncode"},
    {"WebPDecoderVersion", WebPDecoderVersion_wrapper, METH_VARARGS, "WebPVersion"},
    {"WebPDecoderBuggyAlpha", WebPDecoderBuggyAlpha_wrapper, METH_VARARGS, "WebPDecoderBuggyAlpha"},
    {NULL, NULL}
};

static void addMuxFlagToModule(PyObject* m) {
#ifdef HAVE_WEBPMUX
    PyModule_AddObject(m, "HAVE_WEBPMUX", Py_True);
#else
    PyModule_AddObject(m, "HAVE_WEBPMUX", Py_False);
#endif
}

void addTransparencyFlagToModule(PyObject* m) {
    PyModule_AddObject(m, "HAVE_TRANSPARENCY",
		       PyBool_FromLong(!WebPDecoderBuggyAlpha()));
}


#if PY_VERSION_HEX >= 0x03000000
PyMODINIT_FUNC
PyInit__webp(void) {
    PyObject* m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_webp",            /* m_name */
        NULL,               /* m_doc */
        -1,                 /* m_size */
        webpMethods,        /* m_methods */
    };

    m = PyModule_Create(&module_def);
    addMuxFlagToModule(m);
    addTransparencyFlagToModule(m);
    return m;
}
#else
PyMODINIT_FUNC
init_webp(void)
{
    PyObject* m = Py_InitModule("_webp", webpMethods);
    addMuxFlagToModule(m);
    addTransparencyFlagToModule(m);
}
#endif
