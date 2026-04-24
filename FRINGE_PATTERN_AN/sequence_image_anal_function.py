import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq, irfft, dct, idct
import cv2
import os
import pathlib
import json
import matplotlib.pyplot as plt


import sig_analize as san
import generate_areas as ga


def get_imgs_paths(dir_paths):
    
    img_paths_list = []

    if isinstance(dir_paths, str):
        img_paths_list = [dir_paths + '/'+ f for f in os.listdir(dir_paths) if f.endswith('.jpg')]
        img_paths_list.sort()
    else:
        for dir_path in dir_paths:
            img_paths = [dir_path + '/'+ f for f in os.listdir(dir_path) if f.endswith('.jpg')]
            img_paths.sort()
            img_paths_list.append(img_paths)

    return img_paths_list


# creates 1-D arrays out of selected ROI for all images in
# "img_path_list" and writes them in json files, stored in "jsons_dir"
# ROI is selected for each sequence
# separate json file is created for each sequence if imgs
def create_json(
    json_path,
    img_paths
):
    json_dir = os.path.dirname(json_path)
    if json_dir:
        pathlib.Path(json_dir).mkdir(parents=True, exist_ok=True) 

    ga.choose_multy(img_paths, json_path, mode='common')
    

def create_many_jsons(jsons_dir, # premade directory, where data will be stored
                 img_paths_list
                ):
    if not os.path.exists(jsons_dir):
        os.makedirs(jsons_dir)
        
    for i, img_paths in enumerate(img_paths_list):
        json_path = jsons_dir+'sequence-'+str(i)+'.txt'

        ga.choose_multy(img_paths, json_path, mode='common')


def load_imgs_from_json(json_path, show=True):
    with open(json_path,'r') as f:
        imgs = json.load(f)[:-1]

    if show:
        img_count = len(imgs)
        row_count = (img_count+2)//3

        fig, ax = plt.subplots(row_count, 3, layout='constrained',figsize=(12, 4*row_count), sharex=False, sharey=False)

        for i in range(img_count):
            ax[i//3][i%3].plot(imgs[i])
            ax[i//3][i%3].set_title(f"\n Необработанный сигнал, \n t = {(i+6)*10} c")#номер: {i}")
            ax[i//3][i%3].set_xlabel("положение по оси X [px]")
            ax[i//3][i%3].set_ylabel("интенсивность")
            
    return imgs


# to make peaks more prominent it is nesessary to
# remove low frequencies from the signals
def filter_low_frq(sigs, 
                   nl = 2,       # number of lowerest frequencies filtered
                   fs = 1       # frequency of discretization of the signal
                  ):
    # we will use san.my_butter_high to create high pass filter
    sig_len = len(sigs[0])  # we chose areas of the same length for all pictures in the series from one run
    f_min = nl/sig_len

    border = 4
    
    bh, ah = signal.butter(border, f_min, btype = 'highpass', fs=fs)
    sig_h = [signal.filtfilt(bh, ah, sig, method='gust') for sig in sigs]

    return sig_h

# counts the number of peaks in autocorrelation function
# needed to roughly estimate the frequency of fringes

def count_peaks_of_autocorr(sig_h, 
                            show_corr = True):
    cor_res =  [san.auto_corr(sig, dt=1) for sig in sig_h]

    sig_count = len(cor_res)
    row_count = (sig_count+2)//3

    if show_corr:
        fig, ax = plt.subplots(row_count, 3, figsize=(12, row_count), sharex=True, sharey=True)
        for i in range(sig_count):
            ax[i//3][i%3].plot(*cor_res[i])
        plt.suptitle(f"Autocorrelation of sig_h, filtered from lowerest frequencies")
        plt.show()

    peak_count = [san.peak_counter(cor[1])[0] for cor in cor_res]
    return peak_count


# to make peaks more prominent it is nesessary to
# remove low frequencies from the signals
# we will use san.my_butter_high to create high pass filter
# !!! here we use nl = (number of peaks in autocorrelation function)-1

def filter_lowest_n_frq(sig_list, nl: list, fs=1, border=4, show_corr=True, show_flt_sig=True):
    sig_len = len(sig_list[0])
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
            ax[i//3][i%3].plot(*san.auto_corr(sig_hn[i], dt=1/fs))
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



# plots inverce phase velocity and fitted line
# returns slope and intercept of the fitted line
def plot_phase_vel(
    file_list,
    vel_labels
):
    prop_cycle = plt.rcParams['axes.prop_cycle']
    color = prop_cycle.by_key()['color']
    marker = ['+','s','^','*']
    
    
    phase_vel_line = []
    
    for file in file_list:
        time_f = []
        phase_vel_rev = []
            
        with open(file, 'r') as f:
            t0, ph0 = f.readline().strip().split(' ')
            time_f.append(int(t0))
            phase_vel_rev.append(0)
            for line in f:
                t, ph = line.strip().split(' ')
                time_f.append(int(t))
                phase_vel_rev.append(float(ph)-float(ph0))
        
        slope, intercept = np.polyfit(time_f, phase_vel_rev, 1)
        phase_vel_line.append([time_f, phase_vel_rev, np.array(time_f)*slope + intercept])

    plt.figure()
    for i, line in enumerate(phase_vel_line):
        plt.scatter(line[0], line[1], marker=marker[i], color=color[i], label=vel_labels[i])
        plt.plot(line[0], line[2], '--', color=color[i])
    plt.legend()
   #plt.title('Зависимость обратной скорости приращения фазы \n сигнала поперек интерференционных полос от времени.')
    plt.xlabel('t(сек)')
    plt.ylabel(r'$T_{инт}$ (пиксель)')
    plt.title('Зависимость периода интерференции \n от времени растекания капли \n при разных скоростях потока. ')
    plt.show()

    return slope, intercept

def get_friction(file_list, 
                #vel_list, 
                dynamic_visc,  # in kg/(m*c)
                wavelength=443, # in nm
                n_oil=1.4, 
                ins_ang=0, 
                px_res=27.8, # in px/mm
                show_graph=True):
    fric = []
    Koeff = 10**6*4*np.pi*dynamic_visc*np.sqrt(n_oil**2-np.sin(ins_ang))/wavelength/px_res

    for file in file_list:
            time_f = []
            phase_vel_rev = []
            
            with open(file, 'r') as f:
                for line in f:
                    t, ph = line.strip().split(' ')
                    time_f.append(int(t))
                    phase_vel_rev.append(float(ph))
        
            slope, intercept = np.polyfit(time_f, phase_vel_rev, 1)
            fric.append(slope*Koeff)

    return fric