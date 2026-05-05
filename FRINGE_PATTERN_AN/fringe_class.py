import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq, irfft, dct, idct
from scipy.optimize import curve_fit

import cv2
import os
import pathlib
import json
import matplotlib.pyplot as plt


import sig_analize as san
import generate_areas as ga



class Fringe():
    def __init__(self, signal=None, fs=1):
        self.sig = signal
        self.sig_len = len(self.sig)
        self.fs = fs               # frequency of discretization of the signal
        self.peak_count = 0
        self.Wn = []
        self.instant_frequency = 0
        self.frq_cos = 0
        self.popt_cos = []

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

    def count_peaks_of_autocorr(self, show = False):
        cor_res =  san.auto_corr(self.sig, dt=1/self.fs)

    
        if show:
            plt.figure()          
            plt.plot(*cor_res)
            plt.suptitle(f"Autocorrelation of signal")
            plt.show()
    
        peak_count = san.peak_counter(cor_res[1])[0]
        self.peak_count = peak_count
        return peak_count

# determins window Wn of notch butterworth filter
    def update_Wn(self, rel_h, nperseg_c=1, show=False):
        nperseg = int(self.sig_len*nperseg_c)
        
        f, P_den = signal.welch(np.real(self.sig), fs = self.fs, nperseg=nperseg)
        f_len = len(f)

        peak = np.argmax(P_den)
        width = signal.peak_widths(P_den, [peak], rel_height=rel_h)

        Wn = [width[2]*self.fs/2/(f_len-1), width[3]*self.fs/2/(f_len-1)]
        #print(Wn)
        self.Wn = Wn

        if show:
            plt.figure()
            plt.plot(f, P_den/np.max(P_den))
            plt.hlines(width[1]/np.max(P_den), *Wn, color= 'C2')
            #plt.plot(w, np.abs(h), '--')
            #plt.set_xlim(-0.01, 0.5)

        return Wn

    def get_Wn_filter(self, border):

        btype = 'bandpass'
        b, a = signal.butter(N=border, Wn = self.Wn, btype = btype, fs=self.fs)
        return b, a



    def filter_notch_Wn(self, border=4, updateWn=True, rel_h=0.5, nperseg_c=1, inplace=True):

        if updateWn or not self.Wn:
            self.update_Wn(rel_h=rel_h, nperseg_c=nperseg_c)

        btype = 'bandpass'
        
        b, a = self.get_Wn_filter(border)# sampling frequency
        #w, h = signal.freqz(b, a, fs = self.fs) # filter step responce
        sig_flt = signal.filtfilt(b, a, self.sig, method='gust')

        if inplace:     
            self.sig = sig_flt
            return 0
        return Fringe(sig_flt,self.fs)

    def filter(self, inplace=True, rel_h=0.5, nperseg_c=1):

        sig = self.filter_low_frq(nl=2, inplace=False)
        peak_num = sig.count_peaks_of_autocorr()
        print(peak_num)
        sig.filter_low_frq(nl=max(peak_num-1,1), inplace=True)
        sig.filter_notch_Wn(rel_h=rel_h, nperseg_c=nperseg_c)

        if inplace:
            self.sig = sig.sig
            return 0
            
        return sig
        

    
    def get_frq(self):

        sig = self.sig
    
        anal_y = signal.hilbert(np.real(sig))
        instant_phase = np.unwrap(np.angle(anal_y))
            #instant_phase = np.angle(anal_y)
        instant_fr = self.phase_vel(instant_phase[5:-5], dt = 1/self.fs)
        self.instant_frequency = instant_fr   
    
        return instant_fr

    def get_frq_cos(self, init_guess):

        dist = np.arange(self.sig_len)/self.fs
        popt, pcov = curve_fit(self.func, dist, self.sig, maxfev=3000, p0=init_guess)

        frq = popt[-1]
        self.frq_cos = frq
        self.popt_cos = popt
        return self.frq_cos, popt

    @staticmethod
    def func(x, a1, a2, a3, b1, c1, c2):
        return a1+a2*x+a3*x**2 + b1*np.cos(c1+c2*x)

    @staticmethod
    def phase_vel(ins_ph, dt):
        return np.mean(np.diff(ins_ph)/dt)




