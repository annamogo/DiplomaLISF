import numpy as np
from directions import Direct


class DispCoeff:
    # L - number of points we take to calculate dispertion (odd integer, filtering interval along lines) 
    # M - side of the squere over which avaraging of coefficients takes place
    
    def __init__(self, L:int, M:int = 0) -> None:
        self.L = L
        self.M = M
        self.d_arr = np.empty(shape=0)
        self.c_arr = np.empty(shape=0)
    
    
    def _dispersion(self, points_xi: list) -> float:
        points_xi = [int(p) for p in points_xi]
        L = len(points_xi)
        xi_aver = sum(points_xi)/L
        
        D = sum([(xi_p - xi_aver)**2 for xi_p in points_xi])/L/L
        return D
    
    def line_dispertion(self, line_xi: list) -> list:
        d_list = []
       
        p_count = len(line_xi)
        L = self.L
        for i in range(p_count):
    
            if i<L//2:
                points = line_xi[0:2*i+1]
            elif i > p_count-1-L//2:
                i_ = p_count-1-i
                points = line_xi[p_count-1-2*i_:p_count]
            else:
                points = line_xi[i-L//2:i+L//2+1]
                    
            d_list.append(self._dispersion(points))
    
        return d_list
    
    
        
    def line_list_dispertion(self, dir_lines: Direct) -> np.ndarray:
        d_2d_list = []
        L = self.L
        
        for line_xi in dir_lines.lines:
            d_list = self.line_dispertion(line_xi)
            d_2d_list.append(d_list)
    
        D_arr = np.zeros(dir_lines.img_shape)
        for p, D in zip([p for line_points in dir_lines.points for p in line_points],[D for d_line in d_2d_list for D in d_line]):
            D_arr[*p] = D
    
        self.d_arr = D_arr
        
        return D_arr
    
    def avg_line_list_dispertion(self, dir_lines: Direct = None) -> np.ndarray:
        M = self.M
        
        if self.d_arr.size == 0:
            try:
                self.line_list_dispertion(dir_lines)
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error occured: {e},/n possibly did not count d_arr beforehand and didn't provide direction lines array")
                
        
        Y = self.d_arr.shape[0]
        X = self.d_arr.shape[1]
        Y_ext = Y+M-1
        X_ext = X+M-1
        
        d_arr_ext = np.zeros((Y_ext, X_ext))
        d_arr_ext[M//2:-M//2+1,M//2:-M//2+1] = self.d_arr
    
        dim = max(X,Y)
        dim_ext = dim+M-1
        mask, tr_mask = self._avg_mask(arr_dim=(Y,X))
    
        c_arr = tr_mask@d_arr_ext@mask/M/M
        
        self.c_arr = c_arr
    
        return c_arr
    
    def _avg_mask(self, arr_dim: tuple) -> tuple[np.ndarray, np.ndarray]:
        M = self.M
        
        dim = max(arr_dim)
        dim_ext = dim+M-1
    
        mask = np.zeros((dim_ext, dim))
        for i in range(dim):
            for l in range(M):
                mask[i+l,i] = 1
    
        if arr_dim[0] <= arr_dim[1]:
            tr_mask = mask.T[:arr_dim[0],:arr_dim[0]+M-1]
        else:
            tr_mask = mask.T
            mask = mask[:arr_dim[1]+M-1,:arr_dim[1]]
    
        return mask, tr_mask