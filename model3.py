import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import animation
from matplotlib.widgets import Slider
from enum import IntEnum, Enum

"""
this model will account for wind intensity, wind direction and tree type,
the model will have three types of growth: brush, cedar and other sap rich trees, and conifers
the model will have an option to grow the trees and after a selected amount of time you can set the direction of the wind and launch a spark from the middle
"""

# consts
neighbors = [(0,1), (1,1), (1,0), (-1,0), (-1,-1), (0,-1), (-1,1), (1, -1)]

class Stages(IntEnum):
    EMPTY = 0
    TREE1 = 1
    TREE2 = 2
    TREE3 = 3
    ONFIRE = 4

# TODO: update fire burn duration by creating different flame intensities and spreads

# different percents of likelihood that a flame will catch onto the current square, assigned depending on wind direction and square position 
flame_percent = [1.0, 1.0, 1.0, 1.0, 1.0]
wind_impact = [0, 0.05, 0.12, 0.18, 0.2]

#  color list and map
color_list = ["#400f15", "#4A6E1A", "#5FCA07", "#1fc506", "#ff7429"]
cmap = colors.ListedColormap(color_list)
boundaries = [0,1,2,3,4,5]
norm = colors.BoundaryNorm(boundaries, cmap.N)

# initial fraction of a forest occupied by trees
init_coverage = 0.2

# probability of a tree growing in a cell, probability of a lightning strike
p, f = 0.05, 0.0001

# size of grid 
sizex, sizey = 100, 100

# probability of catching fire
burn_risk = 0.7

# wind direction, 0-359 degrees, with 0 degrees pointing east
wind_angle = 0

# wind intensity, between 0-5
wind_change = False
wind_intensity = 0




# Create an update function 
def update(grid):
    # fill the new grid with zeros
    new_grid = np.zeros((sizex, sizey))
    # iterate through each cell
    for ix in range(1,sizex-1):
        for iy in range(1, sizey-1):
            # if the cell is empty, probabalistically grow a tree
            if grid[iy,ix] == Stages.EMPTY and np.random.random() <= p:
                new_grid[iy,ix] = Stages.TREE1
            if grid[iy,ix] >= Stages.TREE1 and grid[iy,ix] < Stages.ONFIRE:
                new_grid[iy,ix] = assign_tree(grid[iy,ix])
                if wind_angle == None:
                    new_grid[iy, ix] = assign_fire_no_wind((iy,ix), grid, new_grid)
                else:
                    new_grid[iy, ix] = assign_fire_with_wind((iy,ix), grid, new_grid, wind_angle)
                if new_grid[iy,ix] >= Stages.TREE1 and new_grid[iy,ix] < Stages.ONFIRE:
                    if np.random.random() <= f:
                         new_grid[iy,ix] = Stages.ONFIRE

    return new_grid


# update tree growth with different levels of tree density
def assign_tree(tree_val):
    new_val = tree_val
    if np.random.random() <= p and tree_val < Stages.TREE3:
        match tree_val:
            case Stages.TREE1:
                return Stages.TREE2
            case Stages.TREE2:
                return Stages.TREE3
    return tree_val


# account for windspread
def assign_fire_with_wind(square, oldgrid, newgrid, angle):
    # get current coordinates
    y, x = square[0], square[1]
    current_tree_cover = newgrid[y,x]
    if wind_change:
        account_wind_intensity()
    nb_percents = find_percents(angle, flame_percent)
    for entry in nb_percents:
        if oldgrid[y+entry[0][0], x+entry[0][1]] == Stages.ONFIRE and np.random.random() <= entry[1]:
            return Stages.ONFIRE    
    return current_tree_cover

# add wind intensity
def account_wind_intensity():
    global flame_percent
    global wind_change
    flame_percent_new = []
    for i in range(len(flame_percent)):
        flame_percent_new.append(1.0 - (wind_impact[i]*wind_intensity))
    flame_percent = flame_percent_new
    wind_change = False

