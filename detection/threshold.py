import math
import statistics
import config

def calculate_adaptive_threshold(array):
    mean = sum(array) / len(array)
    standard_deviation = statistics.stdev(array)
    adaptive_threshold = mean + config.THRESHOLD_K * standard_deviation
    return adaptive_threshold