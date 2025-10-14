import numpy as np
import cv2

image_path = "./img-24-5-190-l.jpg"
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

r = cv2.selectROI("select area", img)
cropped_img = img[int(r[1]):int(r[1]+r[3]), 
                    int(r[0]):int(r[0]+r[2])]
x_len = r[2]
y_len = r[3]

cv2.imshow('My Image', cropped_img)
cv2.waitKey()
cv2.destroyAllWindows()

img_sum = np.sum(cropped_img, axis=0)
img_avg = (img_sum - np.mean(img_sum))

np.savetxt('signal.txt', img_avg, delimiter=' ')

