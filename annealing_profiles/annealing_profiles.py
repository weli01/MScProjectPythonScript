import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Load pre- and post-irradiation annealing data from Excel files
anneals = [
    'data/MTS Pre-Irradiation.xlsx',
    'data/MCP Pre-Irradiation.xlsx',
    'data/MCP MTS Post-Irradiation.xlsx'
]

# Function to extract time, set temperature and delivered temprature from Thermosoft data
def data_extractor(data):
    '''
    :param data: path to data Excel file
    :return: time in minutes, preset temperature, actual temperature
    '''

    # Import annealing data from excel file using pandas
    data = pd.read_excel(data, 1)

    # Assign time of measurement, preset temperature and actual temperature
    time = pd.to_datetime(data['Unnamed: 0'][2:], format='%d/%m/%Y %H:%M:%S')
    preset = data['Controller1SP'][2:]
    actual = data['Controller1'][2:]

    # Find the minimum date and time in the column
    min_datetime = time.min()

    # Calculate the time difference from the minimum date and time and convert to minutes
    time = (time - min_datetime).dt.total_seconds() / 60

    return time, preset, actual

# Extract data for each anneal
MTS_pre = data_extractor(anneals[0])
MCP_pre = data_extractor(anneals[1])
MCPMTS_post = data_extractor(anneals[2])

# Organise all profiles into one list
profiles = [MTS_pre, MCP_pre, MCPMTS_post]

# Titles for figure subplots
plot_titles = ['MTS Pre-Irradiation', 'MCP Pre-Irradiation', 'MCP & MTS Post-Irradiation']

# Colours for plotting
colours = ['k', 'r']  # black for preset temp; red for actual temp

# Create the figure and grids for subplots
fig = plt.figure(figsize=(9, 8))
gs = GridSpec(nrows=3, ncols=1)

# Create subplots
axs = [
    fig.add_subplot(gs[0, 0]),
    fig.add_subplot(gs[1, 0]),
    fig.add_subplot(gs[2, 0])
]

# Plot data on each subplot
for i in range(3):
    time = profiles[i][0]
    temp = [profiles[i][1], profiles[i][2]]  # [preset, actual]

    # Plot settings
    for j in range(2):
        axs[i].plot(time, temp[j], colours[j])
    axs[i].set_ylabel(r'$T$ [$^{\circ}$C]')
    axs[i].minorticks_on()
    axs[i].grid(which='major', linestyle='-', linewidth='0.5', alpha=0.5)
    axs[i].set_axisbelow(True)
    axs[i].set_title(plot_titles[i], x=0, y=1, weight='bold', horizontalalignment='left', fontsize=14)
    if i == 0:
        axs[i].legend(['Set heat profile', 'Delivered heat profile'])
    if i == 2:
        axs[i].set_xlabel(r'$t$ [min]')

# Adjust layout and save the figure
plt.subplots_adjust(top=0.96, bottom=0.06, left=0.065, right=0.995, hspace=0.35, wspace=0.1)
plt.savefig(f'results/heat_profiles.pdf')