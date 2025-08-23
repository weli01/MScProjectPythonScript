import pandas as pd
import statistics
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

# Load MCP and MTS crystal data from CSV files and store them in lists
MCP, MTS = [pd.read_csv(f'data/{data}.csv', encoding='ANSI') for data in ('MCP', 'MTS')]

# Define crystal names, colours, markers, labels, and text location for plotting
crystal_names = ['MCP and MTS', 'MCP', 'MTS']
colour = [['#0554f2', '#07bdfa'], ['#fa6007', 'orange']]
markers = [['<', '>'], ['^', 'v']]
label = [['MCP w/o N$_2$', 'MCP w/ N$_2$'], ['MTS w/o N$_2$', 'MTS w/ N$_2$']]
location = [[[63, 16.5E6], [83, 15.5E6]], [[80, -0.1E6], [80, 1.1E6]]]

# Define mAs values
mAs = [5, 10, 20, 50, 100]

# Initialise empty matrices
means, stdevs, CVs, LIs, LIs_error, grads, ys, Rs = [[[0, 0], [0, 0]] for _ in range(8)]

# Iterate through crystals
for i, crystal in enumerate([MCP, MTS]):
    counts = pd.Series([crystal.iloc[[i], 10].squeeze() for i in range(0, 89, 3)])

    # Iterate through use and no use of Nitrogen
    for j in range(2):

        # Handle special case for MTS with nitrogen (error in readout for first crystal of 5 mAs)
        if i == 1 and j == 1:
            mean = [statistics.mean(counts[4:6])] + [statistics.mean(counts[i:i + 3]) for i in range(9, len(counts), 6)]
            stdev = [statistics.stdev(counts[4:6])] + [statistics.stdev(counts[i:i + 3]) for i in range(9, len(counts), 6)]
        else:
            mean = [statistics.mean(counts[i:i + 3]) for i in range(0 if j == 0 else 3, len(counts), 6)]
            stdev = [statistics.stdev(counts[i:i + 3]) for i in range(0 if j == 0 else 3, len(counts), 6)]

        # Calculate mean and standard deviation of the counts
        means[i][j], stdevs[i][j] = mean, stdev

        # Calculate coefficient of variation
        CV = pd.Series(stdev) / pd.Series(mean) * 100

        # Calculate the Pearson correlation
        R, _ = pearsonr(mAs, mean)

        # Obtain gradient and y-intercept from linear relationship
        coeffs = np.polyfit(mAs, mean, 1)
        f = np.poly1d(coeffs)
        y = f(mAs)

        stdevs[i][j], CVs[i][j], grads[i][j], ys[i][j], Rs[i][j] = stdev, CV, coeffs[0], y, R

# Create the figure and grids for subplots
fig = plt.figure(figsize=(9.5, 6))
gs = GridSpec(nrows=2, ncols=2, width_ratios=[4, 3])

# Create subplots
axs = [fig.add_subplot(gs[:, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])]

# Plot data on each subplot for TL Intensity
for i in range(3):

    # Configure axis labels, limits, ticks, and formatting
    axs[i].minorticks_on()
    axs[i].set_xlim(-3, 103)
    axs[i].set_xticks(range(0, 101, 10))
    axs[i].set_xticks(range(0, 101, 5), minor=True)
    axs[i].yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True)) # scientific notation
    axs[i].ticklabel_format(axis='y', style='sci', scilimits=(6, 6), useOffset=True)

    if i == 0 or i == 2:
        axs[i].set_xlabel('Current-Time [mAs]')
    if i == 0:
        axs[i].set_ylabel('TL Intensity [cts]')

    for j in range(2):
        for k in range(2):
            if i == 2:
                j = 1

            # Plot data points, error bars, and trendline
            axs[i].scatter(mAs, means[j][k], facecolors='w', edgecolors=colour[j][k], s=25, marker=markers[j][k], label=label[j][k], linewidths=1)
            axs[i].errorbar(mAs, means[j][k], yerr=stdevs[j][k], fmt='o', color=colour[j][k], capsize=5, elinewidth=1, markeredgewidth=1, zorder=-1, ms=0.1)
            axs[i].plot(mAs, ys[j][k], linestyle='--' if k == 0 else (0, (2, 4)), linewidth=0.7, color=colour[j][k], zorder=-2)

            # Show R^2 in the main plot
            if i == 0:
                axs[i].text(location[j][k][0], location[j][k][1], rf'$R^2={Rs[j][k]:.4f}$', fontsize=10,
                            color=colour[j][k])

        if i == 1 or i == 2:
            break

    # Plot legend
    axs[i].legend(fontsize=11)

# Adjust layout and save the figure
plt.subplots_adjust(top=0.97, bottom=0.07, left=0.07, right=0.99, hspace=0.2, wspace=0.1)
plt.savefig(f'results/linearity_plot.pdf')

# Print relative sensitivity calculations
print(f'\nRelative sensitivity crystals: {grads[0][1] / grads[1][1]:.2f}\n'
      f'Relative sensitivity MCP: {grads[0][1] / grads[0][0]:.2f}\n'
      f'Relative sensitivity MTS: {grads[1][1] / grads[1][0]:.2f}\n')

# Print differences in CVs
CVs = [item for sublist in CVs for item in sublist]

print(f'Difference in CVs')
for i, crystal in enumerate([MCP, MTS]):
    print('-' * 40)
    print(f'\033[4m{"MCP" if i == 0 else "MTS"}\033[0m')
    print('{:>7s}{:>7s}{:>7s}{:>7s}'.format('mAs', 'w/o', 'w', 'diff'))
    for j, mAs_value in enumerate(mAs):
        idx = i * 2
        print('{:>7d}{:>7.2f}{:>7.2f}{:>7.2f}'.format(mAs_value, CVs[idx][j], CVs[idx + 1][j], (CVs[idx + 1][j] - CVs[idx][j])))
    print()