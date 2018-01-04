from PIL.aliases import *
from typing import Optional, List, Text, Any

PILLOW_VERSION = ...
DEFAULT_STRATEGY = ...
FILTERED = ...
HUFFMAN_ONLY = ...
RLE = ...
FIXED = ...

# List of functions is incomplete

def alpha_composite(core1: ImagingCore, core2: ImagingCore) -> ImagingCore: ...
def blend(core1: ImagingCore, core2: ImagingCore, alpha: float) -> ImagingCore: ...
def fill(mode: Mode, size: Size, color: Any) -> Any: ...
def new(mode: Mode, size: Size) -> ImagingCore: ...
def merge(mode: Mode, im1: ImagingCore, im2: ImagingCore=...,
          im3: ImagingCore=..., im4: ImagingCore=...) -> ImagingCore: ...
### FIXME: Are these merge values defaults or Optional?

def map_buffer(target_data: Any, size: Size, decoder_name: Text,
               bbox: Optional[Any], offset: int, args: Tuple[Mode, int, int]
               ) -> ImagingCore: ...  ### what are data & bbox?

def crc32(buffer: bytes, hilo: Tuple[int, int]=(0,0)) -> Tuple[int, int]: ...

def effect_mandelbrot(size: Size=(512,512),
                      extent: Tuple[float, float, float, float]=(-3,-2.5,2,2.5),
                      quality: int=100) -> ImagingCore: ...
def effect_noise(size: Size, sigma: float=128) -> ImagingCore: ...
def linear_gradient(mode: Mode) -> ImagingCore: ...
def radial_gradient(mode: Mode) -> ImagingCore: ...
def wedge(mode: Mode) -> ImagingCore: ...

### FIXME TYPING: Should defaults be included here? they could get out of sync with _imaging.c
### FIXME TYPING: Unsure of the default values in some cases.

class ImagingCore:
    mode = ...  # type: Mode
    size = ...  # type: Size
    bands = ...  # type: int
    id = ... # type: Any  ### FIXME TYPING: Can be more specific?
    ptr = ... # type: Any  ### FIXME TYPING: Can be more specific?

    def getpixel(self, xy: XY) -> Optional[Color]: ...
    def putpixel(self, xy: XY, value: Any) -> None: ...  ### FIXME TYPING: Color?
    def pixel_access(self, readonly: int) -> Any: ...
    def convert(self, mode: Mode, dither: int=..., paletteimage: ImagingCore=...) -> ImagingCore: ...
    def convert2(self, im1: ImagingCore, im2: ImagingCore) -> None: ...
    def convert_matrix(self, mode: Mode, matrix: Union[Matrix4, Matrix12]) -> ImagingCore: ...
    def convert_transparent(self, mode: Mode, t: Union[Tuple[int, int, int], int]) -> ImagingCore: ...
    def copy(self) -> ImagingCore: ...
    def crop(self, bbox: LURD) -> ImagingCore: ...
    def expand(self, xmargin: int, ymargin: int, mode_index: int=0) -> ImagingCore: ...
    def filter(self, size: Size, divisor: float, offset: float, kernel: List[float]) -> ImagingCore: ...
    def histogram(self, extrema: Union[Tuple[float, float], Tuple[int, int]]=...,
                  mask: ImagingCore=...) -> List[int]: ...  ### Do they take None?
    def modefilter(self, i: int) -> Any: ...
#    def offset(self): ... ### Function removed?
    def paste(self, core: Union[ImagingCore, Color], box: LURD, coremask: ImagingCore=...) -> None: ...
    def point(self, lut: Union[List[int], List[float]], mode: Optional[Mode]) -> ImagingCore: ...
    def point_transform(self, scale: float=1.0, offset: float=0.0) -> ImagingCore: ...
    def putdata(self, data: Any, scale: float=1.0, offset: float=0.0) -> None: ...
    def quantize(self, colors: int=..., method: int=..., kmeans: int=...) -> ImagingCore: ...
    def rankfilter(self, size: int, rank: int) -> ImagingCore: ...
    def resize(self, size: Size, resample: int=..., box: LURD=(0,0,0,0)) -> ImagingCore: ...
    def transpose(self, method: int) -> ImagingCore: ...
    def transform2(self, box: LURD, core: ImagingCore, method: int,
                   data: List[float], resample: int=..., fill: int=...) -> None: ...
    def isblock(self) -> int: ...
    def getbbox(self) -> Optional[LURD]: ...
    def getcolors(self, maxcolors: int) -> Optional[List[Tuple[int, Color]]]: ... ###################
    def getextrema(self) -> SingleChannelExtrema: ...
    def getprojection(self) -> Tuple[List[int], List[int]]: ...
    def getband(self, band: int) -> ImagingCore: ...
    def putband(self, image: ImagingCore, band_index: int) -> None: ...
    def split(self) -> List[ImagingCore]: ...
    def fillband(self, band: int, color: int) -> None: ...
    def setmode(self, mode: Mode) -> None: ...
    def getpalette(self, mode: Mode="RGB", rawmode: Mode="RGB") -> bytes: ...
    def getpalettemode(self) -> Mode: ...
    def putpalette(self, rawmode: Mode, palettes: bytes) -> None: ...
    def putpalettealpha(self, index: int, alpha: int=...) -> None: ...
    def putpalettealphas(self, alphas: bytes) -> None: ...

### chop_* here

### gaussian_blur and unsharp_mask here

### box_blur here

    def effect_spread(self, distance: int) -> ImagingCore: ...
    def new_block(self, mode: Mode, size: Size) -> ImagingCore: ...
    def save_ppm(self, file: Text) -> None: ...
