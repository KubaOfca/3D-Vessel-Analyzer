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

# TODO: cykle, 1 pomiary kretosci, modyfikacja szkieletonizacji w celu zbadania grubosci


# global var
ROI = [(115, 1032), (169, 702)]
PIXEL_SIZE = 0.0264583333

def main():
    result_dict = {
        "FileName": [],
        "Vessel-to-volume ratio [%]": [],
        "number of vascular trees": [],
        "length of vessels": [],
        "number of branching": [],
        "number of cycles": [],
        "distance metric": [],
        "soam": [],
        "Exec time": [],
    }

    folder = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\dane_07.03.2022"
    ctr = 0  # only for debuging
    for filename in os.listdir(folder):
        file_full_path = os.path.join(folder, filename)
        if filename.endswith(".dcm") and os.path.isfile(file_full_path):
            s_time = time.time()

            result_dict["FileName"].append(filename)
            dcm_image = pydicom.dcmread(file_full_path)
            dcm_as_array = dcm_image.pixel_array[:, ROI[1][0]:ROI[1][1], ROI[0][0]:ROI[0][1]]
            iman.threshold(dcm_as_array)
            dcm_as_array = iman.make_RGB_image_binary(dcm_as_array)
            result_dict["Vessel-to-volume ratio [%]"].append(round(iman.vr(dcm_as_array), 2))
            data_skeleton = skeletonize(dcm_as_array, method='lee')
            # test_array = np.zeros((3, 5, 6), dtype=np.uint8)
            # test_array[1, 3, 0] = 1
            # test_array[1, 3, 1] = 1
            # test_array[1, 3, 2] = 1
            # test_array[1, 3, 3] = 1
            # test_array[1, 3, 4] = 1
            # test_array[1, 2, 5] = 1
            # test_array[1, 1, 4] = 1
            # test_array[1, 1, 3] = 1
            # test_array[1, 1, 2] = 1
            # test_array[1, 2, 2] = 1
            # test_array = skeletonize(test_array, method='lee')
            # print(test_array)
            trees, lv_feature, nb_feature, nc_feature, dm_feature, cp_feature, \
                vms_feature = form_array_of_skeleton_make_spanning_trees(data_skeleton)
            nt_feature = len(trees)
            result_dict["length of vessels"].append(round(lv_feature * PIXEL_SIZE, 2))
            result_dict["number of branching"].append(nb_feature)
            result_dict["number of cycles"].append(nc_feature)
            result_dict["number of vascular trees"].append(nt_feature)
            result_dict["distance metric"].append(round(dm_feature, 2))
            result_dict["soam"].append(round(cp_feature / vms_feature, 2))

            time_exec = round(time.time() - s_time, 2)
            ctr += 1
            print(f'[Exec Time] {time_exec}, Image: {ctr}')
            result_dict["Exec time"].append(time_exec)

    df = pd.DataFrame(data=result_dict)
    df.to_excel(r'C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\VesselsAnalyzer\results\Wyniki_round.xlsx',
                index=False,
                sheet_name='data')


main()
