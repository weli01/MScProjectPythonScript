import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.gridspec as gridspec

# Load MCP and MTS crystal data from CSV files
MCP = pd.read_csv('data/MCP.csv', encoding='ANSI')
MTS = pd.read_csv('data/MTS.csv', encoding='ANSI')

# Define the names of the crystals and percentage difference ranges
crystal_names = ['MCP', 'MTS']
PD_names = ['  >15', '10-15', ' 5-10', '   <5']

# Create a figure and gridspec layout for the subplots
fig = plt.figure(figsize=(8, 5.2))
gs = fig.add_gridspec(2, 1, hspace=0)

# Function to extract crystal information, calculates statistics, and stores results.
def process_crystal(crystal, control, is_mcp):
    '''
    :param crystal: df containing crystal data
    :param control: series of control counts for adjustment
    :param is_mcp: flag indicating if crystal is MCP for adjusment
    :return: results, sorted_crystals, median, MAD, control
    '''

    # Extract the crystal number and counts from the data
    crystal_num = pd.Series([crystal.iloc[i, 5] for i in range(0, 98, 3)])
    counts = pd.Series([crystal.iloc[i, 10] for i in range(0, 98, 3)])

    # Adjust counts by subtracting the mean control value for MCP crystals
    if is_mcp:
        counts -= statistics.mean(control)

    # Calculate the median and median absolute deviation of the counts
    median = statistics.median(counts)
    MAD = stats.median_abs_deviation(counts)

    # Calculate the percentage difference from the median
    PD = ((counts - median) / median) * 100

    # Create a dataframe to store the results
    results = pd.DataFrame({
        'crystal_num': crystal_num,
        'counts': counts,
        'difference': counts - median,
        'PD': PD.round(2),
        'PD_abs': abs(PD)
    }).sort_values('PD_abs', ascending=False)

    # Convert certain columns to integers
    results[['crystal_num', 'counts', 'difference']] = results[['crystal_num', 'counts', 'difference']].astype(int)

    print(f'\033[4m{crystal_name}\033[0m:\n'
          f'{results.to_string(index=False)}\n')


    # Sort the crystals by the absolute difference from the median
    sorted_crystals = abs(counts - median).sort_values(ascending=False)

    return results, sorted_crystals, median, MAD, control


# Function to print percentage difference ranges
def print_non_nan_values(df, PD_names):
    '''
    :param df: df containing percentage difference values
    :param PD_names: names of the percentage difference ranges
    '''
    # Print the non-NaN values in each column of the DataFrame
    for name, column in enumerate(df.columns):
        values = [(i + 1, v) for i, v in enumerate(df[column]) if not pd.isna(v)]
        formatted_values = ", ".join(f"[#{index}: {value:.1f}]" for index, value in values)
        print(f'{PD_names[name]}: {formatted_values}')
    print(f'{"-" * 200}\n')


# Main loop to process each crystal and generate plots
for i, (crystal, crystal_name) in enumerate(zip([MCP, MTS], crystal_names)):

    # Extract the control counts
    control = pd.Series([crystal.iloc[i, 10] for i in range(99, 107, 3)])

    # Process the crystal data
    results, sorted_crystals, median, MAD, control = process_crystal(crystal, control, is_mcp=(i == 0))

    # Print the results for each crystal

    print(f'Median = {median:.0f} \u00B1 {MAD:.0f}\n'
          f'Control Counts = {statistics.mean(control):.0f} \u00B1 {statistics.stdev(control):.0f}\n')

    # Create a dataframe for the percentage difference ranges
    PD_ranges = pd.DataFrame({
        'r15': results['PD'][abs(results['PD']) > 15],
        'r10_15': results['PD'][(abs(results['PD']) <= 15) & (abs(results['PD']) > 10)],
        'r5_10': results['PD'][(abs(results['PD']) <= 10) & (abs(results['PD']) > 5)],
        'r5': results['PD'][abs(results['PD']) <= 5]
    })

    # Print the percentage difference ranges
    print_non_nan_values(PD_ranges, PD_names)

    # Create a subplot for each crystal
    ax = fig.add_subplot(gs[i, 0])

    # Scatter plot of the counts and plot the median line
    ax.scatter(results['crystal_num'], results['counts'], color='#0554f2' if i == 0 else 'darkorange', label='Measured counts', zorder=10)
    ax.plot(np.arange(0, 35, 1), np.full(35, median), '--', color='#07bdfa' if i == 0 else 'orange', linewidth=1, label="Median count", zorder=2)

    # Set the y-axis limits
    y_max = median + 0.25 * median
    y_min = median - 0.25 * median

    # Configure the x- and y-axis ticks
    ax.set_xticks(np.arange(1, 34, 1), minor=True)
    ax.set_xticks(np.arange(1, 34, 2), minor=False)
    ax.set_yticks(np.arange(round(y_min, -5 if i == 1 else -6), round(y_max, -5 if i == 1 else -6), 100000 if i == 1 else 1000000))
    ax.set_xlim(0, 34)
    ax.set_ylim(y_min, y_max)

    # Format the y-axis labels
    ax.yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(6, 6), useOffset=True)

    # Create a secondary y-axis for percentage difference
    axPD = ax.twinx()
    axPD.plot(results['crystal_num'], results['PD'], 'o', alpha=0)
    axPD.set_ylim(-25, 25)
    axPD.set_yticks(np.arange(-15, 16, 5), minor=False)

    # Add horizontal lines for percentage difference thresholds
    for j in [-15, -10, -5, 5, 10, 15]:
        axPD.axhline(j, 0, 34, linestyle='--', linewidth=0.7, alpha=0.3, color='grey', zorder=1)

    # Add arrows to 3 crystals with greatest deviation
    for k in range(3):
        ax.annotate('', (results.iloc[k]['crystal_num']+0.1, results.iloc[k]['counts']),
                    xytext=(13, 6),  # Reverse the direction and adjust the position
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle='-|>', color='red', lw=1))

    # Set axis labels, title and legend
    ax.set_xlabel('Crystal Number')
    ax.set_ylabel('TL Intensity [cts]')
    axPD.set_ylabel('PD [%]')
    ax.set_title(crystal_name, weight='bold', x=0.04, y=0.875, fontsize=14)
    ax.legend(fontsize=8.5)

# Adjust layout and save the figure
plt.subplots_adjust(top=0.95, bottom=0.08, left=0.07, right=0.92, hspace=0.1, wspace=0.3)
plt.savefig('results/intercrystal.pdf')

