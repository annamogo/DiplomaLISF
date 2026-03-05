# chooses areas of given image and saves them to files .jpg

import numpy as np
import cv2
import json

class Select(Object):

    def __init__(self, img_path, win_name):
        self.img = cv2.imread(img_path)            
        self.img_line = []
        self.win_name = win_name

    def dump_to_json(self, json_path):
        
        

class SelectLine(Select):

    def __init__(self, img_path, win_name):
        super().__init__(img_path, win_name)

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


def choose_area(img_path, r = None):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    if not r:
        r = cv2.selectROI("select area", img)
        cv2.destroyAllWindows()
        
    cropped_img = img[int(r[1]):int(r[1]+r[3]), 
                    int(r[0]):int(r[0]+r[2])]

    img_sum = np.sum(cropped_img, axis=0)
    img_avg = (img_sum - np.mean(img_sum))

    return img_avg


def get_area_box(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    r = cv2.selectROI("select area", img)
    cv2.destroyAllWindows()
    
    return r


def choose_multy(img_path_list, json_path, mode = 'individual'):
    r = []
    
    with open(json_path, 'w') as f:
        f.write('[')

        if mode == 'common':
            r = get_area_box(img_path_list[1])
            
        for img_path in img_path_list:
            img_avg = choose_area(img_path, r)
            json.dump(list(img_avg), f)
            f.write(',')          

        f.write('[]]')
    

        
'''
def normal_lim(mean, std, llim, ulim):
    val = np.random.normal(mean, std)
    return int(np.clip(val, llim, ulim))


def img_bunch_gen(image_path, N, dx0_lim, dy0_lim, dxl_lim, dyl_lim):
    # N - necessary number of altered images 
    # dx0_lim, dy0_lim, dxl_lim, dyl_lim: tuples of variation limits or 0

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    #h, w = img.shape

    x0, y0, xl, yl = cv2.selectROI("select area", img)
    cropped_img = img[y0:y0+yl, x0:x0+xl]
    
    cv2.imshow('My Image', cropped_img)
    cv2.waitKey()
    cv2.destroyAllWindows()

 
    with open("averaged_imgs.txt", 'w') as f:
    
        f.write('[')
        
        # create random alteration to range
        # by moving point 0 and width|hight
        
        if dx0_lim:
            print('hi')#dx0 = [0] + list(np.random.randint(*(np.array(dx0_lim)*x0), N) + x0)
        else:
            dx0 = [x0]*(N+1)
        json.dump(dx0, f)
        f.write(', ')
            
        if dy0_lim:
            print('hi')#dy0 = [0] + list(np.random.randint(*(np.array(dy0_lim)*y0), N) + y0)
        else:
            dy0 = [y0]*(N+1)
        json.dump(dy0, f)
        f.write(', ')
            
        if dxl_lim:
            dxl = [xl] + [int(a) for a in np.random.randint(*(np.array(dxl_lim)*xl+xl), N)]
        else:
            dxl = [xl]*(N+1)
        json.dump(dxl, f)
        f.write(', ')
            
        if dyl_lim:
            print('hi')#dyl = list(np.random.randint(*(np.array(dyl_lim)*yl), N))
        else:
            dyl = [yl]*(N+1)
        json.dump(dyl, f)
        f.write(', ')

        
        f.write('[')
        for i in range(N+1):

            #print(f"zero-point ({x0+dx0}, {y0+dy0}) ; width/hight ({xl+dxl}, {yl+dyl})")
            
            new_cropped = img[dy0[i]:dy0[i]+dyl[i], dx0[i]:dx0[i]+dxl[i]]

            img_sum = np.sum(new_cropped, axis=0)
            img_avg = img_sum - np.mean(img_sum)


            json.dump(list(img_avg), f)
            if i != N:
                f.write(', ')
            
            cv2.imwrite("area_effect/"+str(i)+".jpg", new_cropped)
        
        f.write(']]')
    


#np.savetxt('signal.txt', img_avg, delimiter=' ')

'''