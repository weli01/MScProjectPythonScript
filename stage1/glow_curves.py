import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# MCP and MTS crystal data from CSV files
MCP = pd.read_csv('data/MCP.csv', encoding='ANSI')
MTS = pd.read_csv('data/MTS.csv', encoding='ANSI')

# Define crystal names for plot
crystal_names = ['MCP', 'MTS']

# Create a figure with two subplots sharing the same x-axis
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

# Iterate through crystals
for i, (crystal, name, ax) in enumerate(zip([MCP, MTS], crystal_names, [ax1, ax2])):

    # Define time range and crystal count parameters based on crystal index
    time_params = (0, 31.4, 315) if i == 0 else (0, 57.4, 575)
    count_params = (13, 328) if i == 0 else (13, 588)

    # Extract time and count data
    time = np.linspace(*time_params)
    count = pd.DataFrame([crystal.iloc[[i], slice(*count_params)].squeeze().values for i in range(0, 98, 3)])

    # Extract temperature data
    temp = pd.Series(crystal.iloc[[2], slice(*count_params)].squeeze().values)

    # Compute mean and standard deviation of crystal counts
    mean_cnt = count.mean()
    st_dev = count.std(axis=0)

    # Plot mean counts against time
    ax.plot(time, mean_cnt, color='#0554f2' if i == 0 else 'darkorange', label=f'Mean counts')
    ax.fill_between(time, mean_cnt - st_dev, mean_cnt + st_dev, color='#07bdfa' if i == 0 else 'orange', alpha=0.2, label=r'SD')

    # Create a secondary y-axis for temperature and adjust ticks
    ax_temp = ax.twinx()
    ax_temp.set_ylabel(r'Temperature [$^{\circ}$C]')
    ax_temp.plot(time, temp, linestyle='--', linewidth=1, label=f'Heat profile', color='red')
    ax_temp.set_ylim(0, 250 if i ==0 else 350)
    yticks = ax_temp.yaxis.get_major_ticks()
    yticks[-1 if i == 0 else -2].set_visible(False)
    ax_temp.set_yticks(np.append(ax_temp.get_yticks(), 240 if i == 0 else 300))
    tick_labels = ax_temp.get_yticklabels()
    tick_labels[-1].set_color('red')

    # Set the properties of the primary y-axis
    ax.set_ylabel('Count rate [cps]')
    ax.set_xlim(time_params[:2])
    ax.set_ylim(0)
    ax.minorticks_on()
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(4, 4), useOffset=True)

    # Combine legends for this subplot
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax_temp.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc='upper left', fontsize=9, bbox_to_anchor=(0.001, 0.925))

    # Set title
    ax.set_title(crystal_names[i], weight='bold', x=0.04, y=0.895, fontsize=14)

# Set the common x-axis label
ax2.set_xlabel(r'Time [s]')

# Adjust layout and save the figure
fig.subplots_adjust(top=0.98, bottom=0.03, left=0.07, right=0.99, hspace=0.17, wspace=0.1)
plt.savefig('results/glowcurves.pdf', bbox_inches='tight')