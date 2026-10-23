import math
from sensor.mock_sensor import MockSensor
import matplotlib.pyplot as plt
import config
from dsp.features import calculate_amplitude, calculate_signal_strength
from detection.threshold import calculate_adaptive_threshold
from detection.detector import detect_target
from dsp.iq_demod import demodulate_iq
import statistics

sensor = MockSensor()
iq_filter_window = 5
target_buffer_count = 100

background_buffer_count = 20

detections_by_frequency = {}

for tx_frequency in config.TX_FREQUENCIES:
    sensor.tx_frequency = tx_frequency
    print("tx_frequency:", tx_frequency)
    # background calibration
    sensor.sample_index = 0
    background_i_values = []
    background_q_values = []
    background_amplitudes = []
    background_start_index = 0
    for start in range(
            0,
            background_buffer_count * config.BUFFER_SIZE,
            config.BUFFER_SIZE
    ):
       current_buffer = []
       for _ in range(config.BUFFER_SIZE):
               current_buffer.append(sensor.read_sample())

       current_i, current_q = demodulate_iq(
         current_buffer,
         config.SAMPLING_FREQUENCY,
         tx_frequency,
         iq_filter_window,
         start
        )
       background_i_values.append(current_i)
       background_q_values.append(current_q)
       background_amplitudes.append(
            calculate_amplitude(current_i, current_q)
        )
    background_i = sum(background_i_values) / len(background_i_values)
    background_q = sum(background_q_values) / len(background_q_values)
    background_residual_amplitudes = []
    for current_i, current_q in zip(background_i_values, background_q_values):
        residual_i = current_i - background_i
        residual_q = current_q - background_q
        residual_amplitude = calculate_amplitude(
        residual_i, residual_q
        )
        background_residual_amplitudes.append(residual_amplitude)
    residual_mean = sum(background_residual_amplitudes) / len(background_residual_amplitudes)
    residual_std = statistics.stdev(background_residual_amplitudes)
    residual_threshold = residual_mean + config.THRESHOLD_K * residual_std
    # reference / measure
    start_sample_index = sensor.sample_index

    target_buffers = []
    for _ in range(target_buffer_count):
        current_buffer = []
        for _ in range(config.BUFFER_SIZE):
            current_buffer.append(sensor.read_sample())
        target_buffers.append(current_buffer)
    detections = []
    target_amplitudes = []
    signal_strengths = []
    target_ids = []
    phases = []
    for buffer_index, current_buffer in enumerate(target_buffers):
        i_value, q_value = demodulate_iq(
            current_buffer,
            config.SAMPLING_FREQUENCY,
            tx_frequency,
            iq_filter_window,
            start_sample_index + buffer_index * config.BUFFER_SIZE
        )
        amplitude = calculate_amplitude(i_value, q_value)
        target_amplitudes.append(amplitude)
        phase = math.atan2(q_value, i_value)
        if phase < 1:
            target_id = "Target"
        else:
            target_id = "Background"

        target_ids.append(target_id)
        signal_strength = calculate_signal_strength(
            amplitude,
            config.SIGNAL_STRENGTH_REFERENCE
        )
        signal_strengths.append(signal_strength)
        phases.append(phase)

        target_i = i_value - background_i
        target_q = q_value - background_q

        target_amplitude = calculate_amplitude(target_i, target_q)
        if_target = detect_target(target_amplitude, residual_threshold)
        final_target = if_target and target_id == "Target"
        detections.append(final_target)
        print(
            buffer_index,
            "Amplitude:", amplitude,
            "Strength:", signal_strength,
            "ID:", target_id,
            "Detection:", if_target,
            "Final:", final_target
        )
    detections_by_frequency[tx_frequency] = detections
print("detections:", detections_by_frequency)


print("Target ID:", target_ids)
print("Target count:", target_ids.count("Target"))
print("Background count:", target_ids.count("Background"))

minimum_consecutive = 3
confirmed_detections = []

max_consucitive = 0
current_consucitive = 0


for i in range(len(detections)):
    start = max(0, i - minimum_consecutive + 1)
    window = detections[start:i + 1]
    confirmed = len(window) == minimum_consecutive and all(window)
    confirmed_detections.append(confirmed)

print("confirmed consucitive:", sum(confirmed_detections))

event_start = None
event_end = None

for i, confirmed in enumerate(confirmed_detections):
    if confirmed and event_start is None:
        event_start = i - minimum_consecutive + 1
    if confirmed:
        event_end = i
print("Target event start:", event_start)
print("Target event end:", event_end)

buffer_duration = config.BUFFER_SIZE / config.SAMPLING_FREQUENCY

event_start_time =  event_start * buffer_duration
event_end_time = (event_end + 1) * buffer_duration

print("event_start_time:", event_start_time)
print("event_end_time:", event_end_time)

target_start_time_in_measurement = (config.TARGET_START_TIME - background_buffer_count * buffer_duration)
detection_latency = event_start_time - config.TARGET_START_TIME
detection_duration = event_end_time - event_start_time

print("Detection latency:", detection_latency)
print("Detection duration:", detection_duration)

print("Detected buffers:", sum(detections))
print("Total buffers:", len(detections))
print("Target amplitudes:", target_amplitudes)
print("Target phase:", phases)

