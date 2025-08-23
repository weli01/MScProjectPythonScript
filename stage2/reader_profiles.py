import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# MCP and MTS crystal data from Excel files
data = pd.read_excel('data/reader.xlsx', 0)

# Extract 'time' data
time = data['time']

# Create dataframe for MCP and MTS heating rates
MCP_HRs = pd.DataFrame(data[['MCP1', 'MCP2', 'MCP3']]).T
MTS_HRs = pd.DataFrame(data[['MTS1', 'MTS2', 'MTS3']]).T

# Assign data to each column
MCP1, MCP2, MCP3 = [data[f'MCP{i}'].dropna().reset_index(drop=True) for i in range(1, 4)]
MTS1, MTS2, MTS3 = [data[f'MTS{i}'].dropna().reset_index(drop=True) for i in range(1, 4)]

# All profiles in one list and assocaited heating rates
profiles = [[MCP1, MCP2, MCP3],
            [MTS1, MTS2, MTS3]]
HRs = [[2, 5, 10],
       [2, 10, 20]]

# Define tiles and linestyles for plotting
plot_titles = ['MCP Readout', 'MTS Readout']
style = ['-.', '--', ':']

# Create a figure and gridspec layout for the subplots
fig = plt.figure(figsize=(8, 6))
gs = GridSpec(nrows=2, ncols=1)

# Add subplots in the grid spec
axs = [fig.add_subplot(gs[0, 0]),
       fig.add_subplot(gs[1, 0])]

# Plot data on each subplot
for i in range(2): # for each material
    for j in range(3): # for each heating rate
        axs[i].plot(time[:len(profiles[i][j])], profiles[i][j], ls=style[j], color='r', label=rf'{HRs[i][j]}')

    # Set axes parameters (labels, ticks, limits)
    if i == 1:
        axs[i].set_xlabel(r'$t$ [s]')
    if i == 0:
        axs[i].set_yticks(range(0, 241, 40))
        axs[i].set_yticks(range(0, 241, 10), minor=True)
    axs[i].set_ylabel(r'$T$ [$^{\circ}$C]')
    axs[i].set_xlim(xmin=0)
    axs[i].set_ylim(ymin=0)
    axs[i].get_yticklabels()[list(axs[i].get_yticks()).index(240 if i == 0 else 300)].set_weight('bold')

    # Set grid parameters
    axs[i].grid(which='major', linestyle='-', linewidth='0.5', alpha=0.5)
    axs[i].set_axisbelow(True)
    axs[i].minorticks_on()

    # Set title and legend
    axs[i].set_title(plot_titles[i], x=0, y=1, weight='bold', horizontalalignment='left', fontsize=14)
    axs[i].legend(title=r'$\beta$ [°C/s]', loc=4)

# Adjust layout and save the figure
plt.subplots_adjust(top=0.95, bottom=0.08, left=0.08, right=0.99, hspace=0.31, wspace=0.1)
plt.savefig(f'results/reader_heat_profiles.pdf')
