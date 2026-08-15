import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import animation

neighbors = [(0,1), (1,1), (1,0), (-1,0), (-1,-1), (0,-1), (-1,1), (1, -1)]
EMPTY, TREE, ONFIRE = 0,1,2
#  color list and map
color_list = ["#400f15", "#1dab07", "#ff7429"]
cmap = colors.ListedColormap(color_list)
boundaries = [0,1,2,3]
norm = colors.BoundaryNorm(boundaries, cmap.N)

# STEP 2: create an update function - EASY PEASY LEMON SQUEAZY
def update(grid):
    # fill the new grid with zeros
    new_grid = np.zeros((sizex, sizey))
    # iterate through each cell
    for ix in range(1,sizex-1):
        for iy in range(1, sizey-1):
            # if the cell is empty, probabalistically grow a tree
            if grid[iy,ix] == EMPTY and np.random.random() <= p:
                new_grid[iy,ix] = TREE
            if grid[iy,ix] == TREE:
                new_grid[iy,ix] = TREE
                # Iterate through the neighbors of the cell, checking if any are on fire
                for ny,nx in neighbors:
                    if abs(ny) == abs(nx) and np.random.random() <= 0.53:
                        continue
                    if grid[iy+ny, ix+nx] == ONFIRE:
                        new_grid[iy,ix] = ONFIRE
                        break
                else:
                    if np.random.random() <= f:
                         new_grid[iy,ix] = ONFIRE

    return new_grid


# STEP 1: create a grid in matplotlib - DONED IT
# initial fraction of a forest occupied by trees
init_coverage = 0.2
# probability of a tree growing in a cell, probability of a lightning strike
p, f = 0.05, 0.0001

# size of grid 
sizex, sizey = 100, 100

# initialize the forest grid as a np array full of zeros
grid = np.zeros((sizex, sizey))

# add in initial random coverage
grid[1:sizey -1, 1:sizex-1] = np.random.random(size=(sizey-2, sizex-2)) < init_coverage

# plot the grid
fig = plt.figure(figsize=(12.8, 9.6)) #temp size
ax = fig.add_subplot(111)
ax.set_axis_off()
im = ax.imshow(grid, cmap, norm=norm)



# STEP 3: SET UP THE ANIMATION AHH
def animate(i):
    im.set_data(animate.grid)
    animate.grid = update(animate.grid)

animate.grid = grid

# interval in ms
interval = 100
anim = animation.FuncAnimation(fig, animate, interval=interval, frames=200)
# YIPPEE IT WORKED!!!AHHH
plt.show()

