from __future__ import division, print_function
import numpy as np
import warnings

tol = 1e-14  # Tolerance value used to avoid division by zero

class ModeVector:
    """
    A class for handling mode vectors, allowing for on-the-fly computation or precomputation.
    Mode vectors are essential for the DOA algorithms, representing the phase delays
    across the microphone array for potential source locations.
    """
    
    def __init__(self, L, fs, nfft, c, grid, mode="far", precompute=False):
        """
        Initializes the ModeVector object with microphone locations, sampling frequency, and other parameters.
        
        :param L: 2D numpy array of microphone positions
        :param fs: Sampling frequency
        :param nfft: FFT length
        :param c: Speed of sound
        :param grid: The grid object defining candidate source locations
        :param mode: 'far' or 'near', indicating the field mode
        :param precompute: Boolean flag indicating whether to precompute mode vectors
        """
        # Validate FFT length to be even
        if nfft % 2 == 1:
            raise ValueError("FFT length must be even.")
        
        self.precompute = precompute

        # Initialize position vectors for the grid and microphone locations
        p_x = grid.x[None, None, :]
        p_y = grid.y[None, None, :]
        p_z = grid.z[None, None, :]
        r_x = L[0, None, :, None]
        r_y = L[1, None, :, None]
        r_z = L[2, None, :, None] if L.shape[0] == 3 else np.zeros((1, L.shape[1], 1))

        # Compute distance based on the selected mode (far or near field)
        if mode == "near":
            dist = np.sqrt((p_x - r_x) ** 2 + (p_y - r_y) ** 2 + (p_z - r_z) ** 2)
        elif mode == "far":
            dist = (p_x * r_x) + (p_y * r_y) + (p_z * r_z)

        self.tau = dist / c  # Time of flight based on distance and speed of sound

        self.omega = 2 * np.pi * fs * np.arange(nfft // 2 + 1) / nfft  # Angular frequencies

        if precompute:
            self.modeVec = np.exp(1j * self.omega[:, None, None] * self.tau)
        else:
            self.modeVec = None

    def __getitem__(self, ref):
        """
        Allows for indexing into the mode vector, enabling on-the-fly computation if not precomputed.
        
        :param ref: The indices to compute or retrieve mode vectors for
        :return: Computed or retrieved mode vectors
        """
        if self.precompute:
            return self.modeVec[ref]
        else:
            return self.computeOnFly(ref)

    def computeOnFly(self, ref):
        """
        Computes mode vectors on the fly for the given indices.
        
        :param ref: The indices to compute mode vectors for
        :return: Computed mode vectors
        """
        # Dynamically compute mode vectors based on provided indices
        omega = self.omega[ref[0]]
        if len(ref) == 3:
            return np.exp(1j * omega * self.tau[:, ref[1], ref[2]])
        else:
            raise ValueError("Incorrect indexing of mode vectors.")

class DOA:
    """
    Base class for Direction of Arrival (DoA) estimation algorithms.
    """
    
    def __init__(self, L, fs, nfft, c=343.0, numSrc=1, mode="far", r=None, azimuth=None, colatitude=None, **kwargs):
        """
        Initializes the DOA object with microphone array configuration and other parameters.
        
        :param L: Microphone array positions
        :param fs: Sampling frequency
        :param nfft: FFT length
        :param c: Speed of sound
        :param numSrc: Number of sources to detect
        :param mode: 'far' or 'near' field mode
        :param r: Candidate distances from the origin for near-field mode
        :param azimuth: Candidate azimuth angles
        :param colatitude: Candidate colatitude angles
        """
        self.L = L  # Microphone positions
        self.fs = fs  # Sampling frequency
        self.nfft = nfft  # FFT length
        self.c = c  # Speed of sound
        self.numSrc = numSrc  # Number of sources
        self.mode = mode  # 'far' or 'near'
        
        # Additional initialization code for grid and mode vector omitted for brevity

class SRP(DOA):
    """
    Implements the Steered Response Power (SRP) algorithm for DoA estimation.
    """
    
    def __init__(self, L, fs, nfft, c=343.0, numSrc=1, mode="far", r=None, azimuth=None, colatitude=None, **kwargs):
        """
        Initializes the SRP object with the same parameters as the DOA class.
        """
        super().__init__(L, fs, nfft, c, numSrc, mode, r, azimuth, colatitude, **kwargs)
        self.numPairs = self.L.shape[1] * (self.L.shape[1] - 1) / 2  # Number of microphone pairs

    def Mic_tuning_direction(self, X):
    """
    Process the given multichannel signals to estimate DOA using the SRP-PHAT algorithm.
    
    :param X: Multichannel signals in the frequency domain. Shape: (num_mics, num_freq_bins, num_frames)
    """
    # Number of points in the search grid
    n_points = self.grid.n_points
    
    # Initialize the SRP-PHAT spectrum
    srp_phat_spectrum = np.zeros(n_points)
    
    # Loop over all grid points to compute SRP-PHAT
    for i, point in enumerate(self.grid.points):
        # Initialize accumulator for this grid point
        accumulator = 0
        
        # Loop over all pairs of microphones
        for m in range(self.num_mics - 1):
            for n in range(m + 1, self.num_mics):
                # Calculate the Time Difference of Arrival (TDOA) for this pair and grid point
                tdoa = self.calculateTDOA(m, n, point)
                
                # Convert TDOA to phase difference
                phase_diff = 2 * np.pi * self.freq_bins * tdoa / self.fs
                
                # Apply the PHAT weighting
                X_weighted_m = X[m, :, :] * np.exp(-1j * phase_diff)
                X_weighted_n = X[n, :, :]
                
                # Cross-correlation between the two weighted signals
                cross_corr = np.sum(np.conj(X_weighted_m) * X_weighted_n, axis=1)
                
                # Accumulate the power (magnitude of cross-correlation)
                accumulator += np.abs(cross_corr)
        
        # Store the accumulated power for this grid point
        srp_phat_spectrum[i] = np.sum(accumulator)
    
    # Find the index of the maximum value in the SRP-PHAT spectrum
    estimated_source_index = np.argmax(srp_phat_spectrum)
    
    # Retrieve the corresponding grid point as the estimated DOA
    estimated_doa = self.grid.points[estimated_source_index]
    
    return estimated_doa


# Example of instantiation and usage
# L = np.array([[0, 1], [1, 0], [0, 0]])  # Example microphone positions
# fs = 16000  # Example sampling frequency
# nfft = 512  # Example FFT length
# srp = SRP(L, fs, nfft)
# X = np.random.rand(L.shape[1], nfft//2+1, 100)  # Simulated frequency-domain signals
# srp.process(X)
