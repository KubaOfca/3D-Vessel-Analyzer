import pydicom
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize_3d
from make_tree_from_skeleton import form_array_of_skeleton_make_spanning_trees
import os
import pandas as pd
from time import time

# Useful commends
# np.set_printoptions(threshold=sys.maxsize)


# global var
ROI = [(115, 1032), (169, 702)]


def vr(image):
    foreground = np.count_nonzero(image == 1)
    depth, height, width = image.shape
    return foreground/(depth*height*width)


def threshold(image):
    background = np.logical_and(image[:, :, :, 0] == image[:, :, :, 1], image[:, :, :, 1] == image[:, :, :, 2])
    image[background] = [0, 0, 0]
    image[np.logical_not(background)] = [1, 0, 0]


def make_RGB_image_binary(image):
    image = np.delete(image, np.s_[1:3], 3).squeeze()
    return image


def save_one_2D_binary_image(image, name):
    im = Image.fromarray(image * 255)
    im.save(f"{name}.png")


def save_series_2D_binary_image(image, basename):
    n = image.shape[0]
    for i in range(n):
        im = Image.fromarray(image[i], "RGB")
        im.save(f"{basename}{i}.png")


def main():
    result_dict = {
        "FileName": [],
        "Vessel-to-volume ratio": [],
        "number of vascular trees": [],
        "length of vessels": [],
        "number of branching": [],
        "number of cycles": [],
        "Exec time": [],
    }
    folder = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\dane_07.03.2022"
    for filename in os.listdir(folder):
        filename_path = os.path.join(folder, filename)
        if filename.endswith(".dcm") and os.path.isfile(filename_path):
            s_time = time()
            result_dict["FileName"].append(filename)
            dcm_image = pydicom.dcmread(filename_path)
            data = dcm_image.pixel_array[:, ROI[1][0]:ROI[1][1], ROI[0][0]:ROI[0][1]]
            threshold(data)
            data = make_RGB_image_binary(data)
            result_dict["Vessel-to-volume ratio"].append(vr(data))
            data_skeleton = skeletonize_3d(data)
            trees, lv_feature, nb_feature, nc_feature = form_array_of_skeleton_make_spanning_trees(data_skeleton)
            nt_feature = len(trees)
            result_dict["length of vessels"].append(lv_feature)
            result_dict["number of branching"].append(nb_feature)
            result_dict["number of cycles"].append(nc_feature)
            result_dict["number of vascular trees"].append(nt_feature)
            time_exec = round(time() - s_time, 2)
            print(f'[Exec Time] {time_exec}')
            result_dict["Exec time"].append(time_exec)
    df = pd.DataFrame(data=result_dict)
    df.to_csv('result2.csv', index=False)
    print("End")


main()
