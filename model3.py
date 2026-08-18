import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import animation
from matplotlib.widgets import Slider, Button
from scipy import ndimage
from enum import IntEnum, Enum

"""
This program simulates a growth and burn cycle of a forest. Each cell is in one of five states:

1. Empty
2. Occupied by a tree (a conifer or a hardwood)
3. Occupied by a dormant tree
4. On fire
5. Decomposed

The probability of a tree growing vary for conifers and hardwoods to reflect the relative difference in their growth speeds. Similarly,
the probability of catching fire and the intensity of the flame vary depending on the type of tree that has been ignited. When a conifer burns,
there is a chance that it may not die off but rather become a "dormant tree", this reflects conifers' serotiny, a series of traits that allow for thier
seeds to be released and thrive after exposure to high heats. In the next growth cycle, dormant conifers grow back more quickly. This model also
allows the user to add wind and aims to simulate mosaic burn patterns.
"""


# consts, different stages
neighbors = [(0,1), (1,1), (1,0), (-1,0), (-1,-1), (0,-1), (-1,1), (1, -1)]

# kernel to use when convolve
kernel = np.array([[1,1,1],
                   [1,0,1],
                   [1,1,1]])

# tree types
class Trees(IntEnum):
    EMPTY = 0
    CONIFER = 1
    HARDWOOD = 2
    DECOMPOSED = 3
    DORMANT_CONIFER = 4

# fire types (categorized by intensity)
class Fires(IntEnum):
    FIRE1 = 5
    FIRE2 = 6
    FIRE3 = 7
    FIRE4 = 8

# initial fraction of a forest occupied by each tree
init_hardwood_coverage = 0.05
init_conifer_coverage = 0.05

# color list and map
color_list = ["#400f15", "#065C23", "#78D60C", "#40210f", "#001b06", "#40210f", "#c04530", "#ff7429", "#ffb938"]
cmap = colors.ListedColormap(color_list)
boundaries = [0,1,2,3,4,5,6, 7]
norm = colors.BoundaryNorm(boundaries, cmap.N)

# growthrates
# conifers grow on average more quickly than a hardwood
# best approx I have is that hardwoods grow at 2/3 the rate of conifers on average
hardwood_growth = 2/5

# probability of burning
conifer_burn_risk = 1.0
hardwood_burn_risk = 0.4
temp_burn_risk = [0.2, 0.4, 0.7, 1.0]

# dormancy rate
dormant_rate = 0.02

# probability of a tree dying
d = 0.03

# probability of tree growing in a cell
p = 0.05

# size of grid
sx, sy = 100, 100

# set the action initially to grow
# wind angle, 0-359 degrees, with 0 degrees pointing east
wind_angle = 0
flame_percent = [1.0, 1.0, 1.0, 1.0, 1.0] 
wind_impact = [0, 0.05, 0.12, 0.18, 0.2]

# wind intensity, between 0-5
wind_change = False
wind_intensity = 0

# -------------------------------------------------------------------------------------------------------------------------
# update growth
def grow(grid, dormant_grid):

    # fill new grid with zeros
    new_grid = np.zeros((sy,sx))

    # get species dependent grids
    conifer_trees = (grid == 1).astype(int)
    hardwood_trees = (grid == 2).astype(int)

    # convolve them to get the number of each of the trees present
    num_conifers = ndimage.convolve(conifer_trees, kernel, mode='constant', cval=0)
    num_hardwood = ndimage.convolve(hardwood_trees, kernel, mode='constant', cval=0)

    for ix in range(1, sx-1):
        for iy in range(1, sy-1):
            # if empty, check if a new tree might grow
            if grid[iy,ix] == Trees.EMPTY and np.random.random() <= p:
                new_grid[iy,ix] = select_tree((iy,ix), num_conifers, num_hardwood)

            # if arrived at a square where a tree recently decomposed, increase the chance of a new tree growing
            if grid[iy,ix] == Trees.DECOMPOSED and np.random.random() <= p*2:
                new_grid[iy,ix] = select_tree((iy,ix), num_conifers, num_hardwood)

            # if there is a tree, see if it decomposes or not
            if grid[iy,ix] == Trees.CONIFER or grid[iy,ix] == Trees.HARDWOOD or grid[iy,ix] == Trees.DORMANT_CONIFER:
                new_grid[iy,ix] = grid[iy,ix]
                if new_grid[iy,ix] == Trees.DORMANT_CONIFER:
                    new_grid[iy,ix] = Trees.CONIFER
                if np.random.random() <= d:
                    new_grid[iy,ix] = Trees.DECOMPOSED

    return new_grid, dormant_grid




# return a tree based on surrounding trees
def select_tree(square, conifers, hardwoods):
    y, x = square[0], square[1]
    if conifers[y,x] > hardwoods[y,x]:
        return Trees.CONIFER
    elif conifers[y,x] < hardwoods[y,x]:
        return Trees.HARDWOOD
    else:
        if np.random.random() <= hardwood_growth:
            return Trees.HARDWOOD
        else:
            return Trees.CONIFER





