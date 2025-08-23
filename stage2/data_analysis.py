import pandas as pd
import statistics
from math import sqrt
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Define the heating rates and their corresponding strings
HRs = [[2, 5, 10], [2, 10, 20]]
HRs_str = [['2', '5', '10'], ['2', '10', '20']]

# Load MCP and MTS crystal data from CSV files and store them in lists
MCP = [pd.read_csv(f'data/MCP (HR{i}).csv', encoding='ANSI') for i in HRs[0]]
MTS = [pd.read_csv(f'data/MTS (HR{i}).csv', encoding='ANSI') for i in HRs[1]]

# Define crystal names for plotting
crystal_names = ['MCP', 'MTS']

# Function to plot confidence interval for each seperate heating rate
def plot_CI(ax, x, counts, control, colour_dp, colour_ci, title, add_labels):
    '''
    :param ax: axis object to plot on
    :param x: x-coordinate of the plot
    :param counts: data counts
    :param colour_dp: colour of data points
    :param colour_ci: colour of confidence interval
    :param title: title of the subplot
    :param add_labels: boolean flag to add legend labels only once
    :return: None
    '''

    # Compute mean and standard deviation
    mean, stdev = statistics.mean(counts), statistics.stdev(counts)

    # Compute connfidence interval (t=2.57 for 95% conf. lvl and df=5 since n=6)
    CI = 2.57 * stdev / sqrt(len(counts))

    # Print results
    print(f'\033[4m{title}\033[0m:\n'
          f'Mean = {mean:.0f} \u00B1 {CI:.0f}\n'
          f'CI = {CI * 100 / mean:.1f}%\n'
          f'Counts: {counts.to_list()}\n'
          f'Control: {control}\n\n'
          f'{"-" * 50}\n')

    # Plot the confidence interval and mean counts
    if add_labels: # to have only 1 set of labels for each crystal material
        ax.errorbar(x, mean, yerr=CI, fmt='o', color=colour_ci, capsize=5, markersize=0.1, zorder=-1, label='CI')
        ax.scatter(x, mean, color=colour_dp, label='Mean counts')
    else:
        ax.errorbar(x, mean, yerr=CI, fmt='o', color=colour_ci, capsize=5, zorder=-1)
        ax.scatter(x, mean, color=colour_dp)

# Create a figure and gridspec layout for the subplots
fig = plt.figure(figsize=(8.5, 3.5))
gs = GridSpec(1, 2)

# Main loop to process each crystal and generate plots
for i, crystal in enumerate([MCP, MTS]):

    # Add a subplot in the grid spec
    ax = fig.add_subplot(gs[0, i])

    # Plot confidence interval for each heating rate
    for counter, HR in enumerate(crystal):
        counts = pd.Series([HR.iloc[[j], 10].squeeze() for j in range(0, 18, 3)])
        control = int(pd.Series([HR.iloc[[j], 10].squeeze() for j in range(19, 21, 3)]).mean())
        #counts -= control
        plot_CI(ax, counter + 1, counts, control, '#0554f2' if i == 0 else 'darkorange', '#07bdfa' if i == 0 else 'orange', f'{crystal_names[i]} (HR{HRs_str[i][counter]})', counter == 0)

    # Set x-axis ticks and labels
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(HRs_str[i])

    # Set plot title and axis labels
    ax.set_title(f'{crystal_names[i]}', x=0.09 if i == 0 else 0.91, y=0.89, weight='bold', fontsize=14)
    ax.set_xlabel('Heating Rate [°C/s]')
    if i == 0:
        ax.set_ylabel('TL Intensity [cts]')

    # Format y-axis to use scientific notation
    ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(6, 6), useOffset=True)

    # Add legend
    ax.legend(loc='upper left', bbox_to_anchor=(0.001 if i == 0 else 0.58, 0.92), fontsize=9.5)

# Adjust layout and save the figure
plt.subplots_adjust(top=0.94, bottom=0.12, left=0.08, right=0.98, hspace=0.05, wspace=0.2)
plt.savefig('results/CIplots.pdf')
