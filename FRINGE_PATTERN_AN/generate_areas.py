# chooses areas of given image and saves them to files .jpg

import numpy as np
import cv2
import json
import os
import pathlib
from bresenham import bresenham

class Select(object):

    def __init__(self, img_path, win_name):
        self.img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)            
        self.img_line = []
        self.win_name = win_name

    def dump_to_json(self, json_path):
        pass

        

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

    def select_line_from_img(self):

        if not self.line_points:
            self.get_line_points()
            
        x = [point[0] for point in self.line_points]
        y = [point[1] for point in self.line_points]

        self.img_line = self.img[y, x]
        
        return self.img_line


class SelectLines():
    def __init__(self, dir_path, win_name='window'):
        self.dir_path = dir_path
        self.img_paths = get_imgs_paths(self.dir_path)
        self.line_points = []
        self.lines = []

    def get_line_points(self):
        select = SelectLine(self.img_paths[0])
        line_points = select.get_line_points()
        self.line_points = line_points
        return line_points

    def get_lines_from_imgs(self):
        for img_path in img_paths:
            select = SelectLine(img_path)
            select.set_line_points(self.line_points)
            line = select.select_line_from_img()
            self.lines.append(line)

        return self.lines
        


def get_imgs_paths(dir_path):
    img_paths = [dir_paths + '/'+ f for f in os.listdir(dir_paths) if f.endswith('.jpg')]
    img_paths.sort()
    return img_paths