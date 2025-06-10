import logging

from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSizePolicy,
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QTimer, Qt

from src.detect import State
from src.action import Action, mouse_down, mouse_up


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MainWindow(QWidget):
    def __init__(self, capture_func, position_func, config):
        super().__init__()
        self.capture_func = capture_func
        self.position_func = position_func
        self.config = config

        # state and action
        self.state = State(config)
        self.action = Action()

        # flags
        self.detection = False  # flag for detection
        self.detection_initialize = False

        # NOTE buffer for frame delay, this feature may not be stable
        self.state_dict_buffer = []

        # buttons
        self.start_button = QPushButton("Activate (or press A)")
        self.stop_button = QPushButton("Quit (or press Q)")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_block = QWidget()
        button_block.setLayout(button_layout)

        # image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(button_block)
        main_layout.addStretch()  # push image to bottom
        main_layout.addWidget(self.image_label)
        self.setLayout(main_layout)

        # connect buttons
        self.start_button.clicked.connect(self.start_detection)
        self.stop_button.clicked.connect(self.stop_detection)

        # connect image
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image)
        self.timer.start(config.mspf)

    def create_bar_cache(self, width, height):
        bar_cache = QPixmap(width, height)
        bar_cache.fill(Qt.transparent)
        painter = QPainter(bar_cache)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # detection bar
        painter.setBrush(QColor(255, 0, 0, 100))
        detect_x = self.compute_bar_x(width, self.config.detect_bar_width)
        painter.drawRect(
            detect_x,
            self.config.detect_bar_y,
            self.config.detect_bar_width,
            self.config.bar_height,
        )

        # input bar
        painter.setBrush(QColor(0, 255, 0, 50))
        input_x = self.compute_bar_x(width, self.config.input_bar_width)
        painter.drawRect(
            input_x,
            self.config.input_bar_y,
            self.config.input_bar_width,
            self.config.bar_height,
        )

        painter.end()

        self.bar_cache = bar_cache

    @staticmethod
    def compute_bar_x(image_width, bar_width):
        return (image_width - bar_width) // 2

    def draw_bar(self, pixmap):
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(0, 0, self.bar_cache)  # draw with bar cache
        painter.setBrush(QColor(0, 255, 0, 200))
        painter.setPen(Qt.NoPen)
        painter.end()

    def click_window(self):
        x, y = self.position_func()
        mouse_down(x + 100, y + 100)
        mouse_up(x + 100, y + 100)

    def start_detection(self):
        logger.info("start detection")
        self.click_window()
        self.detection = True

    def stop_detection(self):
        logger.info("stop detection")
        self.detection = False
        self.detection_initialize = False
        self.state.reset()

    def update_image(self):
        img = self.capture_func()
        h, w, ch = img.shape
        q_img = QImage(img.tobytes(), w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        if self.detection:
            # initialize
            if not self.detection_initialize:
                self.create_bar_cache(w, h)
                self.detect_bar_x = self.compute_bar_x(w, self.config.detect_bar_width)
                self.input_bar_x = self.compute_bar_x(w, self.config.input_bar_width)
                self.ratio = self.config.input_bar_width / self.config.detect_bar_width
                self.detection_initialize = True

            # detection
            self.state.update_state(
                img[
                    self.config.detect_bar_y : self.config.detect_bar_y
                    + self.config.bar_height,
                    self.detect_bar_x : self.detect_bar_x
                    + self.config.detect_bar_width,
                ]
            )

            # not in gameplay or other error
            if self.state.invalid_detect:
                self.stop_detection()

            # queue to buffer
            self.state_dict_buffer.append(
                {
                    "actions": self.state.actions,
                    "states": self.state.get_resized_states(self.ratio),
                }
            )
            if len(self.state_dict_buffer) > self.config.delay_frames:
                # apply actions
                self.action.run(
                    state_dict=self.state_dict_buffer[0],
                    local_coordinate=(self.input_bar_x, self.config.input_bar_y),
                    global_coordinate=self.position_func(),
                )

                # visualize bar
                self.draw_bar(pixmap)

                # dequeue from buffer
                self.state_dict_buffer.pop(0)

        # Retina displays 1 point equals 2 pixels
        scaled_pixmap = pixmap.scaledToWidth(w // 2, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.start_detection()
        if event.key() == Qt.Key_Q:
            self.stop_detection()
