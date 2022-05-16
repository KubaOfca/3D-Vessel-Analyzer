import pydicom
from skimage.morphology import skeletonize
from cython_scripts.tree_from_skeleton_image import form_array_of_skeleton_make_spanning_trees
import pandas as pd
import time
import image_manipulation
from datetime import datetime
from tkinter import filedialog as fd
from tkinter import messagebox
import ttkbootstrap as tk
import threading
import os
from bs4 import BeautifulSoup
import tifffile as tiffio
import numpy as np

# TODO: 1 pomiary kretosci, modyfikacja szkieletonizacji w celu zbadania grubosci ???
# TODO: poprwiac cykle
# TODO: przeliczenie na centymetry, sprawdzic czy poprawne
# TODO: poszukac innego sposobu analizy parametrow

# global var
ROI = [(115, 1032), (169, 702)]
stop_analyze = False


def is_folder_valid(folder):
    try:
        os.listdir(folder)
    except FileNotFoundError as e:
        messagebox.showerror(
            title="Invalid directory",
            message=f"{e}\nInset a valid directory path"
        )
        return False

    return True


def is_files_with_correct_extension_valid(files, extension):
    if files:
        return True
    else:
        messagebox.showerror(
            title="Files Error",
            message=f"No {extension} files were found in this directory"
        )
        return False


def load_raw_xml_file(filename, directory):
    raw_xml_filename = f"{filename.split('.')[0]}.raw.xml"  # in order to load the same filename with .raw.xml extension
    raw_xml_full_path = os.path.join(directory, raw_xml_filename)
    try:
        with open(raw_xml_full_path, 'r') as raw_xml_file:
            raw_xml_data = raw_xml_file.read()
        xml_reader = BeautifulSoup(raw_xml_data, "xml")
        depth = float(xml_reader.find('parameter', {'name': 'B-Mode/Depth'}).get('value').replace(',', '.'))
        width = float(xml_reader.find('parameter', {'name': 'B-Mode/Width'}).get('value').replace(',', '.'))
        step_size = float(xml_reader.find('parameter', {'name': '3D-Step-Size'}).get('value').replace(',', '.'))
        pixel_size_cm = depth * width * step_size / 10
    except Exception as e:
        messagebox.showerror(
            title="Raw XML error",
            message=f"{e}\nCan't load raw.xml file, so some of features will be in pixel scale instead of cm"
        )
        pixel_size_cm = 1

    return pixel_size_cm


def check_assumption_before_analysis():
    directory = fr"{dataset_entry.get()}"

    if input_file_extension_var.get():
        extension = ".tif"
    else:
        extension = ".dcm"

    if not is_folder_valid(directory):
        return

    files = [x for x in os.listdir(directory) if x.endswith(extension)]

    if not is_files_with_correct_extension_valid(files, extension):
        return

    threading.Thread(target=analyze_vessels, args=(directory, files, len(files), extension)).start()


def save_results(result_dict, directory):
    df = pd.DataFrame(data=result_dict)
    result_file_name = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
    is_save_valid = True

    if save_file_type_var.get():
        # csv
        try:
            df.to_csv(
                rf'{directory}\{result_file_name}.csv',
                index=False
            )
        except Exception as e:
            error_text = f"Error {type(e).__name__} occurred. Arguments:\n{repr(e.args)}"
            messagebox.showerror(
                title="Error in saving to csv",
                message=f'{error_text}'
            )
            is_save_valid = False
    else:
        # xlsx
        try:
            df.to_excel(
                rf'{directory}/{result_file_name}.xlsx',
                index=False,
                sheet_name='data')
        except Exception as e:
            error_text = f"Error {type(e).__name__} occurred. Arguments:\n{repr(e.args)}"
            messagebox.showerror(
                title="Error in saving to xlsx",
                message=f'{error_text}'
            )
            is_save_valid = False

    if not is_save_valid:
        new_save_file_type = "xlsx" if save_file_type_var.get() else "csv"
        answer = messagebox.askyesno(
            title="Question?",
            message=f'Do you want try to save results in {new_save_file_type} file?'
        )
        if answer:
            try:
                if save_file_type_var.get():
                    df.to_excel(
                        rf'{directory}/{result_file_name}.xlsx',
                        index=False,
                        sheet_name='data')
                else:
                    df.to_csv(
                        rf'{directory}\{result_file_name}.csv',
                        index=False
                    )
            except Exception as e:
                error_text = f"Error {type(e).__name__} occurred. Arguments:\n{repr(e.args)}"
                messagebox.showerror(
                    title=f"Error in saving to {new_save_file_type}",
                    message=f'{error_text}\nResult won\'t be save'
                )
                return False

    return True


