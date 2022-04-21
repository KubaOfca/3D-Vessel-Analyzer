import pydicom
from skimage.morphology import skeletonize
from cython_scripts.tree_from_skeleton_image import form_array_of_skeleton_make_spanning_trees
import os
import pandas as pd
import time
import image_manipulation as iman
import numpy as np

# Useful commends
# np.set_printoptions(threshold=sys.maxsize)

# global var
ROI = [(115, 1032), (169, 702)]


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

    folder = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\VesselsAnalyzer\DCM_database"

    for filename in os.listdir(folder):
        filename_path = os.path.join(folder, filename)
        if filename.endswith(".dcm") and os.path.isfile(filename_path):
            s_time = time.time()

            result_dict["FileName"].append(filename)
            dcm_image = pydicom.dcmread(filename_path)
            data = dcm_image.pixel_array[:, ROI[1][0]:ROI[1][1], ROI[0][0]:ROI[0][1]]
            iman.threshold(data)
            data = iman.make_RGB_image_binary(data)
            result_dict["Vessel-to-volume ratio"].append(iman.vr(data))
            data_skeleton = skeletonize(data, method='lee')
            # test
            test_array = np.zeros((3, 5, 6), dtype=np.uint8)
            test_array[1, 3, 0] = 1
            test_array[1, 3, 1] = 1
            test_array[1, 3, 2] = 1
            test_array[1, 3, 3] = 1
            test_array[1, 3, 4] = 1
            test_array[1, 2, 5] = 1
            test_array[1, 1, 4] = 1
            test_array[1, 1, 3] = 1
            test_array[1, 1, 2] = 1
            test_array[1, 2, 2] = 1

            trees, lv_feature, nb_feature, nc_feature = form_array_of_skeleton_make_spanning_trees(data_skeleton)
            nt_feature = len(trees)
            result_dict["length of vessels"].append(lv_feature)
            result_dict["number of branching"].append(nb_feature)
            result_dict["number of cycles"].append(nc_feature)
            result_dict["number of vascular trees"].append(nt_feature)

            time_exec = round(time.time() - s_time, 2)
            print(f'[Exec Time] {time_exec}')
            result_dict["Exec time"].append(time_exec)

    df = pd.DataFrame(data=result_dict)
    df.to_csv('result_form_mat.csv', index=False)


main()
