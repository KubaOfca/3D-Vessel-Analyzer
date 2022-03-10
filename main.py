import matplotlib.pyplot as plt
import pydicom
import sys
import cv2
import math
import numpy as np
import os
# np.set_printoptions(threshold=sys.maxsize)


def threshold_image(image):
    number_of_panels, number_of_rows, number_of_columns, rgb = image.pixel_array.shape
    for panel in range(number_of_panels):
        print(f"Changing panel no. {panel}")
        for row in range(number_of_rows):
            if row % 50 == 0:
                print(f"Row no: {row}")
            for col in range(number_of_columns):
                if image.pixel_array[panel, row, col, 0] >= 120 and image.pixel_array[panel, row, col, 1] <= 105:
                    image.pixel_array[panel, row, col] = 255
                else:
                    image.pixel_array[panel, row, col] = 0
        plt.axis("off")
        plt.imshow(image.pixel_array[panel, :, 100:].astype(np.uint8))
        plt.savefig(f"{panel}.png")



# creates a point cloud file (.ply) from numpy array
def createPointCloud(filename, arr):
    # open file and write boilerplate header
    file = open(filename, 'w');
    file.write("ply\n");
    file.write("format ascii 1.0\n");

    # count number of vertices
    num_verts = arr.shape[0];
    file.write("element vertex " + str(num_verts) + "\n");
    file.write("property float32 x\n");
    file.write("property float32 y\n");
    file.write("property float32 z\n");
    file.write("end_header\n");

    # write points
    point_count = 0;
    for point in arr:
        # progress check
        point_count += 1;
        if point_count % 1000 == 0:
            print("Point: " + str(point_count) + " of " + str(len(arr)));

        # create file string
        out_str = "";
        for axis in point:
            out_str += str(axis) + " ";
        out_str = out_str[:-1];  # dump the extra space
        out_str += "\n";
        file.write(out_str);
    file.close();

# extracts points from mask and adds to list
def addPoints(mask, points_list, depth):
    mask_points = np.where(mask == 255);
    for ind in range(len(mask_points[0])):
        # get point
        x = mask_points[1][ind];
        y = mask_points[0][ind];
        point = [x, y, depth];
        points_list.append(point);

def view_3D():
    # tweakables
    slice_thickness = .36195;  # distance between slices
    xy_scale = 5;  # rescale of xy distance

    # load images
    folder = "images/";
    files = os.listdir(folder);
    images = [];
    for file in files:
        if file[-4:] == ".png":
            img = cv2.imread(folder + file, cv2.IMREAD_GRAYSCALE);
            img = cv2.resize(img, (200, 200));  # change here for more or less resolution
            print(type(img))
            print(img.shape)
            images.append(img);

    # keep a blank mask
    blank_mask = np.zeros_like(images[0], np.uint8);

    # create masks
    masks = [];
    masks.append(blank_mask);
    for image in images:
        # mask
        mask = cv2.inRange(image, 0, 100);

        # show
        cv2.imshow("Mask", mask);
        cv2.waitKey(1);
        masks.append(mask);
    masks.append(blank_mask);
    cv2.destroyAllWindows();

    # go through and get points
    depth = 0;
    points = [];
    for index in range(1, len(masks) - 1):
        # progress check
        print("Index: " + str(index) + " of " + str(len(masks)));

        # get three masks
        prev = masks[index - 1];
        curr = masks[index];
        after = masks[index + 1];

        # do a slice on previous
        prev_mask = np.zeros_like(curr);
        prev_mask[prev == 0] = curr[prev == 0];
        addPoints(prev_mask, points, depth);

        # # do a slice on after
        next_mask = np.zeros_like(curr);
        next_mask[after == 0] = curr[after == 0];
        addPoints(next_mask, points, depth);

        # get contour points (_, contours) in OpenCV 2.* or 4.*
        contours, hierarchy = cv2.findContours(curr, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for con in contours:
            for point in con:
                p = point[0];  # contours have an extra layer of brackets
                points.append([p[0], p[1], depth]);

        # increment depth
        depth += slice_thickness;

    # rescale x,y points
    for ind in range(len(points)):
        # unpack
        x, y, z = points[ind];

        # scale
        x *= xy_scale;
        y *= xy_scale;
        points[ind] = [x, y, z];

    # convert points to numpy and dump duplicates
    points = np.array(points).astype(np.float32);
    points = np.unique(points.reshape(-1, points.shape[-1]), axis=0);
    print(points.shape);

    # save to point cloud file
    createPointCloud("test.ply", points);



filepath = r"C:\Users\Jakub Lechowski\Desktop\PracaLicencjacka\Skrypty\ImageViewer\bazaDanychDCM\zdj.dcm"
dcm_image = pydicom.dcmread(filepath)

threshold_image(dcm_image)






