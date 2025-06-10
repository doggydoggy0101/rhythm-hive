import sys
import logging
import numpy as np

from PyQt5.QtWidgets import QApplication

from src.screen_capture import position_iphone_mirroring, capture_iphone_mirroring
from src.app import MainWindow


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(message)s",
)


class Config:
    def __init__(self):
        # detection parameters
        self.bar_height = 30
        self.detect_bar_y = 250
        self.detect_bar_width = 420
        self.input_bar_y = 500
        self.input_bar_width = 840
        self.min_width_threshold = 50
        self.max_width_threshold = 120

        # luminance parameters
        self.luminance_weight = np.array([0.299, 0.587, 0.114])  # RGB
        self.luminance_threshold = 196

        # movement parameters
        self.move_threshold = 50

        # time paramters
        self.mspf = 20  # 50 fps
        self.delay_frames = 1


if __name__ == "__main__":
    image = capture_iphone_mirroring()
    global_x, global_y = position_iphone_mirroring()

    if image is None:
        logger.error("failed to capture image from iPhone mirroring")
        exit(1)
    elif global_x is None:
        logger.error("failed to position of iPhone mirroring")
        exit(1)
    else:
        logger.info(f"image shape: {image.shape[:2]}")
        logger.info(f"iPhone Mirroring position: ({global_x}, {global_y})")

    config = Config()

    app = QApplication(sys.argv)
    window = MainWindow(
        capture_func=capture_iphone_mirroring,
        position_func=position_iphone_mirroring,
        config=config,
    )
    window.setWindowTitle("🌸🎮🐱")
    window.show()
    sys.exit(app.exec_())
