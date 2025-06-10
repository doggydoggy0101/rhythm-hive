import logging

from Quartz.CoreGraphics import (
    CGEventCreateMouseEvent,
    CGEventPost,
    kCGHIDEventTap,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGEventLeftMouseDragged,
    kCGMouseButtonLeft,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def mouse_event(type, x, y):
    event = CGEventCreateMouseEvent(None, type, (x, y), kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, event)


def mouse_down(x, y):
    mouse_event(kCGEventLeftMouseDown, x, y)


def mouse_up(x, y):
    mouse_event(kCGEventLeftMouseUp, x, y)


def mouse_drag(x, y):
    mouse_event(kCGEventLeftMouseDragged, x, y)


class Action:
    def map2screen(self, rel_x):
        # Retina displays 1 point equals 2 pixels
        x = self.global_x + (rel_x + self.local_x) // 2
        y = self.global_y + self.local_y // 2
        return x, y

    def run(self, state_dict, local_coordinate, global_coordinate):
        self.local_x, self.local_y = local_coordinate
        self.global_x, self.global_y = global_coordinate

        for state, action in zip(state_dict["states"], state_dict["actions"]):
            if action == "press":
                x, y = self.map2screen(state)
                logger.debug(f"press at global coordinate: ({x}, {y})")
                mouse_down(x, y)

            if action == "move":
                x, y = self.map2screen(state)
                logger.debug(f"move to global coordinate: ({x}, {y})")
                mouse_drag(x, y)

            if action == "release":
                x, y = self.map2screen(state)
                logger.debug(f"release at global coordinate: ({x}, {y})")
                mouse_drag(x, y - 5)
                mouse_up(x, y - 5)