class FringeList(Fringe):
    def __init__(self, fringe_list = None):
        if fringe_list:
            self.fringe_list = fringe_list
        else:
            self.fringe_list = []
        self.list_len = len(self.fringe_list)
        self.frq_list = []
        self.frq_cos_list = []
        self.popt_cos_list = []

    def append(self, fringe: Fringe):
        self.fringe_list.append(fringe)
        self.list_len += 1

    def plot(self, col_num=3, show_cos=False):

        row_num = (self.list_len - 1)//col_num + 1

        fig, ax = plt.subplots(row_num, col_num, layout='constrained', sharex=True, sharey=True)


        for i in range(self.list_len):
            ax[i//col_num][i%col_num].plot(self.fringe_list[i].sig)

        for i in range(self.list_len):
            ax[i//col_num][i%col_num].set_title(f'Number of image: {i}')

        if show_cos:
            x_list = np.linspace(0,self.fringe_list[0].sig_len,200)
            cos_interpol_list = [self.func(x_list, *popt) for popt in self.popt_cos_list]

            for i in range(self.list_len):
                ax[i//col_num][i%col_num].plot(x_list, cos_interpol_list[i])


    def fringe_list_from_lines(self, line_list):

        for line in line_list:
            self.fringe_list.append(Fringe(signal=line, fs=1))
            self.list_len = len(self.fringe_list)

    def filter_low_frq(self,       
                       nl,      # number of lowerest frequencies filtered 
                       inplace=True
                      ):
        
        ll = self.list_len
        if isinstance(nl, list):
            nl_list = [nl[-1]]*ll
            nl_list[:min(ll, len(nl))] = nl[:min(ll, len(nl))]
        elif isinstance(nl, int):
            nl_list = [nl]*ll
            
                
        # we will use san.my_butter_high to create high pass filter
        if inplace:
            for fringe, nl_fr in zip(self.fringe_list, nl_list):
                fringe.filter_low_frq(nl=nl_fr, inplace=True)
        else:
            new_fringe_list = FringeList()
            
            for fringe, nl_fr in zip(self.fringe_list, nl_list):
                new_fringe = fringe.filter_low_frq(nl=nl_fr, inplace=False)
                new_fringe_list.append(new_fringe) 

            return new_fringe_list


# counts the number of peaks in autocorrelation function
# needed to roughly estimate the frequency of fringes

    def count_peaks_of_autocorr(self, show=False):
        peak_count_list = []
        
        for fringe in self.fringe_list:
            peak_count =  fringe.count_peaks_of_autocorr(show=show)
            peak_count_list.append(peak_count)

        return peak_count_list

    
# filter the signals with notch butterworth filter
    def filter_notch_Wn(self, border=4,  updateWn=True, rel_h=0.5, nperseg_c=1, inplace=True):
        if inplace:
            for fringe in self.fringe_list:
                fringe.filter_notch_Wn(border=border, updateWn=updateWn, rel_h=rel_h, nperseg_c=nperseg_c, inplace=True)
        else:
            new_fringe_list = FringeList()
            
            for fringe in self.fringe_list:
                new_fringe = fringe.filter_notch_Wn(border=border, updateWn=updateWn, rel_h=rel_h, nperseg_c=nperseg_c, inplace=False)
                new_fringe_list.append(new_fringe)

            return new_fringe_list

    def filter(self, inplace=True, rel_h=0.5, nperseg_c=1):
        new_fringe_list = []
        for fringe in self.fringe_list:
            new_fringe = fringe.filter(inplace=False, rel_h=rel_h, nperseg_c=nperseg_c)
            new_fringe_list.append(new_fringe)

        if inplace:
            self.fringe_list = new_fringe_list
            return 0
            
        return FringeList(new_fringe_list)


    def get_frq(self, prefilter=True, rel_h = 0.5, nperseg_c=1):
        frq_list = []
        if prefilter:
            for fringe in self.fringe_list:
                tmp_fringe = fringe.filter(inplace=False, rel_h=rel_h, nperseg_c=nperseg_c)
                frq_list.append(tmp_fringe.get_frq())
        else:
            for fringe in self.fringe_list:
                frq_list.append(fringe.get_frq())
        self.frq_list = frq_list
        return self.frq_list

    def get_frq_cos(self, init_guess_w):
        frq_cos_list = []
        popt_cos_list = []
        for fringe, w0 in zip(self.fringe_list, init_guess_w):
            frq, popt = fringe.get_frq_cos(init_guess=[0,0,0,1,0,w0])
            frq_cos_list.append(frq)
            popt_cos_list.append(popt)
        self.frq_cos_list = frq_cos_list
        self.popt_cos_list = popt_cos_list
        return self.frq_cos_list
        



# to make peaks more prominent it is nesessary to
# remove low frequencies from the signals
# we will use san.my_butter_high to create high pass filter
# !!! here we use nl = (number of peaks in autocorrelation function)-1

