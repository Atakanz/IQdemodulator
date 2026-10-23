import math

def demodulate_iq(signal, sampling_frequency, reference_frequency, filter_window=5, start_sample_index=0):
    i_mixed = []
    q_mixed = []

    for n, sample in enumerate(signal):

        sample_index = start_sample_index + n
        t = sample_index / sampling_frequency

        reference_cos = math.cos(
            2 * math.pi * reference_frequency * t
        )

        reference_sin = math.sin(
            2 * math.pi * reference_frequency * t
        )

        i_mixed.append(sample * reference_cos)
        q_mixed.append(sample * reference_sin)

    i_filtered = []
    q_filtered = []

    for n in range(filter_window - 1, len(signal)):

        i_window = i_mixed[n - filter_window + 1:n + 1]
        q_window = q_mixed[n - filter_window + 1:n + 1]

        i_filtered.append(sum(i_window) / len(i_window))
        q_filtered.append(sum(q_window) / len(q_window))

    i_value = sum(i_filtered) / len(i_filtered)
    q_value = sum(q_filtered) / len(q_filtered)

    return i_value, q_value