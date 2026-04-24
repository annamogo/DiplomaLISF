import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq, irfft, dct, idct
import cv2
import os
import pathlib
import json
import matplotlib.pyplot as plt


import sig_analize as san
import generate_areas as ga



class FringeList(Fringe):
    def __init__(self, fringe_list = None):
        if fringe_list:
            self.fringe_list = fringe_list
        else:
            self.fringe_list = []
        self.list_len = len(self.sig_list)

    def


class Fringe():
    def __init__(self, signal=None, fs=1):
        self.sig = signal
        self.sig_len = len(self.sig)
        self.fs = fs               # frequency of discretization of the signal
        self.peak_count = 0
        self.Wn = []
        self.instant_frequency = 0

    def plot(self):
        plt.figure()
        plt.plot(self.sig)
        plt.show()

        
# to make peaks more prominent it is nesessary to
# remove low frequencies from the signals
    def filter_low_frq(self,       
                       nl,      # number of lowerest frequencies filtered 
                       inplace=True
                      ):
        # we will use san.my_butter_high to create high pass filter
        f_min = nl/self.sig_len
    
        border = 4
        
        bh, ah = signal.butter(border, f_min, btype = 'highpass', fs=self.fs)
        sig_h = signal.filtfilt(bh, ah, self.sig, method='gust')

        if inplace:
            self.sig = sig_h
            return 0
        
        return Fringe(signal=sig_h, fs=self.fs)

# counts the number of peaks in autocorrelation function
# needed to roughly estimate the frequency of fringes

    def count_peaks_of_autocorr(self, show_corr = False):
        cor_res =  san.auto_corr(self.sig, dt=1/self.fs)

    
        if show_corr:
            plt.figure()          
            plt.plot(*cor_res[i])
            plt.suptitle(f"Autocorrelation of signal")
            plt.show()
    
        peak_count = san.peak_counter(cor_res[1])[0]
        self.peak_count = peak_count
        return peak_count

# determins window Wn of notch butterworth filter
    def update_Wn(self, rel_h, nperseg_c=1):
        nperseg = int(self.sig_len*nperseg_c)
        
        f, P_den = signal.welch(np.real(self.sig), fs = self.fs, nperseg=nperseg)
        f_len = len(f)

        peak = np.argmax(P_den)
        width = signal.peak_widths(P_den, [peak], rel_height=rel_h)

        Wn = [width[2]*self.fs/2/(f_len-1), width[3]*self.fs/2/(f_len-1)]
        self.Wn = Wn

        return Wn

    def get_Wn_filter(self, border):

        btype = 'bandpass'
        b, a = signal.butter(N=border, Wn = self.Wn, btype = btype, fs=self.fs)
        return b, a



    def filter_notch_Wn(self, border=4, inplace=True):

        btype = 'bandpass'
        
        b, a = self.get_Wn_filter(border)# sampling frequency
        #w, h = signal.freqz(b, a, fs = self.fs) # filter step responce
        sig_flt = signal.filtfilt(b, a, self.sig, method='gust')

        if inplace:     
            self.sig = sig_flt
            return 0
        return Fringe(sig_flt,self.fs)

    
    def get_frq(self):
    
        anal_y = signal.hilbert(np.real(self.sig))
        instant_phase = np.unwrap(np.angle(anal_y))
            #instant_phase = np.angle(anal_y)
        instant_fr = self.phase_vel(instant_phase[5:-5], dt = 1/self.fs)
        self.instant_frequency = instant_fr
    
    
        return instant_fr

    @staticmethod
    def phase_vel(ins_ph, dt):
        return np.mean(np.diff(ins_ph)/dt)


# to make peaks more prominent it is nesessary to
# remove low frequencies from the signals
# we will use san.my_butter_high to create high pass filter
# !!! here we use nl = (number of peaks in autocorrelation function)-1

