import numpy as np
import pandas as pd
import napari
from pycromanager import Bridge
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from shared.find_organelles import find_organelle
from skimage.measure import label, regionprops
import shared.analysis as ana
import shared.dataframe as dat
import os

# --------------------------
# PARAMETERS allow change
# --------------------------
# Please changes
data_path = "/Users/xwyan/Dropbox/LAB/ChangLab/Projects/Data/100xData_forXiaowei/Speckles_100x/20211109_H3/H3-Site_1_1"
save_path = "/Users/xwyan/Dropbox/LAB/ChangLab/Projects/Data/100xData_forXiaowei/test/Speckles_100x/20211109_H3/H3-Site_1_1"
analyze_organelle = 'nucleoli'  # only accepts 'nucleoli'

# values for analysis
data_c = 0
pos = 0
num_dilation = 3  # number of dilation from the coordinate;
                  # determines analysis size of the analysis spots; default = 3
ctrl_number = 5
tracking_dis = 15

# presets
if analyze_organelle == 'nucleoli':
    thresholding = 'local-nucleoli'
    # global thresholding method; choose in between 'na','otsu','yen', 'local-nucleoli' and 'local-sg'
    min_size = 10  # minimum size; nucleoli default = 10
    max_size = 1000  # maximum size; nucleoli default = 1000;
    # larger ones are generally cells without nucleoli

# modes
fitting_mode = 'single_exp'  # accepts 'single_exp', 'double_exp', 'soumpasis', 'ellenberg', 'optimal'

"""
# ---------------------------------------------------------------------------------------------------
# PLEASE DO NOT CHANGE AFTER THIS
# ---------------------------------------------------------------------------------------------------
"""

# --------------------------
# LOAD MOVIE
# --------------------------
print("### Load movie ...")
data_log = pd.DataFrame({'pos': [pos]})

# build up pycromanager bridge
# first start up Micro-Manager (needs to be compatible version)
bridge = Bridge()
mmc = bridge.get_core()
mm = bridge.get_studio()
# load time series data
store = mm.data().load_data(data_path, True)
cb = mm.data().get_coords_builder()
cb.t(0).p(0).c(0).z(0)
# get max_t and acquisition time
max_t = store.get_max_indices().get_t()
pixels_tseries = dat.get_pixels_tseries(store, cb, data_c)
acquire_time_tseries, real_time = dat.get_time_tseries(store, cb)
data_log['acquire_time'] = [acquire_time_tseries]
data_log['real_time'] = [real_time]

# ----------------------------------
# BLEACH SPOTS DETECTION
# ----------------------------------
print("### Image analysis: bleach spots filtration ...")

# load point_and_shoot log file
log_pd = pd.read_csv('%s/PointAndShoot.log' % data_path, na_values=['.'], sep='\t', header=None)
data_log['num_aim_spots'] = [len(log_pd)]
print("Aim to photobleach %d spots." % data_log['num_aim_spots'][0])
log_pd.columns = ['time', 'aim_x', 'aim_y']  # reformat log_pd

# get bleach_frame
log_pd['bleach_frame'] = dat.get_frame(log_pd['time'], acquire_time_tseries)

# filter bleach_spots that are outside of the organelle
time_ft = []
aim_x_ft = []
aim_y_ft = []
bleach_frame_ft = []
center_x = []
center_y = []
for i in range(len(log_pd)):
    ref_frame = int(log_pd['bleach_frame'][i])-1
    if ref_frame >= 0:
        temp = store.get_image(cb.c(data_c).t(ref_frame).build())
        pix = np.reshape(temp.get_raw_pixels(), newshape=[temp.get_height(), temp.get_width()])
        # organelle detection
        organelle_before_filter, organelle = find_organelle(pix, thresholding, min_size=min_size, max_size=max_size)
        label_organelle = label(organelle, connectivity=1)
        if organelle[int(log_pd['aim_y'][i]), int(log_pd['aim_x'][i])] != 0:
            num_organelle = label_organelle[int(log_pd['aim_y'][i]), int(log_pd['aim_x'][i])]
            center = regionprops(label_organelle)[num_organelle-1].centroid
            time_ft.append(log_pd['time'][i])
            aim_x_ft.append(log_pd['aim_x'][i])
            aim_y_ft.append(log_pd['aim_y'][i])
            bleach_frame_ft.append(log_pd['bleach_frame'][i])
            center_x.append(round(center[1]))
            center_y.append(round(center[0]))

coordinate_pd = pd.DataFrame({'time': time_ft, 'aim_x': aim_x_ft, 'aim_y': aim_y_ft, 'bleach_frame': bleach_frame_ft,
                              'center_x': center_x, 'center_y': center_y})
