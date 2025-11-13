import numpy as np
from scipy import signal
from img_fringe.data_fringe import *

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt

class Process(object):
    def __init__(self):
        pass

    def process(self):
        pass

    def process_stack(self, data: DataFringeStack):
        
        data_flt = []
        for sig in data:
            try:
                sig_flt = self.process(sig)
            except:
                raise Exception
            
            data_flt.append(sig_flt)

        return data_flt


class  HighPass(Process):
    def __init__(self, fs = 1, nl = 2, border = 4, method = 'gust'):
        self.fs = fs # sampling frequency
        self.nl = nl # minimum number of peaks that can be present in the signal
        self.border = border # order of butter filter
        self.btype = 'highpass' # type of butter filter
        self.method = method # method of signal.filtfilt

    def process(self, data: DataFringe):
        f_min = self.nl/data.pcount
        b, a = signal.butter(self.border, f_min, btype=self.btype, fs = self.fs)
        
        data_flt = signal.filtfilt(b, a, data.data, method=self.method)
        return data_flt




class BandPass(Process):
    def __init__(self, fs = 1, border = 4, method='gust', rel_h = 0.7, nperseg_c = 1):
        self.fs = fs  # fs -sampling frequency
        self.border = border
        self.btype = 'bandpass'
        self.method = method
        self.rel_h = rel_h
        self.nperseg_c = nperseg_c


    def plot_welch_peaks(self, sig):

        sig_len = len(sig)
        fxx, Pxx_den = signal.welch(np.real(sig), fs = self.fs, nperseg=self.nperseg_c*sig_len)

        fxx_len = len(fxx)
        
        peak = np.argmax(Pxx_den)
        width = signal.peak_widths(Pxx_den,[peak], rel_height = self.rel_h)

        Wn = [width[2]*self.fs/2/(fxx_len-1), width[3]*self.fs/2/(fxx_len-1)]

        line1 = Line2D(fxx, Pxx_den/np.max(Pxx_den))
        line2 = Line2D(np.linspace(*Wn, 10), [width[1]/np.max(Pxx_den)]*10)
        #line3 = Line2D(w, np.abs(h))
        

        return line1, line2
        

    def my_butter(self, sig):
        sig_len = len(sig)
    
        fxx, Pxx_den = signal.welch(np.real(sig), fs = self.fs, nperseg=self.nperseg_c*sig_len)
        fxx_len = len(fxx)
        
        peak = np.argmax(Pxx_den)
        width = signal.peak_widths(Pxx_den,[peak], rel_height = self.rel_h)
        
        Wn = [width[2]*self.fs/2/(fxx_len-1), width[3]*self.fs/2/(fxx_len-1)]

        try:           
            b, a  = signal.butter(self.border, Wn, self.btype, fs = self.fs)
            return b, a
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            return
            
    def process(self, data: DataFringe):
        b, a = self.my_butter(data.data)
        sig_flt = signal.filtfilt(b, a, data.data, method=self.method)
        return sig_flt


        

    
 
        
        
    
