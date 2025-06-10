import logging
import numpy as np


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class State:
    def __init__(self, config):
        self.config = config
        # NOTE there is a maximimum of two states (left and right hand) in Rhythm Hive
        self.states = [None, None]
        self.actions = [None, None]
        self.invalid_detect = False  # flag for stop detection

    def reset(self):
        self.states = [None, None]
        self.actions = [None, None]
        self.invalid_detect = False

    def detect_position(self, detect_bar):
        position_list = []
        start = None

        max_detect_bar = np.max(detect_bar @ self.config.luminance_weight, axis=0)

        for i, val in enumerate(max_detect_bar):
            if val > self.config.slide_luminance_threshold:
                if start is None:
                    start = i
            else:
                if start is not None:
                    end = i - 1
                    if end - start > self.config.max_width_threshold:
                        return
                    # check outliers with width threshold
                    if end - start > self.config.min_width_threshold:
                        position_list.append((end + start) // 2)
                    start = None

        # edge case
        if start is not None:
            end = len(max_detect_bar) - 1
            if end - start > self.config.max_width_threshold:
                return
            # check outliers with width threshold
            if end - start > self.config.min_width_threshold:
                position_list.append((end + start) // 2)

        return position_list

    def update_state(self, detect_bar):
        # clear state after release
        for i in range(2):
            if self.actions[i] == "release":
                self.states[i] = None

        # clear action
        self.actions = [None, None]

        # detection
        position_list = self.detect_position(detect_bar)
        if position_list is None:
            logger.error("invalid length of inputs, likely out of gameplay")
            self.invalid_detect = True
            return
        if len(position_list) > 2:
            logger.error("invalid number of inputs, likely out of gameplay")
            self.invalid_detect = True
            return

        # match new positions to states
        for i in range(2):
            if self.states[i] is not None:
                matched = False
                for p in position_list:
                    # determine same state
                    if abs(p - self.states[i]) <= self.config.slide_position_threshold:
                        # assign move
                        if p != self.states[i]:
                            self.actions[i] = "move"
                        # update state
                        self.states[i] = p
                        matched = True
                        position_list.remove(p)
                        break
                if not matched:
                    self.actions[i] = "release"

        # assign new positions to states
        if len(position_list) == 2:
            for i in range(2):
                self.states[i] = position_list[0]
                self.actions[i] = "press"
                position_list.pop(0)
            position_list = []
        elif len(position_list) == 1:
            if self.states[0] is not None:
                self.states[0] = position_list[0]
                self.actions[0] = "press"
            else:
                self.states[1] = position_list[0]
                self.actions[1] = "press"
            position_list.pop(0)
        # NOTE there shouldn't be any positions left now
        if len(position_list) != 0:
            logger.error("unassigned positions remain")
            self.invalid_detect = True
            return

        # clear state if no action
        for i in range(2):
            if self.actions[i] is None:
                self.states[i] = None

    def get_resized_states(self, ratio):
        # NOTE states are in detect_bar coordinate, return states in input_bar coordinate
        return [state * ratio if state is not None else None for state in self.states]
