import os
import shutil
from datetime import datetime

# input parameters
master_folder = "D:/Xiaowei/data/20210607_screen/"
data_source = "D:/Xiaowei/data/20210607_screen/"

# log all the running info
if not os.path.exists("%sscreen_processing_log.txt" % master_folder):
    f = open("%sscreen_processing_log.txt" % master_folder, "w+")
else:
    f = open("%sscreen_processing_log.txt" % master_folder, "a+")

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
f.write("datetime: %s\n" % dt_string)
f.write("code_running: %s\n" % __file__)
f.write("master_folder: %s\n" % master_folder)
f.write("data_source: %s\n\n" % data_source)

f.close()

# script start
dirs = [x[0] for x in os.walk(data_source)]
dirs.pop(0)
num_dir = len(dirs)

for s in range(len(dirs)):
    data_path = dirs[s]
    mf_name = dirs[s].split('/')[-1].split('-')[0]
    move_path = ("%s/data/%s/" % (data_source, mf_name))
    if not os.path.exists(move_path):
        os.makedirs(move_path)
    shutil.move(dirs[s], move_path)

print("Done")
