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
    def __init__(self, data = None, resolution = 0):
        super(DataFringe, self).__init__()
        try:
            self.pcount = len(data)
        except:
            self.pcount = 0
            
        self.res = resolution

    def store(self, data):
        self.data = data
        self.pcount = len(data)



class DataFringeStack(object):
    def __init__(self, resolution = 0):
        self.sig_stack = []
        self.resolution = resolution
        self.sig_count = 0

    def __getitem__(self, key):
        return self.sig_stack[key]


    def from_flatten(self, data_list):
        self.sig_stack = []
        
        for data in data_list:
            data_obj = DataFringe(data)
            self.sig_stack.append(data_obj)

    def append_obj(self, data_obj):
        self.sig_stack.append(data_obj)

    def clear(self):
        self.sig_stack = []
        self.resolution = 0
        self.sig_count = 0

        
            
    
    
        