print(coordinate_pd)

# identify ctrl organelles
print("### Image analysis: identifying ctrl organelles ...")
temp = store.get_image(cb.c(data_c).t(0).build())
pix = np.reshape(temp.get_raw_pixels(), newshape=[temp.get_height(), temp.get_width()])
organelle_before_filter, organelle = find_organelle(pix, thresholding, min_size=min_size, max_size=max_size)
label_organelle = label(organelle, connectivity=1)
centers = [regionprops(label_organelle)[x].centroid for x in range(len(regionprops(label_organelle)))]
ctrl_centers = centers.copy()
print(len(ctrl_centers))
for i in range(len(coordinate_pd)):
    aim_spot = (coordinate_pd['center_x'][i], coordinate_pd['center_y'][i])
    close_spot = dat.find_closest_coordinate(aim_spot, centers, 100000000)
    if close_spot in ctrl_centers:
        ctrl_centers.remove(close_spot)

# determine bleach spots location/intensity relative to corresponding organelle
print("### Image analysis: measuring bleach/ctrl spots intensity ...")

spots = pd.DataFrame({'aim_x': list(coordinate_pd['aim_x'])+[round(x[0]) for x in ctrl_centers[:ctrl_number]],
                      'aim_y': list(coordinate_pd['aim_y'])+[round(x[1]) for x in ctrl_centers[:ctrl_number]],
                      'center_x': list(coordinate_pd['center_x'])+[round(x[0]) for x in ctrl_centers[:ctrl_number]],
                      'center_y': list(coordinate_pd['center_y'])+[round(x[1]) for x in ctrl_centers[:ctrl_number]],
                      'group': ['bleach']*len(coordinate_pd)+['ctrl']*ctrl_number})
print(spots)

x_list = [[] for _ in range(len(spots))]
y_list = [[] for _ in range(len(spots))]
int_list = [[] for _ in range(len(spots))]
print(len(x_list))
for i in range(len(spots)):
    print("### Image analysis: measuring %d/%d ..." % (i+1, len(spots)))
    centroid_x = [spots['center_x'][i]]
    centroid_y = [spots['center_y'][i]]
    for t in range(max_t):
        temp = store.get_image(cb.c(data_c).t(t).build())
        pix = np.reshape(temp.get_raw_pixels(), newshape=[temp.get_height(), temp.get_width()])
        organelle_before_filter, organelle = find_organelle(pix, thresholding, min_size=min_size, max_size=max_size)
        label_organelle = label(organelle, connectivity=1)
        centers = [regionprops(label_organelle)[x].centroid for x in range(len(regionprops(label_organelle)))]

        aim_spot = (centroid_y[-1], centroid_x[-1])
        close_spot = dat.find_closest_coordinate(aim_spot, centers, tracking_dis)
        centroid_x.append(round(close_spot[1]))
        centroid_y.append(round(close_spot[0]))
        bleach_spots_x_temp = round(close_spot[1]) + spots['aim_x'][i] - spots['center_x'][i]
        x_list[i].append(bleach_spots_x_temp)
        bleach_spots_y_temp = round(close_spot[0]) + spots['aim_y'][i] - spots['center_y'][i]
        y_list[i].append(bleach_spots_y_temp)

        bleach_spots = ana.analysis_mask([bleach_spots_y_temp], [bleach_spots_x_temp], pix, num_dilation)
        label_bleach_spots = label(bleach_spots, connectivity=1)
        int_temp = regionprops(label_bleach_spots, pix)[0].mean_intensity
        int_list[i].append(int_temp)

spots['x'] = x_list
spots['y'] = y_list
spots['int'] = int_list

# --------------------------
# OUTPUT
# --------------------------
print("### Export data ...")

storage_path = save_path
if not os.path.exists(storage_path):
    os.makedirs(storage_path)

# data_log
data_log.to_csv('%s/data_log.txt' % storage_path, index=False, sep='\t')
spots.to_csv('%s/spots.txt' % storage_path, index=False, sep='\t')

# napari display
viewer = napari.Viewer()
mpl_widget = FigureCanvas(Figure(figsize=(5, 3)))
[ax1, ax2] = mpl_widget.figure.subplots(nrows=1, ncols=2)

viewer.window.add_dock_widget(mpl_widget)

for i in range(len(spots)):
    if spots['group'][i] == 'bleach':
        ax1.plot(spots['int'][i])
    else:
        ax2.plot(spots['int'][i])
ax1.set_title('FRAP curves')
ax1.set_xlabel('time')
ax1.set_ylabel('intensity')
ax2.set_title('ctrl curves')
ax2.set_xlabel('time')
ax2.set_ylabel('intensity')
napari.run()
