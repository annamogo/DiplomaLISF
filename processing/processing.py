import numpy as np
from scipy import signal

from img_fringe.data_fringe import *

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt

from typing import Tuple

class Process(object):
    def __init__(self):
        pass

    def process(self):
        pass

    def process_stack(self, data: DataFringeStack) -> DataFringeStack:
        
        data_flt = []
        
        if not isinstance(data, DataFringeStack):
            raise TypeError("Stack given for processing\
                            is not an instance of DataFringeStack")

        DataFlt = DataFringeStack()
        
        for Sig in data:
            try:
                SigFlt = self.process(Sig)
            except:
                raise Exception
            
            DataFlt.append(SigFlt)

        DataFlt.set_resolution(data.resolution)

        return DataFlt


class  HighPass(Process):
    fs: float|int
    nl: int
    border: int
    method: str


    def __init__(self, fs = 1, nl = 2, border = 4, method = 'gust'):
        self.fs = fs # sampling frequency
        self.nl = nl # minimum number of peaks that can be present in the signal
        self.border = border # order of butter filter
        self.btype = 'highpass' # type of butter filter
        self.method = method # method of signal.filtfilt

    def process(self, Sig: DataFringe) -> DataFringe:
        SigFlt = Sig.copy()
        
        f_min = self.nl/Sig.pcount
        b, a = signal.butter(self.border, f_min, btype=self.btype, fs = self.fs)
        
        sig_flt = signal.filtfilt(b, a, Sig.data, method=self.method)
        SigFlt.store(sig_flt)
        
        return SigFlt




class BandPass(Process):
    fs: float|int
    border: int
    method: str
    rel_h: float|int
    nperseg_c: float|int
    
    def __init__(self, fs = 1, border = 4, method='gust', rel_h = 0.7, nperseg_c = 1):
        self.fs = fs  # fs -sampling frequency
        self.border = border
        self.btype = 'bandpass'
        self.method = method
        self.rel_h = rel_h
        self.nperseg_c = nperseg_c


    def plot_welch_peaks(self, sig: list[float]) -> Tuple[Line2D, Line2D]:

        sig_len = len(sig)
        fxx, Pxx_den = signal.welch(np.real(sig), fs = self.fs, nperseg=self.nperseg_c*sig_len)

        fxx_len = len(fxx)
        
        peak = np.argmax(Pxx_den)
        width = signal.peak_widths(Pxx_den,[peak], rel_height = self.rel_h)

        Wn = [width[2]*self.fs/2/(fxx_len-1), width[3]*self.fs/2/(fxx_len-1)]

        line1 = Line2D(fxx, Pxx_den/np.max(Pxx_den))
        line2 = Line2D(np.linspace(*Wn, 10), [width[1]/np.max(Pxx_den)]*10)
        

        return line1, line2
        

    def my_butter(self, sig: list[float]) -> Tuple[float, float]|None:
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
            
    def process(self, Sig: DataFringe) -> DataFringe:
        SigFlt = Sig.copy()
        
        b, a = self.my_butter(sig.data)
        
        sig_flt = signal.filtfilt(b, a, sig.data, method=self.method)
        SigFlt.store(sig_flt)
        
        return SigFlt


        

    
 
        
        
    
