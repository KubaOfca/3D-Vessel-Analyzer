import pydicom
from skimage.morphology import skeletonize
from cython_scripts.tree_from_skeleton_image import form_array_of_skeleton_make_spanning_trees
import os
import pandas as pd
import time
import image_manipulation as iman
import numpy as np
from datetime import datetime
from tkinter import filedialog as fd
from tkinter import messagebox
import ttkbootstrap as tk
import threading
import os
import math

# Useful commends
# np.set_printoptions(threshold=sys.maxsize)

# TODO: 1 pomiary kretosci, modyfikacja szkieletonizacji w celu zbadania grubosci ???
# TODO: przeliczenie na centymetry

# global var
ROI = [(115, 1032), (169, 702)]
PIXEL_SIZE = 0.0264583333
stop_analyze = False


def stop():
    global stop_analyze
    stop_analyze = True


def check_before_analyze():
    folder = fr"{dataset_entry.get()}"
    try:
        list_of_dcm_files = [x for x in os.listdir(folder) if x.endswith(".dcm")]
    except FileNotFoundError as e:
        messagebox.showerror(
            title="Invalid directory",
            message="Inset a valid directory path"
        )
        return

    number_of_dcm_files = len(list_of_dcm_files)

    if number_of_dcm_files < 1:
        messagebox.showerror(
            title="File Error",
            message="No dcm files were found in this directory"
        )
        return

    threading.Thread(target=analyze_vessels, args=(folder, list_of_dcm_files, number_of_dcm_files)).start()


def analyze_vessels(folder, list_of_dcm_files, number_of_dcm_files):
    stop_analyze_button["state"] = "normal"
    global stop_analyze
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

    file_ctr = 0

    step_of_progress_bar = 100 / number_of_dcm_files

    for filename in list_of_dcm_files:
        if stop_analyze:
            progress_bar_label.configure(text="File 0/0")
            progress_bar.configure(value=0)
            messagebox.showinfo(
                title="Info",
                message="Analysis stopped"
            )
            stop_analyze = False
            stop_analyze_button["state"] = "disabled"
            app.update_idletasks()
            return
        file_full_path = os.path.join(folder, filename)
        if os.path.isfile(file_full_path):
            s_time = time.time()

            result_dict["FileName"].append(filename)
            dcm_image = pydicom.dcmread(file_full_path)
            dcm_as_array = dcm_image.pixel_array[:, ROI[1][0]:ROI[1][1], ROI[0][0]:ROI[0][1]]
            iman.threshold(dcm_as_array)
            dcm_as_array = iman.make_RGB_image_binary(dcm_as_array)
            result_dict["Vessel-to-volume ratio [%]"].append(round(iman.vr(dcm_as_array), 2))
            data_skeleton = skeletonize(dcm_as_array, method='lee')
            # test_array = np.zeros((3, 5, 11), dtype=np.uint8)
            # test_array[1, 3, 0] = 1
            # test_array[1, 3, 1] = 1
            # test_array[1, 3, 2] = 1
            # test_array[1, 3, 3] = 1
            # test_array[1, 3, 4] = 1
            # test_array[1, 3, 5] = 1
            # test_array[1, 3, 6] = 1
            # test_array[1, 3, 7] = 1
            # test_array[1, 3, 8] = 1
            # test_array[1, 3, 9] = 1
            # test_array[1, 1, 9] = 1
            # test_array[1, 1, 8] = 1
            # test_array[1, 1, 7] = 1
            # test_array[1, 1, 6] = 1
            # test_array[1, 1, 5] = 1
            # test_array[1, 1, 4] = 1
            # test_array[1, 1, 3] = 1
            # test_array[1, 1, 2] = 1
            # test_array[1, 2, 2] = 1
            # test_array[1, 2, 10] = 1
            # test_array[1, 2, 6] = 1
            # test_array = skeletonize(test_array, method='lee')
            # print(test_array)
            trees, lv_feature, nb_feature, nc_feature, dm_feature, cp_feature, \
                = form_array_of_skeleton_make_spanning_trees(data_skeleton)
            nt_feature = len(trees)
            result_dict["length of vessels"].append(round(lv_feature * PIXEL_SIZE, 2))
            result_dict["number of branching"].append(nb_feature)
            result_dict["number of cycles"].append(nc_feature)
            result_dict["number of vascular trees"].append(nt_feature)
            result_dict["distance metric"].append(round(dm_feature, 2))
            result_dict["soam"].append(round(cp_feature / lv_feature, 2))

            time_exec = round(time.time() - s_time, 2)
            file_ctr += 1
            print(f'[Exec Time] {time_exec}, Image: {file_ctr}')
            result_dict["Exec time"].append(time_exec)
            progress_bar.step(step_of_progress_bar)
            progress_bar_label.configure(text=f"File {file_ctr}/{number_of_dcm_files}")
            app.update_idletasks()

    df = pd.DataFrame(data=result_dict)
    result_file_name = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
    try:
        df.to_excel(
            rf'{folder}/{result_file_name}.xlsx',
            index=False,
            sheet_name='data')
    except Exception as e:
        error_text = f"Error {type(e).__name__} occurred. Arguments:\n{repr(e.args)}"
        answer = messagebox.askyesno(
            title="Error in saving to excel",
            message=f'{error_text}\nDo you want to try to save it in .csv file?'
        )
        if answer:
            try:
                df.to_csv(
                    rf'{folder}\{result_file_name}.xlsx',
                    index=False)
            except Exception as e:
                error_text = f"Error {type(e).__name__} occurred. Arguments:\n{repr(e.args)}"
                messagebox.showerror(
                    title="Error in saving to csv",
                    message=f'{error_text}\nResult won\'t be save'
                )
                stop_analyze_button["state"] = "disabled"
                progress_bar_label.configure(text="File 0/0")
                progress_bar.configure(value=0)
                app.update_idletasks()
                return

    stop_analyze_button["state"] = "disabled"
    progress_bar_label.configure(text="File 0/0")
    progress_bar.configure(value=0)
    app.update_idletasks()

    answer = messagebox.askyesno(
        title="Analysis complete!",
        message="Do you want to open directory with result file",
    )
    if answer:
        os.startfile(folder)


