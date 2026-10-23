import math

def calculate_amplitude(i_val, q_val):
    return 2 * math.sqrt(i_val ** 2 + q_val ** 2)

def calculate_signal_strength(amplitude, reference_amplitude):
    strength = (amplitude / reference_amplitude) * 100
    return min(100, max(0, strength))