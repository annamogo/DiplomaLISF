# chooses areas of given image and saves them to files .jpg

import numpy as np
import cv2
import json

def choose_area(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    r = cv2.selectROI("select area", img)
    cropped_img = img[int(r[1]):int(r[1]+r[3]), 
                    int(r[0]):int(r[0]+r[2])]

    cv2.destroyAllWindows()

    img_sum = np.sum(cropped_img, axis=0)
    img_avg = (img_sum - np.mean(img_sum))

    return img_avg


def get_area_box(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    r = cv2.selectROI("select area", img)
    cv2.destroyAllWindows()
    
    return r
    

def choose_multy(img_path_list, json_path, mode = 'individual'):

    with open(json_path, 'w') as f:
        f.write('[')

        if mode == 'individual':
            for img_path in img_path_list:
                img = choose_area(img_path)
                json.dump(list(img), f)
                f.write(',')
        elif mode == 'common':
            r = get_area_box(img_path_list[0])
            for img_path in img_path_list:
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                img_cropped = img[int(r[1]):int(r[1]+r[3]), 
                                int(r[0]):int(r[0]+r[2])]

                img_sum = np.sum(img_cropped, axis=0)
                img_avg = (img_sum - np.mean(img_sum))
                json.dump(list(img_avg), f)
                f.write(',')
                

        f.write('[]]')
        
        

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