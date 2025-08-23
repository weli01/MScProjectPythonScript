import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# MCP and MTS crystal data from CSV files
MCP = pd.read_csv('data/MCP.csv', encoding='ANSI')
MTS = pd.read_csv('data/MTS.csv', encoding='ANSI')

# Define crystal names for plot
crystal_names = [[r'MCP w/o N$_2$', r'MCP w/ N$_2$'],
                 [r'MTS w/o N$_2$', r'MTS w/ N$_2$']]

# Define mAs values and associated linestyles
mAs = [5, 10, 20, 50, 100]
ls = [(0, (2, 4)), '-.', ':', '--', '-']

# Create a figure with two subplots sharing the same x-axis
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 7))

# Iterate through crystals
for i, crystal in enumerate([MCP, MTS]):

    # Define time range and crystal count parameters based on crystal index
    time_params = (0, 31.4, 315) if i == 0 else (0, 57.4, 575)
    count_params = (13, 328) if i == 0 else (13, 588)

    # Extract time data
    time = np.linspace(*time_params)

    # Extract temperature data
    temp = pd.Series(crystal.iloc[[2], slice(*count_params)].squeeze().values)

    # Initialise lists to store means and standard deviations
    index = 0
    means = []
    stdevs = []

    # Extract count data for the current mAs range
    all_count = pd.DataFrame([crystal.iloc[[i], slice(*count_params)].squeeze().values for i in range(0, 89, 3)])

    for j in range(2):

        if j == 0:
            n = 0
        else:
            n = 3

        # Iterate through mAs values
        for ctp in mAs:

            count = all_count.iloc[index+n:index+n+3]

            # Compute mean and standard deviation of counts
            mean_cnt = count.mean()
            st_dev = count.std(axis=0)

            # Append results to lists
            means.append(mean_cnt)
            stdevs.append(st_dev)

            index += 6
        index = 0

    # Choose the appropriate axis for the current crystal
    axA = ax1 if i == 0 else ax3
    axB = ax2 if i == 0 else ax4

    # Plot mean counts against time for axA and axB
    for j in range(5):
        axA.plot(time, means[j], color='#0554f2' if i == 0 else 'darkorange', label=f'{mAs[j]} mAs', linestyle=ls[j])
        axA.fill_between(time, means[j] - stdevs[j], means[j] + stdevs[j], color='#07bdfa' if i == 0 else 'orange', alpha=0.2)
        axB.plot(time, means[j + 5], color='#0554f2' if i == 0 else 'darkorange', label=f'{mAs[j]} mAs', linestyle=ls[j])
        axB.fill_between(time, means[j + 5] - stdevs[j + 5], means[j + 5] + stdevs[j + 5], color='#07bdfa' if i == 0 else 'orange', alpha=0.2)

    # Common settings for axA and axB
    for ax in [axA, axB]:
        ax.set_xlim(time_params[:2])
        ax.set_ylim(0, 52E4 if i == 0 else 1.6e4)
        ax.minorticks_on()
        ax.set_axisbelow(True)
        ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(axis='y', style='sci', scilimits=(4, 4), useOffset=True)

        # Create twin y-axis for temperature against time
        ax_twin = ax.twinx()

        # Show temperature label and ticks only on plots on the right
        if ax == axB:
            ax_twin.set_ylabel(r'Temperature [$^{\circ}$C]')
        else:
            ax_twin.set_yticklabels([])

        # Plot temperature against time
        ax_twin.plot(time, temp, color='red', linestyle='-', linewidth=0.5, alpha=0.5)

        # Adjust limits and set maximum temperature to red
        max_T = 240 if i == 0 else 300
        default_ticks = [tick for tick in ax_twin.get_yticks() if tick != 300] if i == 1 else [tick for tick in ax_twin.get_yticks()]
        ax_twin.set_yticks(default_ticks + [max_T])
        ax_twin.set_ylim(0, 249 if i == 0 else 320)
        ax_twin.get_yticklabels()[list(ax_twin.get_yticks()).index(max_T)].set_color('red')
        ax_twin.tick_params(axis='y')

    # Set specific labels and titles
    axA.legend(loc='upper left', title='Current-time', fontsize=8.5, bbox_to_anchor=(0.001, 0.925))
    axA.set_ylabel('Count rate [cps]')
    axA.set_title(crystal_names[i][0], weight='bold', x=0.015, y=0.90, fontsize=14, ha='left')
    axB.set_yticklabels([])
    axB.set_title(crystal_names[i][1], weight='bold', x=0.015, y=0.90, fontsize=14, ha='left')

# Set the common x-axis label
ax3.set_xlabel(r'Time [s]')
ax4.set_xlabel(r'Time [s]')

# Adjust layout and save figure
fig.subplots_adjust(top=0.98, bottom=0.03, left=0.07, right=0.99, hspace=0.13, wspace=0.05)
plt.savefig(f'results/glowcurves.pdf', bbox_inches='tight')
