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
    return network.s[:,m,n]


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
    m = param[0]-1
    n = param[1]-1
        
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
plt.show()

