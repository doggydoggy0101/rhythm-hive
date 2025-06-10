import ctypes
import logging
import numpy as np

from AppKit import NSWorkspace
from Cocoa import NSBitmapImageRep
import Quartz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

APP_IDENTIFIER = "com.apple.ScreenContinuity"


def get_app_name() -> str:
    """
    Check if iPhone Mirroring is running and get its localized app name.

    Returns:
        str: Localized name of iPhone Mirroring.

    Raises:
        SystemExit: If iPhone Mirroring is not running or NSWorkspace is not available.
    """
    app_name = None

    if "NSWorkspace" not in globals():
        logger.warning("NSWorkspace not loaded, unable to check is app running")
        logger.info(
            "see `src.screen_capture.get_app_name()` if you want to remove this check"
        )
        exit(1)

    for app in NSWorkspace.sharedWorkspace().runningApplications():
        if app.bundleIdentifier() == APP_IDENTIFIER:
            app_name = app.localizedName()
            return app_name

    logger.error("iPhone Mirroring is not running, please start it first")
    exit(1)


def capture_iphone_mirroring() -> np.ndarray | None:
    """
    Captures iPhone Mirroring window and returns the image as a NumPy array.

    Returns:
        np.ndarray: The captured image as a NumPy array (Width, Height, Channels), or None on failure.
    """
    app_name = get_app_name()

    options = (
        Quartz.kCGWindowListOptionOnScreenOnly
        | Quartz.kCGWindowListExcludeDesktopElements
    )
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    logger.debug(f"start finding window of '{app_name}'")

    target_window_id = None
    for window in window_list:
        owner_name = window.get(Quartz.kCGWindowOwnerName)
        window_title = window.get(Quartz.kCGWindowName)
        window_layer = window.get(Quartz.kCGWindowLayer)
        window_id = window.get(Quartz.kCGWindowNumber)

        if owner_name == app_name:
            if window_layer == 0:
                logger.debug(
                    f"window found: ID={window_id}, Title='{window_title or 'Untitled'}'"
                )
                target_window_id = window_id
                break

    if target_window_id is None:
        logger.error(
            f"unable to find window of '{app_name}', note that it should be on your current desktop (space) as screen capture only works for visible windows"
        )
        return

    try:
        image_ref = Quartz.CGWindowListCreateImage(
            Quartz.CGRectNull,
            Quartz.kCGWindowListOptionIncludingWindow,
            target_window_id,
            Quartz.kCGWindowImageBoundsIgnoreFraming,
        )

        bitmap_rep = NSBitmapImageRep.alloc().initWithCGImage_(image_ref)

        # Convert NSBitmapImageRep to NumPy array
        width = int(bitmap_rep.pixelsWide())
        height = int(bitmap_rep.pixelsHigh())
        spp = int(bitmap_rep.samplesPerPixel())  # samples per pixel (4: ARGB)
        flag_alpha = bitmap_rep.bitmapFormat()  # alpha channel flag (1: AXXX)

        if spp == 1:  # Grayscale
            shape = (height, width)
        else:  # RGB or RGBA (ARGB)
            shape = (height, width, spp)

        logger.debug(f"bitmap shape (height, width, spp): {shape}")

        data_ptr = bitmap_rep.bitmapData()

        # create a ctypes array from the memoryview's buffer
        c_ubyte_array_type = ctypes.c_ubyte * height * width * spp
        c_array = c_ubyte_array_type.from_buffer_copy(data_ptr)

        # get a NumPy view and copy to a new NumPy array
        np_array_view = np.ctypeslib.as_array(c_array).reshape(shape)
        image_numpy = np_array_view.copy()

        if spp == 4 and flag_alpha == 1:
            image_numpy = image_numpy[..., [1, 2, 3]]  # convert ARGB to RGB
        else:
            logger.warning("bitmap not ARGB, which is not my case")

        logger.debug(f"image (height, width, channel): {image_numpy.shape}")

        return image_numpy

    except Exception as e:
        logger.exception(
            f"error in `src.screen_caputer.capture_iphone_mirroring() \n\n{e} \n\n"
        )
        return


def position_iphone_mirroring():
    """
    Computes position of iPhone Mirroring window and returns the cooridnate.

    Returns:
        tuple[int, int]: Global coordinate representing the top-left corner of the window.
    """
    app_name = get_app_name()

    options = (
        Quartz.kCGWindowListOptionOnScreenOnly
        | Quartz.kCGWindowListExcludeDesktopElements
    )
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    logger.debug(f"start finding window of '{app_name}'")

    for window in window_list:
        owner_name = window.get(Quartz.kCGWindowOwnerName)
        window_title = window.get(Quartz.kCGWindowName)
        window_layer = window.get(Quartz.kCGWindowLayer)
        window_id = window.get(Quartz.kCGWindowNumber)
        window_bound = window.get(Quartz.kCGWindowBounds)

        if owner_name == app_name:
            if window_layer == 0:
                logger.debug(
                    f"window found: ID={window_id}, Title='{window_title or 'Untitled'}'"
                )
                return window_bound["X"], window_bound["Y"]

    return None, None
