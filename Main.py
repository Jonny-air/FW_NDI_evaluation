import Convert_Logs as conv
import os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

#parameters
log_name = 'log_ndi'
fb_enabled = 'not'

start_min = 1
start_sec = 43
end_min = 2
end_sec = 3

#Setup

if(not os.path.isfile(f"./csv/{log_name}_ndi_status_0.csv")):
    print("CSV does not exists yet - converting from log")
    conv.convert_log_to_csv(log_name)
# convert into dataframes
start_time = start_min*60+start_sec
end_time = end_min*60+end_sec
ndiDF = pd.read_csv(f'./csv/{log_name}_ndi_status_0.csv', index_col=0)

ndiDF = ndiDF.query(f'timestamp >= {start_time*1.0E6} and timestamp <= {end_time*1.0E6}')

fpa_col = ndiDF.loc[:,'filtered_fpa']
fpas = fpa_col.values*180/np.pi
fpa_setpoint_col = ndiDF.loc[:,'fpa_setpoint']
fpa_sps = fpa_setpoint_col.values*180/np.pi
airsp_col = ndiDF.loc[:,'filtered_airsp']
airsps = airsp_col.values
airsp_setpoint_col = ndiDF.loc[:,'airsp_setpoint']
airsp_sps = airsp_setpoint_col.values
t = ndiDF.index.values /1.0E6

fig, axs = plt.subplots(2, figsize=(10, 10))

axs[0].plot(t, fpas, 'b', label='Actual FPA')
axs[0].plot(t, fpa_sps, 'g', label='FPA Setpoint')
axs[1].plot(t, airsps, 'b', label='Actual Airspeed')
axs[1].plot(t, airsp_sps, 'g', label='Airspeed Setpoint')

axs[0].set_xlabel('Time [s]')
axs[1].set_xlabel('Time [s]')
axs[0].set_ylabel('FPA [deg}')
axs[1].set_ylabel('airspeed [m/s]')
axs[0].set_title(f'NDI Setpoint tracking performance with feedback {fb_enabled} enabled')
axs[0].grid()
axs[1].grid()
axs[0].legend(loc='best')
axs[1].legend(loc='best')
plt.show()
