import numpy as np
import matplotlib.pyplot as plt
import cv2
import copy

from process_hist import HistAvg

#
# create class, which holds functions from previous block and stores data they provide,
# with some additional functions
#
class DirectList:
    #self.dir_lists: list[Direct]
    #self.dir_imgs: list[np.ndarray]
    #self.angles: list[float]
    
    def __init__(self, angles: list) -> None:
        self.dir_lists = []
        self.dir_imgs = []
        self.angles = angles

    def process(self, img):
        for angle in self.angles:
            direction = Direct(angle)
            direction.get_direction(img)
            self.dir_lists.append(direction)

    def lines_to_img(self) -> list[np.ndarray]:
        for dir_list in self.dir_lists:
            self.dir_imgs.append(dir_list.lines_to_img())

    def show_imgs(self):
        n = len(self.angles)
        
        plt.figure(figsize=[13,2*n])

        for i, img in enumerate(self.dir_imgs):
            plt.subplot((n+2)//3,3,i+1)
            plt.imshow(img, cmap='gray', vmin=0, vmax=255)
            plt.title(f"angle: {self.angles[i]/np.pi}*pi")
            
        plt.show()
            

class Direct:
    def __init__(self, angle, img_shape = None):
        self.points = []
        self.lines = []
        self.angle = angle
        self.img_shape = img_shape

    def _get_line(self, img, x0) -> tuple:
        line = []
        points = []
    
        x_max = img.shape[0]-1
        y_max = img.shape[1]-1

        y = 0
        x = x0

        angle = abs(self.angle)

        if angle > np.pi/4:
     
            while y <= y_max and x <= x_max:
                y = int((x - x0)/np.tan(angle))
                if y <= y_max:
                    points.append([x,y])
                    line.append(int(img[x,y]))
                x = x + 1
        else:
    
            while y <= y_max and x <= x_max:
                x = int(y*np.tan(angle)) + x0
                if x <= x_max:
                    points.append([x,y])
                    line.append(int(img[x,y]))
                y = y + 1        
    
        return line, points

    def _get_lower_half(self, img: np.ndarray, diag: list, check_last: int, x_max: int) -> tuple[list[list[int]], list[list[int,int]]]:
    
        new_points = diag
        lines = []
        points = []
        
        for _ in range(x_max):
            ending = []
            for p in new_points[-check_last:]:
                if p[0] < x_max:
                    ending.append([p[0]+1,p[1]])
                    
            new_points = [[p[0]+1, p[1]] for p in new_points[:-check_last]]
            new_points += ending
    
            points.append(new_points)
    
            lines.append([img[*p] for p in new_points])
    
        return lines, points
    
    def _get_upper_half(self, img: np.ndarray, diag: list, check_last: int, y_max: int) -> tuple[list[list[int]], list[list[int,int]]]:
    
        new_points = diag
        lines = []
        points = []

        points.append(new_points)
        lines.append([img[*p] for p in new_points])
        
        for _ in range(y_max):
            ending = []
            for p in new_points[-check_last:]:
                if p[1] < y_max:
                    ending.append([p[0],p[1]+1])
                    
            new_points = [[p[0], p[1]+1] for p in new_points[:-check_last]]
            new_points += ending
    
            points.append(new_points)
    
            lines.append([img[*p] for p in new_points])
            
        lines.reverse()
        points.reverse()
    
        return lines, points

    def get_direction(self, img: np.ndarray) -> tuple[list[list[int]], list[list[int,int]]]:
        self.img_shape = img.shape

        lines = []
        points = []
    
        angle = abs(self.angle)

        if angle == 0:
            points = [[[y, x] for x in range(self.img_shape[1])] for y in range(self.img_shape[0])]
            lines = [img[y,:].tolist() for y in range(self.img_shape[0])]
        elif angle in [-np.pi/2, np.pi/2]:
            points = [[[y, x] for y in range(self.img_shape[0])] for x in range(self.img_shape[1])]
            lines = [img[:,x].tolist() for x in range(self.img_shape[1])]
        else:           
            if self.angle < 0:
                img = img[:,::-1]
            
    
            check_last_x = 1
            check_last_y = 1
            if angle < np.pi/4:
                check_last_x = int(1/np.tan(self.angle)) + 1
            else:
                check_last_y = int(np.tan(self.angle)) + 1
        
            x_max = img.shape[0]-1
            y_max = img.shape[1]-1
        
            _, diag = self._get_line(img, 0)
        
            lines_up, points_up = self._get_upper_half(img, diag, check_last_y, y_max)
            lines_down, points_down = self._get_lower_half(img, diag, check_last_x, x_max)
        
            lines = lines_up + lines_down
            points = points_up + points_down
    
            if self.angle < 0:
                points = [[[p[0],self.img_shape[1]-1-p[1]] for p in p_line] for p_line in points]

        self.points = points
        self.lines = lines
        
        return lines, points

    def filter_dir(self, L:int = 3):
        h_avg = HistAvg(L = L)
        
    
    def show(self) -> None:
        max_len = max(list(map(len, self.lines)))
    
        img = np.zeros((len(self.lines), max_len))
    
        for i, line in enumerate(self.lines):
            img[i,:len(line)] = line

        plt.figure()
        plt.imshow(img, cmap='gray', vmin=0, vmax=255)
        plt.show()

        return None

    def lines_to_img(self) -> np.ndarray:

        img = np.zeros(self.img_shape)
        for p, i in zip([p for line_points in self.points for p in line_points],[i for line in self.lines for i in line]):
            img[*p] = i

        return img


class DirLine:

    def __init__(self, angle: float, x0: int) -> None:
        self.angle = angle
        self.x0 = x0
        self.line = []
        self.points = []

    def get_line(self, img) -> tuple[list, list[list]]:
        line = []
        points = []
        
        x_max = img.shape[0]-1
        y_max = img.shape[1]-1
    
        y = 0
        x = self.x0
        alpha = self.angle
    
        if alpha > np.pi/4:
     
            while y <= y_max and x <= x_max:
                y = int((x - self.x0)/np.tan(alpha))
                if y <= y_max:
                    points.append([x,y])
                    line.append(int(img[x,y]))
                x = x + 1
        else:
    
            while y <= y_max and x <= x_max:
                x = int(y*np.tan(alpha)) + self.x0
                if x <= x_max:
                    points.append([x,y])
                    line.append(int(img[x,y]))
                y = y + 1 

        self.line = line
        self.points = points
    
        return line, points

    def draw_points(self, img) -> np.ndarray:
        img_out = copy.deepcopy(img)

        for point in self.points:
            try:
                img_p = img[*point]
            except IndexError:
                pass
            else:
                img_out[*point] = 0 if img_p > 120 else 255
    
        return img_out
    
    



        
        