# get the quadrants that will impact the current square the most and less so
def find_percents(angle, flame_percent):
    if angle > 338 or angle <= 23:
        return [((0,-1), flame_percent[0]), ((1,-1), flame_percent[1]), ((-1,-1), flame_percent[1]), ((1,0), flame_percent[2]), ((-1,0), flame_percent[2]), ((1,1), flame_percent[3]), ((-1,1), flame_percent[3]), ((0,1), flame_percent[4])];
    elif angle > 23 and angle <= 68:
        return [((-1,-1), flame_percent[0]), ((0,-1), flame_percent[1]), ((-1,0), flame_percent[1]), ((1,-1), flame_percent[2]), ((-1,1), flame_percent[2]), ((1,0), flame_percent[3]), ((0,1), flame_percent[3]), ((1,1), flame_percent[4])];
    elif angle > 68 and angle <= 113:
        return [((-1,0), flame_percent[0]), ((-1,-1), flame_percent[1]), ((-1,1), flame_percent[1]), ((0,-1), flame_percent[2]), ((0,1), flame_percent[2]), ((1,-1), flame_percent[3]), ((1,1), flame_percent[3]), ((1,0), flame_percent[4])];
    elif angle > 113 and angle <= 158:
        return [((-1,1), flame_percent[0]), ((-1,0), flame_percent[1]), ((0,1), flame_percent[1]), ((-1,-1), flame_percent[2]), ((1,1), flame_percent[2]), ((0,-1), flame_percent[3]), ((1,0), flame_percent[3]), ((1,-1), flame_percent[4])];
    elif angle > 158 and angle <= 203:
        return [((0,1), flame_percent[0]), ((1,1), flame_percent[1]), ((-1,1), flame_percent[1]), ((1,0), flame_percent[2]), ((-1,0), flame_percent[2]), ((1,-1), flame_percent[3]), ((-1,-1), flame_percent[3]), ((0,-1), flame_percent[4])];
    elif angle > 203 and angle <= 248:
        return [((1,1), flame_percent[0]), ((1,0), flame_percent[1]), ((0,1), flame_percent[1]), ((1,-1), flame_percent[2]), ((-1,1), flame_percent[2]), ((0,-1), flame_percent[3]), ((-1,0), flame_percent[3]), ((-1,-1), flame_percent[4])];
    elif angle > 248 and angle <= 292:
        return [((1,0), flame_percent[0]), ((1,-1), flame_percent[1]), ((1,1), flame_percent[1]), ((0,1), flame_percent[2]), ((0,-1), flame_percent[2]), ((-1,1), flame_percent[3]), ((-1,-1), flame_percent[3]), ((-1,0), flame_percent[4])];
    else:
        return [((1,-1), flame_percent[0]), ((1,0), flame_percent[1]), ((0,-1), flame_percent[1]), ((1,1), flame_percent[2]), ((-1,-1), flame_percent[2]), ((0,1), flame_percent[3]), ((-1,0), flame_percent[3]), ((-1,1), flame_percent[4])];
    

# initialize the forest grid as a np array full of zeros
grid = np.zeros((sizex, sizey))

# add in initial random coverage
grid[1:sizey -1, 1:sizex-1] = np.random.random(size=(sizey-2, sizex-2)) < init_coverage

# plot the grid
fig = plt.figure(figsize=(12.8, 9.6)) #temp size
ax = fig.add_subplot(111)
# create room for a slider
fig.subplots_adjust(bottom=0.20)
# create sliders for p, f and wind_angle
paxslider = fig.add_axes((0.25, 0.1, 0.50, 0.03))
pslider = Slider(ax=paxslider, label="p", valmin=0.00, valmax=0.1, valinit=0.05)

faxslider = fig.add_axes((0.25, 0.075, 0.50, 0.03))
fslider = Slider(ax=faxslider, label="f", valmin=0.00, valmax=0.005, valinit=0.0001)

waxslider = fig.add_axes((0.25, 0.05, 0.50, 0.03))
wslider = Slider(ax=waxslider, label="wind angle", valmin=0, valmax=359, valinit=0)

wislider = fig.add_axes((0.25, 0.025, 0.50, 0.03))
wislider = Slider(ax=wislider, label="wind intensity", valmin=0, valmax=5, valinit=0, valstep=1)

ax.set_axis_off()
im = ax.imshow(grid, cmap, norm=norm)


# update the sliders
def update_p(val):
    global p
    p = pslider.val
    fig.canvas.draw_idle()

pslider.on_changed(update_p)

def update_f(val):
    global f
    f = fslider.val
    fig.canvas.draw_idle()

fslider.on_changed(update_f)

def update_wind_angle(val):
    global wind_angle
    wind_angle = wslider.val
    fig.canvas.draw_idle()

wslider.on_changed(update_wind_angle)

def update_wind_intensity(val):
    global wind_intensity
    global wind_change
    wind_intensity = wislider.val
    wind_change = True
    fig.canvas.draw_idle

wislider.on_changed(update_wind_intensity)

# Animation
def animate(i):
    im.set_data(animate.grid)
    animate.grid = update(animate.grid)

animate.grid = grid

# interval in ms
interval = 80
anim = animation.FuncAnimation(fig, animate, interval=interval, frames=200)
# YIPPEE IT WORKED!!!AHHH
plt.show()

# next? probably start incorporating different trees!
