import numpy as np
from scipy import signal
from matplotlib.figure import Figure

class Data(object):
    def __init__(self, data = None):
        self.data = data

    def store(self, data):
        self.data = data

    def write(self, path):
        with open(path, w) as f:
            f.write(self.data)
            
    def read(self, path):
        pass
    


class DataFringe(Data):
    def __init__(self, data = None, resolution = 0, fs = 1):
        super(DataFringe, self).__init__(data)
        try:
            self.pcount = len(data)
        except:
            self.pcount = 0
            
        self.res = resolution
        self.fs = fs

    def store(self, data):
        self.data = data
        self.pcount = len(data)

    def set_fs(self, fs):
        self.fs = fs

    def get_phase_vel(self):
        dx = 1/self.fs
        
        anal_sig = signal.hilbert(np.real(self.data))
        instant_phase = np.unwrap(np.angle(anal_sig))
        phase_vel = np.mean(np.diff(instant_phase[5:-5])/dx/2/np.pi)

        return phase_vel



class DataFringeStack(object):
    def __init__(self, resolution = 0):
        self.sig_stack = []
        self.resolution = resolution
        self.sig_count = 0

    def __getitem__(self, key):
        return self.sig_stack[key]

    def __str__(self):
        _str = "\n".join([str(sig.data) for sig in self.sig_stack])
        return _str

    def __len__(self):
        return len(self.sig_stack)

    def set_fs(self, fs):
        for sig in self.sig_stack:
            sig.set_fs(fs)

    def get_phase_vel(self):
        phase_vel_stack = []
        
        for sig in self.sig_stack:
            phase_vel = sig.get_phase_vel()
            phase_vel_stack.append(phase_vel)

        return phase_vel_stack
            


    def from_array(self, data_list):
        self.sig_stack = []
        
        for data in data_list:
            data_obj = DataFringe(data)
            self.sig_stack.append(data_obj)
            
        self.sig_count = len(self.sig_stack)

    def append_obj(self, data_obj):
        self.sig_stack.append(data_obj)
        self.sig_count += 1

    def clear(self):
        self.sig_stack = []
        self.resolution = 0
        self.sig_count = 0

        
            
    
    
        
