import math
import random
import config

class MockSensor:
    def __init__(self):
        self.tx_frequency = config.TX_REFERENCE
        self.sample_index = 0

    def read_sample(self):
        t = self.sample_index / config.SAMPLING_FREQUENCY
        signal = 0.0
        signal += config.GROUND_AMPLITUDE * math.sin(2 * math.pi * self.tx_frequency * t)
        if config.TARGET_START_TIME <= t <= config.TARGET_END_TIME:
           signal += config.TARGET_AMPLITUDE * math.sin(2 * math.pi * self.tx_frequency * t + config.TARGET_PHASE)
        signal += config.EMI_AMPLITUDE * math.sin(2 * math.pi * config.EMI_FREQUENCY * t)
        signal += random.gauss(0, config.NOISE_STD)
        self.sample_index += 1
        return signal
