from fetch import fetch
from unzip import unzip
from untar import untar
import os, hashlib
import shutil

from config import *

def _relpath(*args):
    return os.path.join(os.getcwd(),*args)

def _relbuild(*args):
    return _relpath('build', *args)

build_dir = _relpath('build')
inc_dir = _relpath('depends')

def check_hash(filename, checksum):
    if not checksum: return filename
    
    (algo, value) = checksum.split(':')
    h = hashlib.new(algo)
    with open(filename, 'rb') as f:
        h.update(f.read())
        if not(h.hexdigest().lower() == value):
            raise ValueError('Checksum Mismatch for %s' %filename)
    return filename

def check_sig(filename, signame):
    #UNDONE -- need gpg
    return filename

def mkdirs():
    try:
        os.mkdir(build_dir)
    except:
        pass
    try:
        os.mkdir(inc_dir)
    except:
        pass
    for compiler in compilers.values():
        try:
            os.mkdir(os.path.join(inc_dir, compiler['inc_dir']))
        except: 
            pass

def extract(src, dest):
    if '.zip' in src:
        return unzip(src, dest)
    if '.tar.gz' in src or '.tgz' in src:
        return untar(src, dest)

def fetch_libs():
    for name,lib in libs.items():
        if name == 'openjpeg':
            filename = check_hash(fetch(lib['url']),lib['hash'])
            for compiler in compilers.values():
                if not os.path.exists(os.path.join(build_dir,lib['dir']+compiler['inc_dir'])): 
                    extract(filename, build_dir)
                    os.rename(os.path.join(build_dir,lib['dir']), 
                              os.path.join(build_dir,lib['dir']+compiler['inc_dir'])) 
        else:
            extract(check_hash(fetch(lib['url']),lib['hash']),build_dir)

def extract_binlib():
    lib = bin_libs['openjpeg']
    extract(lib['filename'], build_dir)
    return
    base = os.path.splitext(lib['filename'])[0]
    for compiler in compilers.values():
        shutil.copy(os.path.join(inc_dir, base, 'include', 'openjpeg-%s' % lib['version']), 
                    os.path.join(inc_dir, compiler['inc_dir']))
        shutil.copy(os.path.join(inc_dir, base, 'bin', 'openjp2.dll'), 
                    os.path.join(inc_dir, compiler['inc_dir']))
        shutil.copy(os.path.join(inc_dir, base, 'lib', 'openjp2.lib'), 
                    os.path.join(inc_dir, compiler['inc_dir']))

def extract_openjpeg(compiler):
    return r"""
rem build openjpeg
setlocal
@echo on
cd %%BUILD%%
mkdir %%INCLIB%%\openjpeg-2.0
copy /Y /B openjpeg-2.0.0-win32-x86\include\openjpeg-2.0  %%INCLIB%%\openjpeg-2.0
copy /Y /B openjpeg-2.0.0-win32-x86\bin\  %%INCLIB%%
copy /Y /B openjpeg-2.0.0-win32-x86\lib\  %%INCLIB%%
endlocal
""" % compiler
        
def cp_tk():
    return r"""
mkdir %INCLIB%\tcl85\include\X11
copy /Y /B %BUILD%\tcl8.5.13\generic\*.h %INCLIB%\tcl85\include\
copy /Y /B %BUILD%\tk8.5.13\generic\*.h %INCLIB%\tcl85\include\
copy /Y /B %BUILD%\tk8.5.13\xlib\X11\* %INCLIB%\tcl85\include\X11\
"""

def header():
    return r"""setlocal
set MSBUILD=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe
set CMAKE="cmake.exe"
set INCLIB=%~dp0\depends
set BUILD=%~dp0\build
""" + "\n".join('set %s=%%BUILD%%\%s' %(k.upper(), v['dir'])
                                        for (k,v) in libs.items() if v['dir'])
    
def setup_compiler(compiler):
    return r"""setlocal EnableDelayedExpansion
call "%%ProgramFiles%%\Microsoft SDKs\Windows\%(env_version)s\Bin\SetEnv.Cmd" /Release %(env_flags)s
set INCLIB=%%INCLIB%%\%(inc_dir)s
""" % compiler

def end_compiler():
    return """
endlocal
"""
        
def nmake_openjpeg(compiler):
    atts = {'op_ver': '2.1'}
    atts.update(compiler)
    return r"""
rem build openjpeg
setlocal
@echo on
cd /D %%OPENJPEG%%%(inc_dir)s
%%CMAKE%% -DBUILD_THIRDPARTY:BOOL=OFF -G "NMake Makefiles" .
nmake -f Makefile clean
nmake -f Makefile
copy /Y /B bin\* %%INCLIB%%
mkdir %%INCLIB%%\openjpeg-%(op_ver)s
copy /Y /B src\lib\openjp2\*.h %%INCLIB%%\openjpeg-%(op_ver)s
endlocal
""" % atts

def msbuild_openjpeg(compiler):
    atts = {'op_ver': '2.1'}
    atts.update(compiler)
    return r"""
rem build openjpeg
setlocal
@echo on
cd /D %%OPENJPEG%%%(inc_dir)s

%%CMAKE%% -DBUILD_THIRDPARTY:BOOL=OFF -G "NMake Makefiles" .
nmake -f Makefile clean
nmake -f Makefile
copy /Y /B bin\* %%INCLIB%%
mkdir %%INCLIB%%\openjpeg-%(op_ver)s
copy /Y /B src\lib\openjp2\*.h %%INCLIB%%\openjpeg-%(op_ver)s
endlocal
""" % atts



