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


# TODO: 1 pomiary kretosci, modyfikacja szkieletonizacji w celu zbadania grubosci ???
# TODO: przeliczenie na centymetry

# global var
ROI = [(115, 1032), (169, 702)]
PIXEL_SIZE = 0.0264583333
stop_analyze = False


def stop():
    global stop_analyze
    stop_analyze = True
    progress_bar_label.configure(text="Stopping the analysis process. Please wait...")
    progress_bar.configure(bootstyle="warning")
    app.update_idletasks()


def reset_app():
    progress_bar.pack_forget()
    progress_bar_label.pack_forget()
    progress_bar_label.configure(text="File 0/0")
    progress_bar.configure(value=0)
    progress_bar.configure(bootstyle="success")
    stop_analyze_button["state"] = "disabled"
    app.update_idletasks()


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
    global stop_analyze
    stop_analyze_button["state"] = "normal"  # make stop button able to click
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

    # progress bar control
    progress_bar.pack(padx=20, pady=20)
    progress_bar_label.pack(padx=20, pady=20)
    file_ctr = 0
    step_of_progress_bar = 100 / number_of_dcm_files

    for filename in list_of_dcm_files:
        # if user click stop button
        if stop_analyze:
            reset_app()
            messagebox.showinfo(
                title="Info",
                message="Analysis stopped"
            )
            stop_analyze = False
            return

        file_full_path = os.path.join(folder, filename)
        if os.path.isfile(file_full_path):
            s_time = time.time()

            # load file
            result_dict["FileName"].append(filename)
            dcm_image = pydicom.dcmread(file_full_path)
            dcm_as_array = dcm_image.pixel_array[:, ROI[1][0]:ROI[1][1], ROI[0][0]:ROI[0][1]]
            # threshold and make image binary
            iman.threshold(dcm_as_array)
            dcm_as_array = iman.make_RGB_image_binary(dcm_as_array)
            # make skeleton from data
            skeleton = skeletonize(dcm_as_array, method='lee')
            # analyze and extract features
            trees, lv_feature, nb_feature, nc_feature, dm_feature, cp_feature, \
                = form_array_of_skeleton_make_spanning_trees(skeleton)
            # save result to dict
            nt_feature = len(trees)
            result_dict["Vessel-to-volume ratio [%]"].append(round(iman.vr(dcm_as_array), 2))
            result_dict["length of vessels"].append(round(lv_feature * PIXEL_SIZE, 2))
            result_dict["number of branching"].append(nb_feature)
            result_dict["number of cycles"].append(nc_feature)
            result_dict["number of vascular trees"].append(nt_feature)
            result_dict["distance metric"].append(round(dm_feature, 2))
            result_dict["soam"].append(round(cp_feature / lv_feature, 2))
            time_exec = round(time.time() - s_time, 2)
            result_dict["Exec time"].append(time_exec)
            # update progress bar
            file_ctr += 1
            progress_bar.step(step_of_progress_bar)
            progress_bar_label.configure(text=f"File {file_ctr}/{number_of_dcm_files}")
            app.update_idletasks()

    # save result to excel or csv file.
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
                reset_app()
                return

    # reset app to init state in order to be ready to next analyze
    reset_app()
    # ask to open a directory with result
    answer = messagebox.askyesno(
        title="Analysis complete!",
        message="Do you want to open directory with result file",
    )
    if answer:
        os.startfile(folder)


# Main

# GUI management
WIDTH = 650
HEIGHT = 450

app = tk.Window(themename="darkly")
# set window position
app.minsize(WIDTH, HEIGHT)
x = (app.winfo_screenwidth()/2) - (WIDTH/2)
y = (app.winfo_screenheight()/2) - (HEIGHT/2)
app.geometry('%dx%d+%d+%d' % (WIDTH, HEIGHT, x, y))

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
    bootstyle="success",
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

app.mainloop()