# GUI
app = tk.Window(themename="darkly")
app.title("Vessels Analyzer")
title = tk.Label(
    app,
    text="Algorithm for the analysis of the three-dimensional distribution of neoplastic vessels")

file_path_frame = tk.LabelFrame(
    app,
    text="Choose path to dataset"
)

dataset_entry = tk.Entry(
    file_path_frame,
    width=70
)

browse_dataset_button = tk.Button(
    file_path_frame,
    text="Browse",
    command=lambda: dataset_entry.insert(0, fd.askdirectory())
)

button_frame = tk.Frame(
    app
)

analyze_button = tk.Button(
    button_frame,
    text="Analyze",
    command=check_before_analyze
)
stop_analyze_button = tk.Button(
    button_frame,
    bootstyle="danger",
    text="Stop",
    command=stop,
)
stop_analyze_button["state"] = "disabled"

progress_bar = tk.Progressbar(
    app,
    bootstyle=tk.SUCCESS,
    length=100
)

progress_bar_label = tk.Label(
    app,
    text="File 0/0"
)

title.pack(padx=20, pady=20)
file_path_frame.pack(padx=20, pady=20)
dataset_entry.grid(row=0, column=0, padx=20, pady=20)
browse_dataset_button.grid(row=0, column=1, padx=20, pady=20)
button_frame.pack(padx=20, pady=20)
analyze_button.grid(row=0, column=0, padx=20, pady=5, sticky=tk.EW)
stop_analyze_button.grid(row=1, column=0, padx=20, pady=5, sticky=tk.EW)
progress_bar.pack(padx=20, pady=20)
progress_bar_label.pack(padx=20, pady=20)

app.mainloop()
