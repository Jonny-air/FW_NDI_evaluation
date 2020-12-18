import Convert_Logs as conv
import os.path
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mathutils import Vector
from pathlib import Path

#parameters
log_name = 'log_wind_1'
fb_enabled = ''
pickup = True
use_latlon = True

# start_min = 1
# start_sec = 43
# end_min = 2
# end_sec = 3

#Setup

if(not os.path.isfile(f"./csv/{log_name}_ndi_status_0.csv")):
    print("CSV does not exists yet - converting from log")
    conv.convert_log_to_csv(log_name)
# convert into dataframes
# start_time = start_min*60+start_sec
# end_time = end_min*60+end_sec
ndiDF = pd.read_csv(f'./csv/{log_name}_ndi_status_0.csv', index_col=0)

# ndiDF = ndiDF.query(f'timestamp >= {start_time*1.0E6} and timestamp <= {end_time*1.0E6}')
def get_col_values(colname):
    col = ndiDF.loc[:,f'{colname}']
    return col.values

fpas = get_col_values('filtered_fpa')*180/np.pi
fpa_sps = get_col_values('fpa_setpoint')*180/np.pi

airsps = get_col_values('filtered_airsp')
airsp_sps = get_col_values('airsp_setpoint')
tuning_params1 = get_col_values('tuning_param1')
tuning_params2 = get_col_values('tuning_param2')

if pickup:
    hs = get_col_values('local_z')
    h_sps = get_col_values('h_sp')

    ndiDF = ndiDF.query(f'pickup_z != 0.0')

    x_loc = get_col_values('local_x')
    y_loc = get_col_values('local_y')
    z_loc = get_col_values('local_z')
    pickup_x = get_col_values('pickup_x')
    pickup_y = get_col_values('pickup_y')
    pickup_z = get_col_values('pickup_z')
    if use_latlon:
        origin = [0,0] #reference lat, lon in deg
        dx1 = x_loc - np.ones_like(x_loc)*origin[0]
        dx2 = pickup_x - np.ones_like(pickup_x)*origin[0]
        dy1 = y_loc - np.ones_like(y_loc)*origin[0]
        dy2 = pickup_y - np.ones_like(pickup_y)*origin[0]
        latitudeCircumference = 40075160 * np.cos(math.radians(origin[0]))
        x_loc = dx1 * latitudeCircumference / 360
        pickup_x = dx2 * latitudeCircumference / 360
        y_loc = dy1 * 40075160 / 360
        pickup_y = dy2 * 40075160 / 360

    dist = np.sqrt( (pickup_x-x_loc)**2 + (pickup_y-y_loc)**2 + (pickup_z-z_loc)**2)
    hit_index = np.argmin(dist)
    before = Vector((x_loc[hit_index-1], y_loc[hit_index-1], z_loc[hit_index-1]))
    after = Vector((x_loc[hit_index+1], y_loc[hit_index+1], z_loc[hit_index+1]))
    target = Vector((pickup_x[hit_index], pickup_y[hit_index], pickup_z[hit_index]))
    n = (after - before).normalized()
    ap = target - before
    tangent = ap.dot(n)
    closest = before + tangent * n  # x is a point on line
    vertical_distance = closest[2]-pickup_z[hit_index]
    horizontal_distance = np.sqrt((pickup_x[hit_index]-closest[0])**2 + (pickup_y[hit_index]-closest[1])**2)
    print("vertical distance:", vertical_distance)
    print("horizontal distance:", horizontal_distance)

# t = ndiDF.index.values /1.0E6
t = np.array(range(fpas.size))*0.1


fig, axs = plt.subplots(2, figsize=(10, 10))

axs[0].plot(t, fpas, 'b', label='Actual FPA')
axs[0].plot(t, fpa_sps, 'g', label='FPA Setpoint')
axs[1].plot(t, airsps, 'b', label='Actual Airspeed')
axs[1].plot(t, airsp_sps, 'g', label='Airspeed Setpoint')

# axs3 = axs[0].twinx()
# axs3.plot(t, tuning_params2, 'r', label='LQR(1)')
# axs3.plot(t, tuning_params1, 'g', label=('LQR(0)'))

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

