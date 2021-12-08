import pandas as pd
import shared.dataframe as dat
import napari
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime

master_folder = "/Users/xwyan/Dropbox/LAB/ChangLab/Projects/Data/100xData_forXiaowei/test/Speckles_100x/20211109_H3/H3-Site_1_1/"
spots = pd.read_csv('%sspots.txt' % master_folder, na_values=['.'], sep='\t')
spots['int'] = [dat.str_to_float(spots['int'][i]) for i in range(len(spots))]

# embed mpl widget in napari viewer
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