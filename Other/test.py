import os
import shutil
import time

shutil.rmtree('online_devices')
time.sleep(0.2)
os.mkdir('online_devices')