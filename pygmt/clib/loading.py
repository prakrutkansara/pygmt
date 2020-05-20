"""
Utility functions to load libgmt as ctypes.CDLL.

The path to the shared library can be found automatically by ctypes or set
through the GMT_LIBRARY_PATH environment variable.
"""
import os
import sys
import ctypes

from ..exceptions import GMTOSError, GMTCLibError, GMTCLibNotFoundError


def load_libgmt(env=None):
    """
    Find and load ``libgmt`` as a :py:class:`ctypes.CDLL`.

    By default, will look for the shared library in the directory specified by
    the environment variable ``GMT_LIBRARY_PATH``. If it's not set, will let
    ctypes try to find the library.

    Parameters
    ----------
    env : dict or None
        A dictionary containing the environment variables. If ``None``, will
        default to ``os.environ``.

    Returns
    -------
    :py:class:`ctypes.CDLL` object
        The loaded shared library.

    Raises
    ------
    GMTCLibNotFoundError
        If there was any problem loading the library (couldn't find it or
        couldn't access the functions).

    """
    if env is None:
        env = os.environ
    libnames = clib_name(os_name=sys.platform)
    libpath = env.get("GMT_LIBRARY_PATH", "")
    error = True
    for libname in libnames:
        try:
            if libpath:
                libgmt = ctypes.CDLL(os.path.join(libpath, libname))
            else:
                libgmt = ctypes.CDLL(ctypes.util.find_library(libname))
            check_libgmt(libgmt)
            error = False
            break
        except OSError as err:
            error = err
    if error:
        raise GMTCLibNotFoundError(
            "Error loading the GMT shared library '{}':".format(", ".join(libnames))
        )
    return libgmt


def clib_name(os_name):
    """
    Return the name of GMT's shared library for the current OS.

    Parameters
    ----------
    os_name : str
        The operating system name as given by ``sys.platform``.

    Returns
    -------
    libname : list of str
        List of possible names of GMT's shared library.

    """
    if os_name.startswith("linux"):
        libname = ["libgmt.so"]
    elif os_name == "darwin":
        # Darwin is macOS
        libname = ["libgmt.dylib"]
    elif os_name == "win32":
        libname = ["gmt.dll", "gmt_w64.dll", "gmt_w32.dll"]
    else:
        raise GMTOSError('Operating system "{}" not supported.'.format(sys.platform))
    return libname


def check_libgmt(libgmt):
    """
    Make sure that libgmt was loaded correctly.

    Checks if it defines some common required functions.

    Does nothing if everything is fine. Raises an exception if any of the
    functions are missing.

    Parameters
    ----------
    libgmt : :py:class:`ctypes.CDLL`
        A shared library loaded using ctypes.

    Raises
    ------
    GMTCLibError

    """
    # Check if a few of the functions we need are in the library
    functions = ["Create_Session", "Get_Enum", "Call_Module", "Destroy_Session"]
    for func in functions:
        if not hasattr(libgmt, "GMT_" + func):
            msg = " ".join(
                [
                    "Error loading libgmt.",
                    "Couldn't access function GMT_{}.".format(func),
                ]
            )
            raise GMTCLibError(msg)
