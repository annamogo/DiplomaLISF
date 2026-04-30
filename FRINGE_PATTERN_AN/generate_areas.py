# chooses areas of given image and saves them to files .jpg

import numpy as np
import matplotlib.pyplot as plt

import cv2
import json
import os
import pathlib
from bresenham import bresenham

from fringe_class import Fringe, FringeList

class Select(object):

    def __init__(self, img_path, win_name):
        self.img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)            
        self.img_line = []
        self.line_len = 0
        self.win_name = win_name

    def select_roi(self):
        r = cv2.selectROI("select area", self.img)
        cv2.destroyAllWindows()
        
        return r


    def dump_to_json(self, json_path):
        pass
        
    @staticmethod
    def get_imgs_paths(dir_path):
        img_paths = [dir_path + '/'+ f for f in os.listdir(dir_path) if f.endswith('.jpg')]
        img_paths.sort()
        return img_paths


        

class SelectArea(Select):
    def __init__(self, img_path, win_name='window'):
        super().__init__(img_path, win_name)

        self.roi = []

    def select_roi(self):
        r = super().select_roi()
        
        self.roi = r
        return r

    def line_from_img(self, r=None):
        if r:
            pass
        elif self.roi:
            r = self.roi
        else:
            r = self.select_roi()

        cropped_img = img[int(r[1]):int(r[1]+r[3]), 
                    int(r[0]):int(r[0]+r[2])]
    
        img_sum = np.sum(cropped_img, axis=0)
        img_line = (img_sum - np.mean(img_sum))
        self.img_line = img_line

        return Fringe(sig=img_line, fs = 1)



class SelectRNDArea(Select):
    def __init__(self,img_path, num=0, win_name='window'):
        super().__init__(img_path, win_name)
        self.roi = super().select_roi()
        *_, self.w_min, self.h_min = super().select_roi()
        self.num = num

        self.roi_list = []

    def get_random_rois(self, num = 0):
        if num:
            pass
        elif self.num:
            num = self.num

        x00, y00, w_max, h_max = self.roi

        rng = np.random.default_rng()
        w_list = rng.choice(np.asarray(range(self.w_min, w_max)),size=num)
        h_list = rng.choice(np.asarray(range(self.h_min, h_max)),size=num)
        x0_list = np.asarray([rng.choice(range(x00, x00+w)) for w in w_list])
        y0_list = np.asarray([rng.choice(range(y00, y00+h)) for h in h_list])

        roi_list = np.stack((x0_list, y0_list, w_list, h_list),axis=1)
        self.roi_list = roi_list
        
        return roi_list
        

class SelectAreas(SelectArea):
    def __init__(self, dir_path, win_name="window"):
        self.dir_path = dir_path
        self.img_paths = self.get_imgs_paths(self.dir_path)
        self.lines = []
        self.lines_num = 0

    def get_lines_from_imgs(self):
        img_line_list = []
        
        select = SelectArea(self.img_paths[0])
        r = select.select_roi()

        for img_path in self.img_paths:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            cropped_img = img[int(r[1]):int(r[1]+r[3]), 
                    int(r[0]):int(r[0]+r[2])]
        
            img_sum = np.sum(cropped_img, axis=0)
            img_line = (img_sum - np.mean(img_sum))
            img_line_list.append(img_line)

        self.lines = img_line_list
        self.lines_num = len(self.lines)

        fringe_list = FringeList()
        fringe_list.fringe_list_from_lines(self.lines)
        
        return fringe_list
        



class SelectLine(Select):

    def __init__(self, img_path, win_name='window'):
        super().__init__(img_path, win_name='window')

        self.cur_img = self.img.copy()
        self.prev_img = self.img.copy()

        self.line_points = []
        self.points = []
        self.point_num = 0
        

    def select_line_event(self, event, x, y, flags, param):
        
        if event == cv2.EVENT_LBUTTONDOWN:
            
    
            if self.point_num < 2:
                
                if self.point_num == 0:
                    cv2.circle(self.cur_img, (x, y), 2, (255, 255, 255), -1)
                    cv2.circle(self.prev_img, (x, y), 2, (255, 255, 255), -1)
                    
                elif self.point_num == 1:
                    cv2.line(self.cur_img, self.points[0], (x, y), (255, 255, 255), 1)
                    
                    cv2.circle(self.cur_img, (x, y), 2, (255, 255, 255), -1)
                    
                self.point_num += 1
                self.points.append((x,y))
                
            print(f'{self.point_num}: {self.points}')


    def get_end_points(self):
        self.cur_img = self.img.copy()
        self.prev_img = self.img.copy()
        self.points = []
        self.point_num = 0
        
        cv2.namedWindow(self.win_name)
        cv2.setMouseCallback(self.win_name, self.select_line_event)

        while True:
            cv2.imshow(self.win_name, self.cur_img)
            
            key = cv2.waitKey(1) & 0xFF
            if key in [27, 13]:
                break
            elif key == 8:
                self.cur_img = self.prev_img
                self.prev_img = self.img.copy()
                if self.point_num > 0:
                    self.points.pop()
                    self.point_num -= 1
                    
                print(f'{self.point_num}: {self.points}')

        cv2.destroyAllWindows()

        return self.points

    def set_line_points(self, line_points):
        self.line_points = line_points

    def get_line_points(self):

        if self.point_num < 2:
            self.get_end_points()
            
        (x1, y1), (x2, y2) = self.points
        self.line_points = list(bresenham(x1, y1, x2, y2))
        
        return self.line_points

    def select_line_from_img(self, img=None):

        if not self.line_points:
            self.get_line_points()
            
        x = [point[0] for point in self.line_points]
        y = [point[1] for point in self.line_points]

        if img:
            line = img[x,y]
            line = line - np.mean(line)
            return Fringe(signal=line, fs=1)
        else: 
            line = self.img[y, x]
            self.img_line = line - np.mean(line)
            return Fringe(signal = self.img_line, fs=1)



class SelectLines():
    def __init__(self, dir_path, win_name='window'):
        self.dir_path = dir_path
        self.img_paths = self.get_imgs_paths(self.dir_path)
        self.line_points = []
        self.lines = []
        self.lines_num = 0

    def get_line_points(self):
        select = SelectLine(self.img_paths[0])
        line_points = select.get_line_points()
        self.line_points = line_points
        return line_points

    def get_lines_from_imgs(self, add=False):

        if not add:
            self.lines = []

        if not self.line_points:
            self.get_line_points
            
        for img_path in self.img_paths:

            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            
            x = [point[0] for point in self.line_points]
            y = [point[1] for point in self.line_points]

            line = img[x,y]
            line = line - np.mean(line)
            
            self.lines.append(line)

        self.lines_num = len(self.lines)

        fringe_list = FringeList()
        fringe_list.fringe_list_from_lines(self.lines)

        return fringe_list

    def plot(self, col_num=3):

        row_num = (self.lines_num - 1)//col_num + 1

        fig, ax = plt.subplots(row_num, col_num, layout='constrained', sharex=True, sharey=True)

        for i in range(self.lines_num):
            ax[i//col_num][i%col_num].plot(self.lines[i])
            ax[i//col_num][i%col_num].set_title(f'Number of image: {i}')
        







































    