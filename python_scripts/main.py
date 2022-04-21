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

    folder = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\dane_07.03.2022"

    for filename in os.listdir(folder):
        file_full_path = os.path.join(folder, filename)
        if filename.endswith(".dcm") and os.path.isfile(file_full_path):
            s_time = time.time()

            result_dict["FileName"].append(filename)
            dcm_image = pydicom.dcmread(file_full_path)
            dcm_as_array = dcm_image.pixel_array[:, ROI[1][0]:ROI[1][1], ROI[0][0]:ROI[0][1]]
            iman.threshold(dcm_as_array)
            dcm_as_array = iman.make_RGB_image_binary(dcm_as_array)
            result_dict["Vessel-to-volume ratio"].append(iman.vr(dcm_as_array))
            data_skeleton = skeletonize(dcm_as_array, method='lee')

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
            # test_array = skeletonize(test_array, method='lee')
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
    try:
        df.to_csv(r'C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\VesselsAnalyzer\results\Wyniki2.csv',
                  index=False)
        df.to_excel(r'C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\VesselsAnalyzer\results\Wyniki2.csv',
                    index=False)
    except:
        print("Saving Error")


main()
