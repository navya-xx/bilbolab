import numpy as np
from scipy.signal import butter, filtfilt


def generate_time_vector(start, end, dt):
    """
    Generate a time vector from start to end with a given sample time interval.

    Parameters:
        start (float): The starting time.
        end (float): The ending time.
        dt (float): The time interval between consecutive samples.

    Returns:
        numpy.ndarray: Time vector from start to end (inclusive) with spacing equal to sample_time.
    """
    # Calculate the number of points needed. Adding 1 ensures the endpoint is included.
    num_points = int((end - start) / dt) + 1
    return np.linspace(start, end, num_points)


def fun_sample_random_input(t_vector, f_cutoff, sigma_I):
    """
    Generate a random input trajectory u by filtering randomly drawn values.
    The trajectory u starts at zero.

    Parameters:
        t_vector : array_like
            1D time vector starting at t[0] = 0.
        f_cutoff : float
            Cutoff frequency for the 6th order Butterworth filter.
        sigma_I : float
            Scaling (amplitude) of the signal.

    Returns:
        u : ndarray
            Random output vector corresponding to the length of t_vector.
    """
    # Ensure t_vector is a 1D array.
    t_vector = np.asarray(t_vector)
    if t_vector.ndim != 1:
        raise ValueError("Time vector must be one-dimensional (a column vector).")

    N = len(t_vector)

    # Compute sampling time and sampling frequency.
    Ts = t_vector[1] - t_vector[0]
    fs = 1.0 / Ts

    # Calculate the normalized cutoff frequency.
    # In MATLAB: Wn = 2*f_cutoff/fs, which is equivalent to f_cutoff/(fs/2) in Python.
    Wn = 2 * f_cutoff / fs

    # Design a 6th order Butterworth low-pass filter.
    b, a = butter(6, Wn, btype='low', analog=False)

    # Define a filtering function using zero-phase filtering.
    def filter_fun(u):
        return filtfilt(b, a, u)

    # Function to compute the crest factor: max(|u|) / RMS(u)
    def crest_factor(u):
        rms = np.sqrt(np.mean(u ** 2))
        return np.max(np.abs(u)) / rms if rms != 0 else np.inf

    # Generate random input sequence until the crest factor is below 3.
    current_crest = 10
    while current_crest > 3:
        # Generate random values in [-1, 1] of length 2*N.
        u = 2 * (np.random.rand(2 * N) - 0.5)
        u = filter_fun(u)
        current_crest = crest_factor(u)

    # Rescale the signal so that 2*std(u) falls within [-sigma_I, sigma_I].
    u = sigma_I * u / (2 * np.std(u))

    # Find the first index where |u| is close to zero.
    # The threshold is sigma_I * 10 / (100 * log(N/2)).
    threshold = sigma_I * 10 / (100 * np.log(N / 2))
    idx_candidates = np.where(np.abs(u) < threshold)[0]
    if len(idx_candidates) == 0 or (idx_candidates[0] + N > len(u)):
        # Fallback: if no index qualifies or there isn't enough room for a segment of length N,
        # return the first N samples.
        return u[:N]

    start_idx = idx_candidates[0]
    return u[start_idx:start_idx + N]
