import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq, ifft
import matplotlib.pyplot as plt


## From Fourie coefficients we will restore the function
## with better resolution

def fourie_restore(coefs, T, fs, N, mode):
    # T - length of the initial signal
    # fs - discretization frequency
    # N - number of points to restore function in
    
    x = np.linspace(0, T, N)
    
    if mode == 'full':
        f = fftfreq(T, fs)
        y_map = map(lambda a: 1/T*np.sum(coefs*np.exp(2j*np.pi*f*a)), x)
    elif mode == 'cos':
        k = np.arange(T)
        y_map = map(lambda a: 1/T*np.sum(coefs*np.cos(np.pi/T*k*a)),x) 
    
    y = np.array(list(y_map))

    return x, y

## To get rid of all meaningless spectral components, we need bandpass filter

# butterworth bandpass filtr creation
# - finds Wn as width of probability dencity peak 
def my_butter(sig, fs=1, N=4, rel_h = 0.7, nperseg = 250):
    # fs -sampling frequency

    fxx, Pxx_den = signal.welch(np.real(sig), fs = fs, nperseg=nperseg)
    fxx_len = len(fxx)
    
    peak = np.argmax(Pxx_den)
    width = signal.peak_widths(Pxx_den,[peak], rel_height = rel_h)
    
    Wn = [width[2]*fs/2/(fxx_len-1), width[3]*fs/2/(fxx_len-1)]

    btype = 'bandpass'

    b, a  = signal.butter(N, Wn, btype, fs = fs)
    return b, a
    

# shit butterworth bandpass filtr creation
def my_butter_shit(fq0, fs=0.5, peak_count=3, N=4):

    if peak_count == 0:
        peak_count = 1
    Wn = [fq0*(peak_count), min(fq0*(peak_count)*2, fs/2.01)]
    #print(Wn)
    btype = 'bandpass'

    b, a  = signal.butter(N, Wn, btype, fs = fs)
    return b, a
    
# butterworth highpass filtr creation
# to cut off low frequences for better peak count
def my_butter_high(fq0, nl = 3, fs=1, N=4):
    f_cut = min(fq0*nl, fs/2.01)
    #print(f_cut)
    btype = 'highpass'

    b, a = signal.butter(N, f_cut, btype, fs=fs)
    return b, a


def phase_vel(ins_ph, dt):
    return np.mean(np.diff(ins_ph)/dt/2/np.pi)

def auto_corr(sig, sig_point_num, dt):
    # signal - signal to find autocorrelation of
    # sig_point_num - number of data points in signal
    
    sig_cor = signal.correlate(sig, sig, mode = 'full')
    sig_cor_lag = signal.correlation_lags(sig_point_num, sig_point_num,  mode = 'full')*dt

    return sig_cor_lag[sig_point_num:], sig_cor[sig_point_num:]/np.max(sig_cor)

def peak_counter(sig):
    # returns number of peaks in a signal and mean period
    peaks, _ = signal.find_peaks(sig)
    peak_count = len(peaks)
    mean_period = np.mean(np.diff(peaks))
    
    return peak_count, mean_period


# function applyes butterwort filter  using my_butter
# computes instant phase using hilbert transform
# plots filtered signal, instant phase and 
# in the third column displays the probability dencity distribution along with
# Wn for the filter and filter responce 
def plot_flt_res(sig_list, fs, rel_h, nperseg_c):

    img_count = len(sig_list)
    sig_len = len(sig_list[0])

    sig_x = np.arange(sig_len)/fs

    
    fig, ax = plt.subplots(img_count, 3, figsize=(12,4*img_count))
    i = 0

    ph_vel = []

    for sig_y in sig_list:


        fxx, Pxx_den = signal.welch(np.real(sig_y), fs = fs, nperseg=int(sig_len*nperseg_c)) # sampling frequency
        fxx_l = len(fxx)

        den_peak = np.argmax(Pxx_den)
        res = signal.peak_widths(Pxx_den, [den_peak], rel_height=rel_h)
        Wn = [res[2]*0.5*fs/fxx_l,res[3]*0.5*fs/fxx_l]
    
        b, a = my_butter(sig_y, N=4, fs=fs, rel_h=rel_h, nperseg=int(sig_len*nperseg_c))# sampling frequency
        w, h = signal.freqz(b, a, fs = fs)
        sig_flt = signal.filtfilt(b, a, sig_y, method='gust') 


        ax[i][0].plot(sig_x, sig_flt)


        anal_y = signal.hilbert(np.real(sig_flt))
        instant_phase = np.unwrap(np.angle(anal_y))
        #instant_phase = np.angle(anal_y)
        ph_vel.append(phase_vel(instant_phase[5:-5], dt = 1/fs))

        ax[i][1].plot(sig_x, instant_phase)
        ax[i][1].set_title(f" phase_vel: {ph_vel[i]}")

        ax[i][2].plot(fxx, Pxx_den/np.max(Pxx_den))
        ax[i][2].hlines(res[1]/np.max(Pxx_den), *Wn, color= 'C2')
        ax[i][2].plot(w, np.abs(h))
        ax[i][2].set_xlim(-0.01, 0.75)

        i = i+1

    return ph_vel

def analize_signal(sig, dt):
    # sig - original signal
    # dt - discritization step
    sig_len = len(sig)
    fs = 0.5/dt
    f0 = 1/sig_len

    # pass the signal through highpass filter to get rid of low frequences
    bh, ah = my_butter_high(fq0 = f0, nl=1, fs=fs)
    sig_flt_h = signal.filtfilt(bh, ah, sig)

    # compute autocorrelation dencity function
    _, sig_cor = auto_corr(sig_flt_h, sig_len, dt)

    # count the number of times correlation function has maximum - number of 
    # periods in the picture
    # we will assume (so far) that the peaks are distributed evenly
    peaks, _ = signal.find_peaks(sig_cor)
    peak_count = len(peaks)

    # use the bandpath butter filter with the number of peaks we found as parameter
    b, h = my_butter(fq0 = f0, fs=fs, peak_count=peak_count)
    sig_flt = signal.filtfilt(b, h, sig)

    # restore analitical signal from filtered signal
    # find instant phase and from it - phase velocity
    anal_y = signal.hilbert(np.real(sig_flt))
    instant_phase = np.unwrap(np.angle(anal_y))
    ph_vel = phase_vel(instant_phase, dt)

    return peak_count, ph_vel
