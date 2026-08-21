import skrf as rf
import math
import sys
import numpy as np
from matplotlib import pyplot as plt


# define dB function for S-parameters
def dB(value):
    return 20.0*np.log10(np.abs(value))        

# define phase function for S-parameters
def phase(value):
    return np.angle(value, deg=True) 

# get one S-parameter item over frequency
def Sxx(network,m,n):
    return network.s[:,m-1,n-1]

# reflection coefficient magnitude shown in the zoomed Smith chart window
ZOOM_GAMMA = 0.5

# shared light grid-line style, used for both the full and zoomed Smith chart
GRID_COLOR = 'lightgrey'
GRID_LW = 0.8

# constant-resistance/-reactance grid values for the zoomed Smith chart,
# denser than skrf's default labeled grid ([0.2, 0.5, 1, 2, 5])
ZOOM_GRID_VALUES = [0.2, 0.5, 1.0, 1.5, 2.0, 3.0]

# draw a denser Smith chart grid for the zoomed view, with labels placed where
# each grid circle crosses the real (for r) or imaginary (for x) axis, since
# skrf's own label placement is designed for the full chart and would fall
# outside the zoomed axis limits
def draw_zoomed_smith_grid(ax, gamma):
    from matplotlib.patches import Circle

    ax.axhline(0, color='grey', lw=0.5)

    for r in ZOOM_GRID_VALUES:
        center = (r/(1+r), 0)
        radius = 1/(1+r)
        ax.add_patch(Circle(center, radius, ec=GRID_COLOR, fc='none', lw=GRID_LW))
        label_pos = center[0] - radius
        if abs(label_pos) < gamma:
            ax.annotate(f"{r:g}", xy=(label_pos, 0), xytext=(label_pos, 0.01),
                        fontsize=8, color='dimgrey', ha='center', va='bottom')

    for sign in (1, -1):
        for x in ZOOM_GRID_VALUES:
            xv = sign * x
            center = (1, 1/xv)
            radius = abs(1/xv)
            ax.add_patch(Circle(center, radius, ec=GRID_COLOR, fc='none', lw=GRID_LW))
            if radius >= 1:
                # crossing point with the imaginary axis nearest the origin
                y0 = 1/xv - math.copysign(math.sqrt(radius**2 - 1), 1/xv)
                if abs(y0) < gamma:
                    ax.annotate(f"{xv:g}j", xy=(0, y0), xytext=(0.01, y0),
                                fontsize=8, color='dimgrey', ha='left', va='center')

    ax.plot(gamma*np.array([-1.1, 1.1]), gamma*np.array([-1.1, 1.1]), 'w.', markersize=0)

# plot a Smith chart figure with one subplot per reflection parameter
def plot_smith_figure(reflection_params, networks, colors, linestyles, title, zoomed=False):
    if len(reflection_params) > 1:
        fig_s, axes_s = plt.subplots(1, len(reflection_params), figsize=(5*len(reflection_params), 5))
    else:
        fig_s, axes_s = plt.subplots(1, 1, figsize=(5, 5))
    fig_s.suptitle(title)

    for a, param in enumerate(reflection_params):
        m = param[0]
        n = param[1]
        ax = axes_s[a] if len(reflection_params) > 1 else axes_s

        if zoomed:
            draw_zoomed_smith_grid(ax, ZOOM_GAMMA)
            for i,network in enumerate(networks):
                data = Sxx(network,m,n)
                ax.plot(data.real, data.imag, color=colors[i], linestyle=linestyles[i], label=network.name)
            ax.set_xlim(-ZOOM_GAMMA, ZOOM_GAMMA)
            ax.set_ylim(-ZOOM_GAMMA, ZOOM_GAMMA)
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            for i,network in enumerate(networks):
                network.plot_s_smith(m-1, n-1, ax=ax, show_legend=False, draw_labels=True,
                                      color=colors[i], linestyle=linestyles[i], label=network.name)
            # skrf draws the grid circles with hardcoded colors (black for r=0/1, x=+-1);
            # recolor them to match the zoomed chart's uniform light grid style
            for patch in ax.patches:
                patch.set_edgecolor(GRID_COLOR)
                patch.set_linewidth(GRID_LW)

        ax.set_title(f"S{m}{n}")
        ax.set_aspect('equal')
        ax.legend()

    plt.tight_layout()
    return fig_s


