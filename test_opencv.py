import numpy as np
from scipy.fft import fft, fftfreq, ifft
from scipy.signal import hilbert

import matplotlib
matplotlib.use("tkagg")
from matplotlib import pyplot as plt
import cv2

image_path = "./img-24-5-190-l.jpg"
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
imgH ,imgW = img.shape

r = cv2.selectROI("select area", img)
cropped_img = img[int(r[1]):int(r[1]+r[3]), 
                    int(r[0]):int(r[0]+r[2])]
x_len = r[2]
y_len = r[3]

cv2.imshow('My Image', cropped_img)
cv2.waitKey()
cv2.destroyAllWindows()

img_sum = np.sum(cropped_img, axis=0)
img_avg = (img_sum - np.mean(img_sum))/y_len
wir = list(range(x_len)) # number of pixels along x axis, for plots

fft_x = fftfreq(x_len,1)
#fft_y = 2.0/x_len*np.abs(fft(img_avg)[:x_len//2])
fft_y = fft(img_avg)

crop = np.array([0 if (x < 0.07 or x > 0.2) else 1 for x in fft_x])
fft_y_crop = crop*fft_y

ifft_y = ifft(fft_y_crop)

anal_y = hilbert(np.real(ifft_y))
amp_env = np.abs(anal_y)
instant_phase = np.unwrap(np.angle(anal_y))


fig, axes = plt.subplots(1,5, figsize=(200, 200))

axes[0].plot(wir, img_avg, 'b--')
axes[1].plot(fft_x[:x_len//2], 2.0/x_len*np.abs(fft_y[:x_len//2]), 'b--')
axes[2].plot(fft_x[:x_len//2], 2.0/x_len*np.abs(fft_y_crop[:x_len//2]), 'b--')
axes[3].plot(wir, np.real(ifft_y), 'b--')
axes[4].plot(wir, instant_phase, 'b--')

#plt.xlabel("pixel number")
#plt.ylabel("sum of intensities")
#plt.title("Intensity Plot")

# Display the plot
plt.show()
