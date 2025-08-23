import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

# Define the heating rates and their corresponding strings
HRs = [[2, 5, 10], [2, 10, 20]]
HRs_str = [[' 2', ' 5', '10'], [' 2', '10', '20']]

# Define crystal names and linestyles for plotting
crystal_names = ['MCP', 'MTS']
linestyle = ['-', '--', ':']

# Load MCP and MTS crystal data from CSV files and store them in lists
MCP = [pd.read_csv(f'data/MCP (HR{i}).csv', encoding='ANSI') for i in HRs[0]]
MTS = [pd.read_csv(f'data/MTS (HR{i}).csv', encoding='ANSI') for i in HRs[1]]

# Create a figure with two subplots stacked vertically
fig = plt.figure(figsize=(8, 6))
gs = GridSpec(2, 1)

# Iterate through crystals
for i, (crystal, name) in enumerate(zip([MCP, MTS], crystal_names)):

    # Add a subplot in the grid spec
    ax1 = fig.add_subplot(gs[i, 0])

    # To handle each heating rate for each crystal material separately
    for counter, HR in enumerate(crystal):

        # Define time range and crystal count parameters based on crystal index
        time_params = (0, (len(HR.axes[1]) - 19) / 10, len(HR.axes[1]) - 18)
        count_params = (13, len(HR.axes[1]) - 5)

        # Extract time and count data
        time = np.linspace(*time_params)
        count = pd.DataFrame([HR.iloc[[i], slice(*count_params)].squeeze().values for i in range(0, 18, 3)])

        # Extract temperature data
        temp = pd.Series(HR.iloc[[2], slice(*count_params)].squeeze().values)

        # Compute mean and standard deviation of crystal counts
        mean_cnt, st_dev = count.mean(), count.std(axis=0)

        # Obtain index of maximum count and obtain corresponding temperature
        temp_peak_index = mean_cnt.idxmax(axis=0)
        temp_peak = temp.loc[temp_peak_index]

        # Print results
        if HRs[i][counter] == 2:
            print(f'\nTemperature at peak count of {crystal_names[i]}')
        else:
            None
        print(f'HR{HRs_str[i][counter]}: {temp_peak:.1f}')

        # Normalise data
        norm_mean_cnt, norm_st_dev = mean_cnt / max(mean_cnt), st_dev / max(mean_cnt)

        # Plot mean counts against time
        ax1.plot(temp, norm_mean_cnt, color='#0554f2' if i == 0 else 'darkorange', linestyle=linestyle[counter], label=rf'$\beta={HRs_str[i][counter]}$°C/s')
        ax1.fill_between(temp, (norm_mean_cnt - norm_st_dev), (norm_mean_cnt + norm_st_dev), color='#07bdfa' if i == 0 else 'orange', alpha=0.2)

    # Set up twin axes ax2 (time) and ax3 (temperature on y-axis)
    ax2 = ax1.twiny()
    ax3 = ax1.twinx()

    # Items in tuples for both ax2 and ax3:
    # 1,2 = two values defining the limits for the x-axis
    # 3 = list of tick positions
    # 4 = list of tick labels corresponding to the positions
    ax2_params = [(0, 12, [9, 9.6, 10.2, 10.8, 11.4, 12], [0, 2, 4, 6, 8, 10]),
                  (0, 11, [6, 6 + 5 / 6, 6 + 10 / 6, 6 + 15 / 6, 6 + 20 / 6, 6 + 25 / 6, 11], [0, 5, 10, 15, 20, 25, 30])]
    ax3_params = [(60, 300, [60, 90, 120, 150, 180, 210, 240, 270, 300], [60, 90, 120, 150, 180, 210, 240, 270, 300], [60, 240, 240]),
                  (60, 360, [60, 120, 180, 240, 300, 360], [60, 120, 180, 240, 300, 360], [60, 300, 300])]

    # Configure ax2 and ax3
    ax2.set_xlim(*ax2_params[i][:2])
    ax2.set_xticks(ax2_params[i][2])
    ax2.set_xticklabels(ax2_params[i][3])

    ax3.set_ylim(*ax3_params[i][:2])
    ax3.set_yticks(ax3_params[i][2])
    ax3.set_yticklabels(ax3_params[i][3])

    # Plot heat profile
    ax3.plot([60, 240, 300] if i == 0 else [60, 300, 500], ax3_params[i][4], 'r', linewidth=1, alpha=0.5)

    # Set ticks and labels for ax1
    major_ticks = np.arange(60, 241, 20) if i == 0 else np.arange(60, 301, 40)
    minor_ticks = np.arange(260, 301, 20) if i == 0 else np.arange(340, 501, 40)
    ax1.set_xticks(np.concatenate((major_ticks, minor_ticks)))
    ax1.set_xticklabels([str(tick) for tick in np.concatenate((major_ticks, [240 if i == 0 else 300] * len(minor_ticks)))])

    # More axes properties
    ax1.legend(loc='upper left', bbox_to_anchor=(0.001, 0.9))
    ax1.set_xlabel(r'Temperature [°C]')
    ax2.set_xlabel(r'Time [s]', x=0.87)
    ax3.set_ylabel(r'Temperature [°C]')
    ax1.set_ylabel('Relative count rate [cps]')
    ax1.set_axisbelow(True)
    ax1.minorticks_on()
    ax1.set_xlim(60, 300 if i == 0 else 500)
    ax1.set_ylim(0, 1.2)

    # Set maximum tempreature on right y-axis to red
    yticks = ax3.yaxis.get_major_ticks()
    yticks[-3 if i==0 else -2].set_visible(False)
    ax3.set_yticks(np.append(ax3.get_yticks(), 240 if i == 0 else 300))
    tick_labels = ax3.get_yticklabels()
    tick_labels[-1].set_color('red')

    # Set y-axis limits on the right
    if i == 0:
        ax3.set_ylim(60, 250)
    else:
        ax3.set_ylim(60, 320)

    # Set subplot title
    ax1.set_title(f'{name}', size=14, x=0.045, y=0.86, weight='bold')

# Adjust layout and save the figure
plt.subplots_adjust(top=0.97, bottom=0.03, left=0.07, right=0.98, hspace=0.35)
plt.savefig('results/glowcurves.pdf', bbox_inches='tight')