def nmake_libs(compiler):
    # undone -- pre, makes, headers, libs
    return r"""
rem Build libjpeg
setlocal
cd /D %%JPEG%%
nmake -f makefile.vc setup-vc6
nmake -f makefile.vc clean
nmake -f makefile.vc libjpeg.lib
copy /Y /B *.dll %%INCLIB%%
copy /Y /B *.lib %%INCLIB%%
copy /Y /B j*.h %%INCLIB%%
endlocal

rem Build zlib
setlocal
cd /D %%ZLIB%%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc zlib.lib
copy /Y /B *.dll %%INCLIB%%
copy /Y /B *.lib %%INCLIB%%
copy /Y /B zlib.lib %%INCLIB%%\z.lib
copy /Y /B zlib.h %%INCLIB%%
copy /Y /B zconf.h %%INCLIB%%
endlocal

rem Build webp
setlocal
cd /D %%WEBP%%
rd /S /Q %%WEBP%%\output\release-static
nmake -f Makefile.vc CFG=release-static RTLIBCFG=static OBJDIR=output all
copy /Y /B output\release-static\%(webp_platform)s\lib\* %%INCLIB%%
mkdir %%INCLIB%%\webp
copy /Y /B src\webp\*.h %%INCLIB%%\\webp
endlocal

rem Build libtiff
setlocal
rem do after building jpeg and zlib
copy %%~dp0\nmake.opt %%TIFF%%

cd /D %%TIFF%%
nmake -f makefile.vc clean
nmake -f makefile.vc lib
copy /Y /B libtiff\*.dll %%INCLIB%%
copy /Y /B libtiff\*.lib %%INCLIB%%
copy /Y /B libtiff\tiff*.h %%INCLIB%%
endlocal


""" % compiler
    
def msbuild_freetype(compiler):
	if compiler['env_version'] == 'v7.1':
		return msbuild_freetype_71(compiler)
	return msbuild_freetype_70(compiler)
      
def msbuild_freetype_71(compiler):
    return r"""
rem Build freetype
setlocal
rd /S /Q %%FREETYPE%%\objs
%%MSBUILD%% %%FREETYPE%%\builds\windows\vc%(vc_version)s\freetype.sln /t:Clean;Build /p:Configuration="Release" /p:Platform=%(platform)s /m 
xcopy /Y /E /Q %%FREETYPE%%\include %%INCLIB%%
copy /Y /B %%FREETYPE%%\objs\vc%(vc_version)s\%(platform)s\*.lib %%INCLIB%%\freetype.lib
endlocal
""" %compiler

def msbuild_freetype_70(compiler):
    return r"""
rem Build freetype
setlocal
py -3 %%~dp0\fixproj.py %%FREETYPE%%\builds\windows\vc%(vc_version)s\freetype.sln %(platform)s
py -3 %%~dp0\fixproj.py %%FREETYPE%%\builds\windows\vc%(vc_version)s\freetype.vcproj %(platform)s
rd /S /Q %%FREETYPE%%\objs
%%MSBUILD%% %%FREETYPE%%\builds\windows\vc%(vc_version)s\freetype.sln /t:Clean;Build /p:Configuration="LIB Release";Platform=%(platform)s /m 
xcopy /Y /E /Q %%FREETYPE%%\include %%INCLIB%%
xcopy /Y /E /Q %%FREETYPE%%\objs\win32\vc%(vc_version)s %%INCLIB%%
copy /Y /B %%FREETYPE%%\objs\win32\vc%(vc_version)s\*.lib %%INCLIB%%\freetype.lib
endlocal
""" %compiler

def build_lcms2(compiler):
    return r"""
rem Build lcms2
setlocal
rd /S /Q %%LCMS%%\Lib
rd /S /Q %%LCMS%%\Projects\VC%(vc_version)s\Release
%%MSBUILD%% %%LCMS%%\Projects\VC%(vc_version)s\lcms2.sln /t:Clean /p:Configuration="Release" /p:Platform=%(platform)s /m
%%MSBUILD%% %%LCMS%%\Projects\VC%(vc_version)s\lcms2.sln /t:lcms2_static /p:Configuration="Release" /p:Platform=%(platform)s /m
xcopy /Y /E /Q %%LCMS%%\include %%INCLIB%%
copy /Y /B %%LCMS%%\Projects\VC%(vc_version)s\Release\*.lib %%INCLIB%%
copy /Y /B %%LCMS%%\Lib\MS\*.lib %%INCLIB%%
endlocal
""" % compiler


def add_compiler(compiler):
    script.append(setup_compiler(compiler))
    script.append(nmake_libs(compiler))

    #script.append(extract_openjpeg(compiler))
   
    script.append(msbuild_freetype(compiler))
    #script.append(build_lcms2(compiler))
    #script.append(nmake_openjpeg(compiler))
    script.append(end_compiler())



mkdirs()
fetch_libs()
#extract_binlib()
script = [header()] #, cp_tk()]

    

if 'PYTHON' in os.environ:
    add_compiler(compiler_fromEnv())
else:
    for compiler in compilers.values():
        add_compiler(compiler)
    #add_compiler(compilers[(7,32)])
    
with open('build_deps.cmd', 'w') as f:    
    f.write("\n".join(script))