if pickup:
    fig, axs = plt.subplots(2, figsize=(10, 10))

    axs[1].plot(t, hs, 'b', label='Actual Height [m]')
    axs[1].plot(t, h_sps, 'g', label='Height Setpoints')
    axs[0].plot(t, fpas, 'b', label='Actual FPA')
    axs[0].plot(t, fpa_sps, 'g', label='FPA Setpoint')

    axs[0].set_xlabel('Time [s]')
    axs[1].set_xlabel('Time [s]')
    axs[0].set_ylabel('FPA [deg}')
    axs[1].set_ylabel('Height [m]')
    axs[0].set_title(f'NDI Setpoint tracking performance with feedback {fb_enabled} enabled')
    axs[0].grid()
    axs[1].grid()
    axs[0].legend(loc='best')
    axs[1].legend(loc='best')
    plt.show()

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d', autoscale_on=True)
    ax.grid()

    global timestep

    def animate(i):
        global timestep
        timestep = i
        plane_loc.set_data(x_loc[i-20:i + 1], y_loc[i-20:i + 1])
        plane_loc.set_3d_properties(z_loc[i-20:i + 1])
        target_prevloc.set_data(pickup_x[i - 5:i], pickup_y[i - 5:i])
        target_prevloc.set_3d_properties(pickup_z[i - 5:i])
        target_loc.set_data(pickup_x[i+1], pickup_y[i+1])
        target_loc.set_3d_properties(pickup_z[i+1])
        x_dist = abs(pickup_x[i+1] - x_loc[i+1])
        y_dist = abs(pickup_y[i+1] - y_loc[i+1])
        if(x_dist > 100 or y_dist > 100 ): x_dist = y_dist = 200
        elif (x_dist > 50 or y_dist > 50): x_dist = y_dist = 100
        elif (x_dist > 10 or y_dist > 10): x_dist = y_dist = 50
        else: x_dist = y_dist = 10
        avg_pickup_x = np.sum(pickup_x[i-10:i+1])/11
        avg_pickup_y = np.sum(pickup_y[i-10:i+1])/11
        ax.set_xlim(avg_pickup_x-x_dist,avg_pickup_x+x_dist)
        ax.set_ylim(avg_pickup_y-y_dist, avg_pickup_y+y_dist)
        ax.set_zlim(pickup_z[0], z_loc[0])
        ax.margins(1, tight=False)
        ax.autoscale_view()
        return plane_loc, target_prevloc, target_loc

    plane_loc, = ax.plot([],[],[], 'o-', color="blue")
    target_loc, = ax.plot([],[],[], 'x', color="red")
    target_prevloc, = ax.plot([],[],[], 'x', color="red", alpha = 0.5)

    def on_press(event):
        if event.key.isspace():
            if ani.running:
                ani.event_source.stop()
            else:
                ani.event_source.start()
            ani.running ^= True
        elif event.key == 'up':
            global timestep
            i = timestep
            ax.set_xlim(pickup_x[i] - 0.5, pickup_x[i] + 0.5)
            ax.set_ylim(pickup_y[i] - 0.5, pickup_y[i] + 0.5)
            ax.set_zlim(pickup_z[i] - 0.5 , pickup_z[i] + 0.5)
            plt.draw()
        elif event.key == 'down':
            i = timestep
            ax.set_xlim(pickup_x[i] - 10, pickup_x[i] + 10)
            ax.set_ylim(pickup_y[i] - 10, pickup_y[i] + 10)
            ax.set_zlim(pickup_z[i], pickup_z[i] + 10)
            plt.draw()

    fig.canvas.mpl_connect('key_press_event', on_press)

    frames = range(hit_index-100, hit_index + 3)
    dt = 1 / 100.
    from time import time
    t0 = time()
    animate(0)
    t1 = time()
    interval = len(frames) * dt - (t1 - t0)

    def update_time():
        t = 0
        t_max = interval
        while t < t_max:
            yield t

    ani = animation.FuncAnimation(fig, animate, frames=frames, interval=interval, blit = False, repeat=False)
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

    ani.running = True
    plt.figtext(0.05, 0.05, f"closest vertical distance: {round(vertical_distance*100,2)}cm \nclosest horizontal distance: {round(horizontal_distance*100,2)}cm")
    ax.plot(closest[0], closest[1], closest[2], 'x', color="green")

    # ani.save('state_level_random_walk.mp4', writer=writer)
    plt.show()



