import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq, irfft, dct, idct
import cv2
import os
import json
import matplotlib.pyplot as plt


import sig_analize as san
import generate_areas as ga


def get_imgs_paths(dir_paths_list):
    
    img_paths_list = []
    
    for dir_path in dir_paths_list:
        img_paths = [dir_path + '/'+ f for f in os.listdir(dir_path) if f.endswith('.jpg')]
        img_paths.sort()
        img_paths_list.append(img_paths)

    return img_paths_list


# creates 1-D arrays out of selected ROI for all images in
# "img_path_list" and writes them in json files, stored in "jsons_dir"
# ROI is selected for each sequence
# separate json file is created for each sequence if imgs

def create_jsons(jsons_dir, # premade directory, where data will be stored
                 img_paths_list
                ):

    for i, img_paths in enumerate(img_paths_list):
        json_path = jsons_dir+'sequence-'+str(i)+'.txt'

        ga.choose_multy(img_paths, json_path, mode='common')


def load_imgs_from_json(json_path):
    with open(json_path,'r') as f:
        imgs = json.load(f)[:-1]
    return imgs


# to make peaks more prominent it is nesessary to
# remove low frequencies from the signals
def filter_low_frq(imgs, 
                   sig_len,  # we chose areas of the same length for all pictures in the series from one run
                   nl = 2,       # number of lowerest frequencies filtered
                   fs = 1       # frequency of discretization of the signal
                  ):
    # we will use san.my_butter_high to create high pass filter
    
    f_min = nl/sig_len
    border = 4
    
    bh, ah = signal.butter(border, f_min, btype = 'highpass', fs=fs)
    sig_h = [signal.filtfilt(bh, ah, img, method='gust') for img in imgs]

    return sig_h

# counts the number of peaks in autocorrelation function
# needed to roughly estimate the frequency of fringes

def count_peaks_of_autocorr(sig_h, sig_len, show_corr = True):
    cor_res =  [san.auto_corr(sig, sig_len, dt=1) for sig in sig_h]

    if show_corr:
        fig, ax = plt.subplots(row_count, 3, figsize=(12, row_count), sharex=True, sharey=True)
        for i in range(img_count):
            ax[i//3][i%3].plot(*cor_res[i])
        plt.suptitle(f"Autocorrelation of sig_h, filtered from {nl} lowerest frequencies")
        plt.show()

    peak_count = [san.peak_counter(cor[1])[0] for cor in cor_res]
    return peak_count


# to make peaks more prominent it is nesessary to
# remove low frequencies from the signals
# we will use san.my_butter_high to create high pass filter
# !!! here we use nl = (number of peaks in autocorrelation function)-1

def filter_lowest_n_frq(sig_list, sig_len, nl: list, fs=1, border=4, show_corr=True, show_flt_sig=True):
    f_min_list = np.array(nl)/sig_len

    sig_hn = []
    for sig, f_min in zip(sig_list, f_min_list):
            bh, ah = signal.butter(border, f_min, btype = 'highpass', fs=fs)
            sig_hn.append(signal.filtfilt(bh, ah, sig, method='gust'))

    # autocorrelation graph
    if show_corr:
        sig_count = len(sig_list)
        row_count = (sig_count+2)//3
        
        fig, ax = plt.subplots(row_count, 3, figsize=(12, row_count), sharex=True, sharey=True)
        for i in range(sig_count):
            ax[i//3][i%3].plot(*san.auto_corr(sig_hn[i], sig_len, dt=1/fs))
        plt.suptitle("Autocorrelation of signal, filtered from all frequencies,\n\
                        lower than what is corresponding to the number of peaks found in the signal")
        plt.tight_layout()
        plt.show()

    # filtered signal graph
    if show_flt_sig:
        sig_count = len(sig_list)
        row_count = (sig_count+2)//3
        
        sig_x = np.arange(sig_len)

        fig, ax = plt.subplots(row_count, 3, figsize=(12, row_count), sharex=True, sharey=True)
        for i in range(sig_count):
            ax[i//3][i%3].plot(sig_x, sig_hn[i])
        plt.suptitle("Filtered signal sig_hn")
        plt.tight_layout()
        plt.show()
        
    return sig_hn


def write_inv_phase(file_name, ph_vel_hn, delta_t, show_graph = True):
    time = np.arange(len(ph_vel_hn))*delta_t

    with open(file_name,'w') as f:
        for t, val in zip(time, 1/np.array(ph_vel_hn)):
            f.write(f"{t} {val:.3f}\n")

    if show_graph:
        slope, intercept = np.polyfit(time, 1/np.array(ph_vel_hn), 1)
        phase_vel_line = time*slope + intercept
        
        plt.figure()
        plt.plot(time, 1/np.array(ph_vel_hn), 'o')
        plt.plot(time, phase_vel_line, '--')
        print(slope)