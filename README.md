# 3D-Vessel-Analyzer

## Overview  
This project focuses on analyzing three-dimensional morfology of blood vessels in neoplastic tumors using the 3D Power Doppler ultrasound technique. This imaging method enables detailed visualization of tumor vascularization and facilitates monitoring the effects of anticancer therapies on vessel morphology and quantity.  

The primary objective of this project is to develop an algorithm capable of analyzing morphological features of vessels based on Doppler ultrasound images.  

## Algorithm Stages  
The algorithm comprises several processing steps:  
1. **Binarization** – Conversion of grayscale images into binary representations.  
2. **Thresholding** – Selection of vessel structures based on intensity values.  
3. **Skeletonization** – Reduction of vessels to their central lines for morphological analysis.  
4. **Tree Building** – Construction of vessels structure representation.  
5. **Post-Processing** – Refinement of the vascular model by eliminating noise and artifacts.  
6. **Feature Extraction** – Calculation of morphological parameters.  

## Extracted Parameters  
The algorithm provides information on the following features:  
- **Vessel-Volume Ratio**: Proportion of vessel volume to total image volume.  
- **Number of Vascular Trees**: Count of distinct vascular structures.  
- **Vessel Length**: Total length of all vessels in the image.  
- **Number of Branches**: Total branch points in the vascular network.  
- **Number of Cycles**: Count of closed loops in the vascular structure.  
- **Cycle Size**: Number of loops exceeding a defined size threshold.  
- **Tortuosity Measurements**: Two metrics to quantify vessel curvature and irregularity.  

## Application  
The developed algorithm has been applied to study the normalization process of neoplastic vessels influenced by **metformin therapy** and **oxygen microbubbles**. These tools provide insights into how treatments impact vascularization, aiding the development of more effective cancer therapies.  

## Supported Input Formats  
The program supports the analysis of both `DICOM` and `TIFF` image formats. Additionally, it can process metadata associated with these images from accompanying `XML` or `CSV` files.  

Below is an example of an input image:  
![Example Input Image](https://mindray.scene7.com/is/image/mindray/doppler-shades-color-fig4-pc?$630-423$)  

## User Interface  
The tool features a dedicated **Tkinter-based GUI** that simplifies the analysis process, making it more user-friendly and accessible.

Screenshot of the user interface:  
![Example UI](https://github.com/user-attachments/assets/c51ceb6e-f344-48a9-b43a-322ae3e3a6d1)

## Publication

https://www.mdpi.com/1422-0067/24/15/12156