def analyze_vessels(directory, list_of_files, number_of_dcm_files, extension):
    global stop_analyze
    stop_analyze_button["state"] = "normal"  # GUI - make stop button able to click
    xlsx_radio["state"] = "disabled"
    csv_radio["state"] = "disabled"
    tif_radio["state"] = "disabled"
    dcm_radio["state"] = "disabled"

    result_dict = {
        "FileName": [],
        "Vessel-to-volume ratio [%]": [],
        "number of vascular trees": [],
        "length of vessels": [],
        "number of branching": [],
        "number of cycles above threshold": [],
        "number of cycles": [],
        "distance metric": [],
        "soam": [],
        "Exec time": [],
    }

    # GUI - progress bar control
    progress_bar.pack(padx=20, pady=20)
    progress_bar_label.pack(padx=20)
    file_ctr = 0
    step_of_progress_bar = 100 / number_of_dcm_files

    for filename in list_of_files:
        # GUI - after click stop button
        if stop_analyze:
            reset_app()
            messagebox.showinfo(
                title="Info",
                message="Analysis stopped"
            )
            stop_analyze = False
            return

        file_full_path = os.path.join(directory, filename)
        if os.path.isfile(file_full_path):
            s_time = time.time()

            # load file
            result_dict["FileName"].append(filename)
            pixel_size_cm = 1
            vessel_3d_array = []  # store information about vessels image in 3D array

            if extension == ".dcm":
                vessel_3d_array = pydicom.dcmread(file_full_path).pixel_array
                pixel_size_cm = load_raw_xml_file(filename, directory)
            elif extension == ".tif":
                vessel_3d_array = tiffio.imread(file_full_path)

            vessel_3d_array = vessel_3d_array[:, ROI[1][0]: ROI[1][1], ROI[0][0]: ROI[0][1]]

            # threshold and make image binary
            image_manipulation.threshold(vessel_3d_array)
            vessel_3d_array = image_manipulation.make_RGB_image_binary(vessel_3d_array)
            # make skeleton from data
            skeleton = skeletonize(vessel_3d_array, method='lee')
            # test
            # test_arr = np.zeros((3, 10, 17), dtype=np.int32)
            # test_arr[1, 5, 0] = 1
            # test_arr[1, 5, 1] = 1
            # test_arr[1, 5, 2] = 1
            # test_arr[1, 4, 3] = 1
            # test_arr[1, 6, 3] = 1
            # test_arr[1, 3, 4] = 1
            # test_arr[1, 7, 4] = 1
            # test_arr[1, 3, 5] = 1
            # test_arr[1, 7, 5] = 1
            # test_arr[1, 2, 6] = 1
            # test_arr[1, 4, 6] = 1
            # test_arr[1, 7, 6] = 1
            # test_arr[1, 1, 7] = 1
            # test_arr[1, 4, 7] = 1
            # test_arr[1, 7, 7] = 1
            # test_arr[1, 1, 8] = 1
            # test_arr[1, 3, 8] = 1
            # test_arr[1, 6, 8] = 1
            # test_arr[1, 8, 8] = 1
            # test_arr[1, 3, 9] = 1
            # test_arr[1, 6, 9] = 1
            # test_arr[1, 8, 9] = 1
            # test_arr[1, 2, 10] = 1
            # test_arr[1, 4, 10] = 1
            # test_arr[1, 7, 10] = 1
            # test_arr[1, 2, 11] = 1
            # test_arr[1, 4, 11] = 1
            # test_arr[1, 7, 11] = 1
            # test_arr[1, 4, 12] = 1
            # test_arr[1, 7, 12] = 1
            # test_arr[1, 4, 13] = 1
            # test_arr[1, 6, 13] = 1
            # test_arr[1, 8, 13] = 1
            # test_arr[1, 4, 14] = 1
            # test_arr[1, 6, 14] = 1
            # test_arr[1, 8, 14] = 1
            # test_arr[1, 5, 15] = 1
            # analyze and extract features
            trees, lv_feature, nb_feature, nc_t_feature, dm_feature, cp_feature, nc_feature \
                = form_array_of_skeleton_make_spanning_trees(skeleton)
            # save result to dict
            nt_feature = len(trees)
            result_dict["Vessel-to-volume ratio [%]"].append(round(image_manipulation.vr(vessel_3d_array), 2))
            result_dict["length of vessels"].append(round(lv_feature * pixel_size_cm, 2))
            result_dict["number of branching"].append(nb_feature)
            result_dict["number of cycles above threshold"].append(nc_t_feature)
            result_dict["number of cycles"].append(nc_feature)
            result_dict["number of vascular trees"].append(nt_feature)
            result_dict["distance metric"].append(round(dm_feature, 2))
            result_dict["soam"].append(round(cp_feature / lv_feature, 2))
            time_exec = round(time.time() - s_time, 2)
            result_dict["Exec time"].append(time_exec)

            # GUI - update progress bar
            file_ctr += 1
            progress_bar.step(step_of_progress_bar)
            progress_bar_label.configure(text=f"File {file_ctr}/{number_of_dcm_files}")
            app.update_idletasks()

    if save_results(result_dict, directory):
        # ask to open a directory with result
        answer = messagebox.askyesno(
            title="Analysis complete!",
            message="Do you want to open directory with result file",
        )
        if answer:
            os.startfile(directory)

    # reset app in order to be ready to next analyze
    reset_app()


