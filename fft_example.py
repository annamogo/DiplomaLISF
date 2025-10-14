from scipy.fft import fft, fftfreq, ifft
import numpy as np
import matplotlib.pyplot as plt

# Number of sample points
N = 600
# Sample spacing (e.g., time interval between samples)
T = 1.0 / 800.0

# Generate a sample signal (sum of two sines)
x = np.linspace(0.0, N*T, N, endpoint=False)
y = np.sin(50.0 * 2.0*np.pi*x) + np.sin(80.0 * 2.0*np.pi*x)

# Perform the FFT
yf = fft(y)
yif = ifft(yf)

# Generate the corresponding frequency values
xf = fftfreq(N, T)[:N//2] # Only positive frequencies are typically plotted


# Plot the magnitude spectrum
fig, ax = plt.subplots(1,2)

ax[0].plot(xf, 2.0/N * np.abs(yf[0:N//2]))
ax[0].grid()
plt.xlabel("Frequency [Hz]")
plt.ylabel("Amplitude")
plt.title("FFT of a Sine Wave")
ax[1].plot(x, yif)
ax[1].plot(x, y)

plt.show()