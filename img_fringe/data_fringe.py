import numpy as np
from copy import deepcopy
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
    data: list[float]|None
    resolution: float|int

    
    def __init__(self, data = None, resolution = 1):
        super(DataFringe, self).__init__(data)
        try:
            self.pcount = len(data)
        except:
            self.pcount = 0
            
        self.res = resolution
        try:
            self.fs = 1/self.res # sampling frequency in pixels is always 1
        except:
            self.fs = 1

    def copy(self) -> 'DataFringe':
        return deepcopy(self)

    def store(self, data: list[float]) -> None:
        self.data = data
        self.pcount = len(data)

    def set_res(self, resolution: float|int) -> None:
        try:
            self.res = resolution
            self.fs = 1/self.res
        except ZeroDivisionError:
            print("resolution must be greater then 0")
        except TypeError:
            print("resolution must be float or int")
        
        

    def get_phase_vel(self) -> float:
        dx = self.fs
        
        anal_sig = signal.hilbert(np.real(self.data))
        instant_phase = np.unwrap(np.angle(anal_sig))
        phase_vel = np.mean(np.diff(instant_phase[5:-5])/dx/2/np.pi)

        return phase_vel



class DataFringeStack(object):
    resolution: float|int

    
    def __init__(self, resolution = 1):
        self.sig_stack = [] # [DataFringe]
        self.resolution = resolution
        self.sig_count = 0

    def __getitem__(self, key: int) -> DataFringe:
        return self.sig_stack[key]

    def __str__(self) -> str:
        _str = "\n".join([str(sig.data) for sig in self.sig_stack])
        return _str

    def __len__(self) -> int:
        return self.sig_count

    def set_resolution(self, resolution: float|int) -> None:
        self.resolution = resolution
        for sig in self.sig_stack:
            sig.set_res(resolution)

    def copy(self) -> 'DataFringeStack':
        return deepcopy(self)


    def get_phase_vel(self) -> list[float]:
        phase_vel_stack = []
        
        for sig in self.sig_stack:
            phase_vel = sig.get_phase_vel()
            phase_vel_stack.append(phase_vel)

        return phase_vel_stack
            

    def from_array(self, data_list: list[list[float]]) -> None:
        self.sig_stack = []
        
        for data in data_list:
            data_obj = DataFringe(data)
            self.sig_stack.append(data_obj)
            
        self.sig_count = len(self.sig_stack)

    def append(self, data_obj: DataFringe) -> None:
        self.sig_stack.append(data_obj)
        self.sig_count += 1

    def clear(self) -> None:
        self.sig_stack = []
        self.resolution = 0
        self.sig_count = 0

        
            
    
    
        
