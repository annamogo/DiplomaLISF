import numpy as np
import copy

from directions import Direct, DirectList


class HistAvg:

    def __init__(self, L=0):
        print(L)
        self.L = L
        self.g = self._g_linear()
    
    def _g_linear(self) -> list:
        L = self.L
        if L%2 == 0:
            g_first = [i for i in range(L//2)]
            a = L/2/sum(g_first)
            g_first = [a*i for i in g_first]
    
            g = g_first + g_first[::-1]
    
        else:
            g_first = [i for i in range(L//2 + 1)]
            g = g_first + g_first[L//2-1::-1]
            a = L/sum(g)
    
            g = [a*i for i in g]
            
        return g
    
    def _hist(self, points: list[int]) -> list:
        hist = [0]*256
    
        g_funk = self.g
        for p, g in zip(points, g_funk):
            hist[p] += g
    
        return hist
    
    def _average_hist_sample(self, points: list) -> float:
        histogramm = self._hist(points)
        hist_range = [i for i in range(255)]
        L = len(points)
    
        avr_cp = round(sum([i*h for i, h in zip(hist_range, histogramm)])/L)
        return avr_cp
    
    def process(self, line: list[list]) -> list[list]:
        L = self.L
        
        seq_len = len(line)
        if seq_len <= L:
            L = seq_len
        
        new_line = line[:L//2]
        
        for i in range(seq_len-L):
            points = line[i:i+L]
            p_new = self._average_hist_sample(points)
        
            new_line.append(p_new)
    
        new_line += line[-L//2:]
            
        return new_line


class HistAvgMulti(HistAvg):
    def __init__(self, L=0):
        super().__init__(L=L)


    def process(self, dir_lists: DirectList, inplace=True) -> [list[list], None]:

        if inplace:
            for dir_list in dir_lists.dir_lists:
                for line in dir_list.lines:
                    line = super().process(line)
                    
            return None
            
        else:
            new_dir_lists = DirectList(angles=dir_lists.angles)
            for dir_list in dir_lists.dir_lists:
                for line in dir_list.lines:
                    new_line = super().process(line)
                    new_dir_lists.dir_lists.append(new_line)
                    
            return new_dir_lists
                



























                    

        
    