# This dict is used to identify the plot function 
# At the moment, this is hard coded in plot section (dB and phase) and not specified via command line
functions = {
    "DB": dB,
    "PHASE": phase,
    "ANG": phase
}


print('Read S-Parameter files and plot selected S-params')

# evaluate commandline
networks = []
parameters = []
smith_mode = False
zoom_mode = False

# read all files specified in command line
for arg in sys.argv[1:]:

    if '.s' in arg:
        # this is an S-parameter file
        network = rf.Network(arg)
        f = network.frequency.f
        networks.append(network)

        # shorted name if file name is too long
        if len(arg)>17:
            network.name = network.name[:10] + '..' + network.name[-20:]

    elif arg.upper() in ('-SMITH', '--SMITH'):
        # plot reflection parameters (Snn) as Smith chart in a separate window
        smith_mode = True
        print('Smith chart plotting enabled for reflection parameters (Snn)')

    elif arg.upper() in ('-ZOOM', '--ZOOM'):
        # additionally plot a Smith chart zoomed to |Gamma|<=0.5 in a separate window
        zoom_mode = True
        print('Zoomed Smith chart window enabled for reflection parameters (Snn)')

    elif arg[0].upper() == 'S':
        # this is control which S-parameter(s) to plot
        l = len(arg)-1 # length of numbers in Sxx parameter
        half = int(math.floor(l/2)) # length of one row/column specifier

        m = int(arg[1:half+1])
        n = int(arg[half+1:l+1])
        parameters.append([m,n])

        print(f'Specified S-parameter: {m},{n}')



# default is S11 if nothing specified
if len(parameters) == 0:
    parameters.append([1,1])


# set wide plot if we have 3 or more parameters
if len(parameters) > 2:
    fig, axes = plt.subplots(2, len(parameters), figsize=(14, 8))  # NxN grid
else:
    fig, axes = plt.subplots(2, len(parameters), figsize=(10, 8))  # NxN grid

fig.suptitle("S Parameters")

colors = ['b', 'r', 'm', 'c', 'g', 'y', 'k', 'w']
linestyles = ['solid', 'dashed', 'dashdot', 'dotted','solid', 'dashed', 'dashdot', 'dotted']


for a, param in enumerate(parameters):
    m = param[0]
    n = param[1]

    func = 'dB'
    if len(parameters) > 1:
        ax = axes[0,a]
    else:
        ax = axes[0]
    for i,network in enumerate(networks):
        data = functions[func.upper()](Sxx(network,m,n))
        freq = network.frequency.f/1e9
        ax.plot(freq , data, color = colors[i], linestyle=linestyles[i], label=network.name)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel(f"{func} S{m}{n}")
    ax.set_xmargin(0)
    ax.legend()
    ax.grid()

    func = 'phase'
    if len(parameters) > 1:
        ax = axes[1,a]
    else:
        ax = axes[1]
    for i,network in enumerate(networks):
        data = functions[func.upper()](Sxx(network,m,n))
        freq = network.frequency.f/1e9
        ax.plot(freq , data, color = colors[i], linestyle=linestyles[i], label=network.name)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel(f"{func} S{m}{n}")
    ax.set_xmargin(0)
    ax.legend()
    ax.grid()

plt.tight_layout()

# Smith chart(s) for reflection parameters (Snn) in separate window(s)
if smith_mode or zoom_mode:
    reflection_params = [p for p in parameters if p[0] == p[1]]
    if reflection_params:
        if smith_mode:
            plot_smith_figure(reflection_params, networks, colors, linestyles, "Smith Chart", zoomed=False)
        if zoom_mode:
            plot_smith_figure(reflection_params, networks, colors, linestyles, "Smith Chart (zoomed)", zoomed=True)
    else:
        print('No reflection S-parameters (Snn) selected, skipping Smith chart')

plt.show()