# update method, setting spark : this stops the growth method and starts the flame method
def burn(grid, dormant_grid):
    # fill new grid with zeros
    new_grid = np.zeros((sy, sx))

    # iterate through cells
    new_grid[dormant_grid] = Trees.DORMANT_CONIFER

    for ix in range(1, sx-1):
        for iy in range(1, sx-1):
            if grid[iy, ix] > Fires.FIRE1:
                new_grid[iy, ix] = get_next_fire(grid[iy, ix])
            if grid[iy, ix] == Trees.CONIFER or grid[iy, ix] == Trees.HARDWOOD:
                new_grid[iy, ix] = grid[iy, ix]
                new_grid[iy, ix] = fire_chance((iy, ix), new_grid, grid, dormant_grid)
                

    return new_grid, dormant_grid



def get_next_fire(current_fire):
    return current_fire - 1;



def fire_chance(square, new_grid, old_grid, dormant_grid):
    y, x = square[0], square[1]
    current_tree_type = new_grid[y,x]
    species_risk = conifer_burn_risk if old_grid[y,x] == Trees.CONIFER else hardwood_burn_risk
    if wind_change:
        account_wind_intensity()
    nb_percents = find_percents(wind_angle, flame_percent)
    for entry in nb_percents:
        temp_risk = get_temp(old_grid[y+entry[0][0], x+entry[0][1]])
        if np.random.random() <= species_risk * entry[1] * temp_risk:
            if current_tree_type == Trees.CONIFER:
                if np.random.random() <= dormant_rate:
                    dormant_grid[y,x] = True
                return Fires.FIRE4
            return Fires.FIRE3
            # return Fires.FIRE4 if current_tree_type == Trees.CONIFER else Fires.FIRE3

    return current_tree_type


    
def get_temp(temperature):
    if temperature <= 4:
        return 0
    return temp_burn_risk[int(temperature-5)]


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
    


# --------------------------------------------------------------------------------------------------------------------------
action = grow

# dormant tree grid
dormant_grid = np.zeros((sy,sx), dtype=bool)

# setting up grid
grid = np.zeros((sy, sx))

# add initial coverage of conifers
grid[1:sy -1, 1:sx-1] = np.random.random(size=(sy-2, sx-2)) < init_conifer_coverage

# add initial coverage of hardwoods without overwriting the conifer assignment
mask = (np.random.random(size=(sy-2, sx-2)) < init_hardwood_coverage) & (grid[1:sy-1, 1:sx-1] == 0)
grid[1:sy -1, 1:sx-1][mask] = 2

# plot the grid
fig = plt.figure(figsize=(12.8, 9.6)) #temp size
ax = fig.add_subplot(111)

# sliders and buttons etc
# create room for a slider
fig.subplots_adjust(bottom=0.20)

# create sliders 
# p slider
paxslider = fig.add_axes((0.25, 0.1, 0.50, 0.03))
pslider = Slider(ax=paxslider, label="p", valmin=0.00, valmax=0.1, valinit=0.05)

# d slider
daxslider = fig.add_axes((0.25, 0.06, 0.50, 0.03))
dslider = Slider(ax=daxslider, label="d", valmin=0.00, valmax=0.1, valinit=0.01)

# wind angle slider
waxslider = fig.add_axes((0.25, 0.08, 0.50, 0.03))
wslider = Slider(ax=waxslider, label="wind angle", valmin=0, valmax=359, valinit=0)

# wind intensity slider
waxis = fig.add_axes((0.25, 0.04, 0.50, 0.03))
wislider = Slider(ax=waxis, label="wind intensity", valmin=0, valmax=5, valinit=0, valstep=1)

ax.set_axis_off()
im = ax.imshow(grid, cmap, norm=norm)

# update sliders
def update_p(val):
    global p
    p = pslider.val
    fig.canvas.draw_idle()

pslider.on_changed(update_p)

def update_d(val):
    global d
    d = dslider.val
    fig.canvas.draw_idle()

dslider.on_changed(update_d)

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


# button to switch to a spark
buttonax = fig.add_axes((0.8, 0.015, 0.1, 0.04))
button = Button(ax=buttonax, label="Burn", hovercolor='0.975')

def switch_action(val):
    global action
    if action == grow:
        # create an initial patch to burn
        animate.grid[int(sy/2), int(sx/2)] = Fires.FIRE4
        animate.grid[int(sy/2)+1, int(sx/2)+1] = Fires.FIRE4
        animate.grid[int(sy/2)-1, int(sx/2)-1] = Fires.FIRE4
        action = burn
    else:
        action = grow

button.on_clicked(switch_action)

# animation
def animate(i):
    im.set_data(animate.grid)
    animate.grid, animate.dormant_grid = action(animate.grid, animate.dormant_grid)

animate.grid = grid
animate.dormant_grid = dormant_grid

# interval in ms
interval = 80
anim = animation.FuncAnimation(fig, animate, interval=interval, frames=200)

plt.show()