# Main

# GUI Functions
def stop():
    global stop_analyze
    stop_analyze = True
    progress_bar_label.configure(text="Stopping the analysis process. Please wait...")
    progress_bar.configure(bootstyle="warning")
    app.update_idletasks()


def select_path():
    dataset_entry.delete(0, 'end')
    dataset_entry.insert(0, fd.askdirectory())


def reset_app():
    progress_bar.pack_forget()
    progress_bar_label.pack_forget()
    progress_bar_label.configure(text="File 0/0")
    progress_bar.configure(value=0)
    progress_bar.configure(bootstyle="success")
    stop_analyze_button["state"] = "disabled"
    xlsx_radio["state"] = "normal"
    csv_radio["state"] = "normal"
    tif_radio["state"] = "normal"
    dcm_radio["state"] = "normal"
    app.update_idletasks()


# GUI management
WIDTH = 650
HEIGHT = 450

app = tk.Window(themename="darkly")
# set window position
app.minsize(WIDTH, HEIGHT)
x_cor = (app.winfo_screenwidth()/2) - (WIDTH/2)
y_cor = (app.winfo_screenheight()/2) - (HEIGHT/2)
app.geometry('%dx%d+%d+%d' % (WIDTH, HEIGHT, x_cor, y_cor))

app.title("Vessels Analyzer")
title = tk.Label(
    app,
    text="Algorithm for the analysis of the three-dimensional distribution of vessels")

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
    command=select_path
)

input_file_type_frame = tk.Frame(
    file_path_frame
)

input_file_extension_var = tk.IntVar()

dcm_radio = tk.Radiobutton(
    input_file_type_frame,
    text=".dcm",
    variable=input_file_extension_var,
    value=0
)

tif_radio = tk.Radiobutton(
    input_file_type_frame,
    text=".tif",
    variable=input_file_extension_var,
    value=1
)

button_frame = tk.Frame(
    app
)

analyze_button = tk.Button(
    button_frame,
    text="Analyze",
    command=check_assumption_before_analysis,
    width=8
)
stop_analyze_button = tk.Button(
    button_frame,
    bootstyle="danger",
    text="Stop",
    command=stop,
    width=8
)
stop_analyze_button["state"] = "disabled"

save_file_type_label = tk.Label(
    button_frame,
    text="Save results to:"
)

save_file_type_var = tk.IntVar()

xlsx_radio = tk.Radiobutton(
    button_frame,
    text=".xlsx",
    variable=save_file_type_var,
    value=0
)

csv_radio = tk.Radiobutton(
    button_frame,
    text=".csv",
    variable=save_file_type_var,
    value=1
)

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
input_file_type_frame.grid(row=1, column=0, columnspan=2, padx=20)
dcm_radio.grid(row=0, column=0, padx=20, pady=20)
tif_radio.grid(row=0, column=1, padx=20, pady=20, sticky=tk.W)
button_frame.pack(padx=20, pady=20)
save_file_type_label.grid(row=0, column=0, columnspan=2, padx=20, pady=5)
xlsx_radio.grid(row=1, column=0, padx=20, pady=5)
csv_radio.grid(row=2, column=0, padx=20, pady=5)
analyze_button.grid(row=0, column=2, rowspan=2, padx=20, pady=5)
stop_analyze_button.grid(row=0, column=3, rowspan=2, padx=20, pady=5)

app.mainloop()
