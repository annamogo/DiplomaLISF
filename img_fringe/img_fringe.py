import numpy as np
from copy import deepcopy
import cv2
import os

from .data_fringe import *

from typing import Tuple

class Img(object):
    def __init__(self, img = None):
        self._validate_img(img)
        self.img = img
        
    def _validate_img(self, img):
        if not isinstance(img, np.ndarray) and img is not None:
            raise ValueError("img must be 2D numpy array")

    def store(self, img):
        self._validate_img(img)
        self.img = img

    def write(self, path):
        cv2.imwrite(path, self.img)

    def read(self, path):
        img = None
        
        try:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        except:
            raise Exception("Failed to read image from given path.")

        if img is None:
            raise Exception("The result of read is empty.")
       
        self.img = img
            

    def show(self):
        cv2.imshow('image window', self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()




class ImgFringe(Img):
    def __init__(self, img = None, resolution = 1):
        super().__init__(img)
        
        self._validate_resolution(resolution)

        self.resolution = resolution

    def _validate_resolution(self, resolution):
        err_text = "resolution must be positive float or integer"
        try: 
            resolution = float(resolution)
            if resolution <= 0 :
                raise ValueError(err_text)
            
        except ValueError as e:
            print(f"{e}: {err_text}")
            

    def set_resolution(self, resolution: float|int) -> None:
        
        self._validate_resolution(resolution)
        self.resolution = resolution
        

    def copy(self) -> 'ImgFringe':
        return deepcopy(self)

    def choose_area(self) -> Tuple[int,int,int,int]:
        
        if self.img is None:
            raise Exception("No image is stored in the Img object")
        else:
            try:
                r = cv2.selectROI("select area", self.img)
            except:
                cv2.destroyAllWindows()
                raise Exception("Could not sucsessfully select area")
            
            else:
                cv2.destroyAllWindows()
                
                return r

    def crop(self, r = None) -> None:

        if r is None:
            r = self.choose_area()
       
        cropped_img = self.img[int(r[1]):int(r[1]+r[3]), 
        int(r[0]):int(r[0]+r[2])]
               
        self.img = cropped_img


    def flatten(self) -> np.ndarray:
        img_sum = np.sum(self.img, axis=0)
        avg = (img_sum - np.mean(img_sum))

        return avg

    def create_data(self) -> DataFringe:
        Sig = DataFringe()
        Sig.store(self.flatten())
        Sig.set_res(self.resolution)

        return Sig






class ImgFringeStack(object):
    resolution: float|int
    
    def __init__(self, resolution = 1):
        self.img_stack = []
        self.img_count = 0
        if resolution:
            self.resolution = resolution
        else:
            self.resolution = 1

    def __getitem__(self, key) -> ImgFringe:
        return self.img_stack[key]

    def __len__(self) -> int:
        return self.img_count

        

    def read(self, path: str) -> None:
        img_path_list = [path + '/'+ f for f in os.listdir(path)
                         if f.endswith('.jpg')]
        img_path_list.sort()

        for img_path in img_path_list:
            img = ImgFringe()
            img.read(img_path)
            self.img_stack.append(img)
            self.img_count += 1

    def append_img(self, img) -> None:
        img_obj = ImgFringe()
        img_obj.store(img)
        self.img_stack.append(img_obj)

    def append(self, obj: ImgFringe) -> None:
        self.img_stack.append(obj)

    def clear(self) -> None:
        self.img_stack = []
        self.img_count = 0
        self.resolution = 0

    def set_resolution(self, resolution, mode='all', number=None
                       ) -> None:
        if mode == 'all':
            self.resolution = resolution
            for Img in self.img_stack:
                Img.set_resolution(resolution)
        elif mode=='one':
            try:
                self.img_stack[number].set_resolution(resolution)
            except IndexError:
                raise Exception("Could not define resolution, index is \
                                not given or out of bounds")
        

    def crop(self, n = 0, mode ='common', inplace=True
             ) -> 'ImgFringeStack':
        
        # mode can be 'individual' or 'common'
        if mode == 'common':
            rl = [self.img_stack[n].choose_area()]*self.img_count
        elif mode == 'individual':
            rl = [img.choose_area() for img in self.img_stack]

        if inplace:
            for img, r in zip(self.img_stack, rl):
                img.store(img.img[int(r[1]):int(r[1]+r[3]), 
                        int(r[0]):int(r[0]+r[2])])
        else:
            cropped = ImgFringeStack()
            
            for img, r in zip(self.img_stack, rl):
                img_cropped = img.img[int(r[1]):int(r[1]+r[3]), 
                        int(r[0]):int(r[0]+r[2])]

                cropped.append_img(img_cropped)

            cropped.set_resolution(resolution = self.resolution)
                
            return cropped

    def show(self) -> None:
        for Img in self.img_stack:
            cv2.imshow("Image Win", Img.img)
            cv2.waitKey(0)
        cv2.destroyAllWindows()
            

    def flatten(self) -> np.ndarray:
        data = []
        for Img in self.img_stack:
            data.append(Img.flatten())

        return data

    def create_data_stack(self) -> 'DataFringeStack':
        Data = DataFringeStack(self.resolution)

        for Img in self.img_stack:
            Sig = Img.create_data()
            Data.append(Sig)
        
        return Data
            
 
