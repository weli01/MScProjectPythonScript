import pandas as pd
import statistics
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from math import sqrt
from sklearn.metrics import r2_score
from decimal import *
import statsmodels.api as sm
import scipy.stats as stats

# Load MCP crystal data and RaySafe data from CSV files
TLD = pd.read_csv('data/MCP.csv', encoding='ANSI')
RaySafe = pd.read_csv('data/RaySafe.csv')

# Letter labelling for subplots
subtitle = ['(a)', '(b)', '(c)']

# Obtain kVp and dose values from RaySafe dosimeter
kVp = RaySafe[['kVp_1', 'kVp_2', 'kVp_3']].mean(axis=1)
dose_mean = RaySafe[['dose_1', 'dose_2', 'dose_3']].mean(axis=1)
dose_std = RaySafe[['dose_1', 'dose_2', 'dose_3']].std(axis=1)

# Obtain tube output and tube out standard deviation
tube_output = [value / 10 for value in dose_mean]
tube_output_std = [value / 10 for value in dose_std]

# Extract counts of the study and control crystals and subtract controls
counts = pd.Series([TLD.iloc[[i], 10].squeeze() for i in range(9, 81, 3)])
control = pd.Series([TLD.iloc[[i], 10].squeeze() for i in range(81, 90, 3)]).mean()
counts -= control

# Calculate mean and standard deviation of the counts
cts_mean = [statistics.mean(counts[i:i + 3]) for i in range(0, len(counts), 3)]
cts_stdev = [statistics.stdev(counts[i:i + 3]) for i in range(0, len(counts), 3)]

# Create a figure and gridspec layout for the subplots
fig = plt.figure(figsize=(9.5, 6))
gs = GridSpec(nrows=2, ncols=4)

# Add subplots in the grid spec
axs = [fig.add_subplot(gs[0, 1:3]),
       fig.add_subplot(gs[1, :2]),
       fig.add_subplot(gs[1, 2:4])]

# Function for plotting and fitting models
def plot_fn(i, x, y, yerr, xerr):
    '''
    :param i: corresponds to plot a, b or c
    :param x: x-axis data
    :param y: y-axis data
    :param yerr: x-axis data uncertainty
    :param xerr: y-axis data uncertainty
    :return: None
    '''

    if i == 0:
        # Quadratic fit
        X = np.column_stack((x ** 2, x, np.ones_like(x)))
    else:
        # Linear fit
        X = sm.add_constant(x)

    # Obtain linear/quadratic equation and corrrelation coefficient
    model = sm.OLS(y, X).fit()
    f = np.poly1d(np.polyfit(x, y, 2 if i == 0 else 1))
    R2 = r2_score(y, f(x))

    # Plot data points, error bars, and trendline
    axs[i].scatter(x, y, color='#0554f2', s=25, linewidths=1)
    axs[i].errorbar(x, y, yerr=yerr, xerr=xerr, fmt='o', color='#07bdfa', capsize=4, elinewidth=0.8, markeredgewidth=0.8, zorder=-1, ms=0.1, alpha=.7)
    axs[i].plot(x, f(x), linestyle='-', linewidth=0.7, color='#07bdfa', zorder=-2)

    # Display equation and R2 on plots
    if i == 0:
        equation_text = rf'$y={Decimal(f.c[0]).quantize(Decimal(".001"), rounding=ROUND_HALF_UP)}x^2$'
        equation_text += rf' ${Decimal(f.c[1]).quantize(Decimal(".001"), rounding=ROUND_HALF_UP)}x$' if f.c[1] < 0 else rf' + ${Decimal(f.c[1]).quantize(Decimal(".001"), rounding=ROUND_HALF_UP)}x$'
        equation_text += rf' ${Decimal(f.c[2]).quantize(Decimal(".001"), rounding=ROUND_HALF_UP)}$' if f.c[2] < 0 else rf' + ${Decimal(f.c[1]).quantize(Decimal(".001"), rounding=ROUND_HALF_UP)}$'
    else:
        equation_text = rf'$y={Decimal(f.c[0]/1000000).quantize(Decimal(".001"), rounding=ROUND_HALF_UP)}$e6$x$'
        equation_text += rf' ${Decimal(f.c[1]/1000000).quantize(Decimal(".001"), rounding=ROUND_HALF_UP)}$e6' if f.c[1] < 0 else rf' + ${Decimal(f.c[1]/1000000).quantize(Decimal(".001"), rounding=ROUND_HALF_UP)}$e6'

    axs[i].text(0.02, 0.92, equation_text, transform=axs[i].transAxes, color='grey', fontsize=12)
    axs[i].text(0.02, 0.82, rf'$R^2={R2:.4f}$', transform=axs[i].transAxes, color='grey', fontsize=12)

    # Configure title, axis labels, limits, ticks, and formatting
    axs[i].set_title(subtitle[i], x=0.955, y=0.01, weight='bold')
    axs[i].set_xlabel('Tube Output [µGy/mAs]' if i == 1 else 'Tube Voltage [kVp]')
    if i != 2:
        axs[i].set_ylabel('Tube Output [µGy/mAs]' if i == 0 else 'MCP TL intensity [cts]')
    axs[i].set_xticks(range(20, 121, 10) if i == 1 else range(50, 121, 10))
    axs[i].set_xticks(range(20, 121, 5) if i == 1 else range(50, 121, 5), minor=True)
    axs[i].set_yticks(range(20, 121, 20) if i == 0 else range(500000, 3500001, 500000))
    axs[i].set_yticks(range(20, 121, 10) if i == 0 else range(500000, 3500001, 250000), minor=True)
    if i != 0:
        axs[i].yaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        axs[i].ticklabel_format(axis='y', style='sci', scilimits=(6, 6), useOffset=True)

# Plot output vs kVp, TL intensity vs output, and TL intensity vs kVp
plot_fn(0, kVp, tube_output, tube_output_std, None)
plot_fn(1, tube_output, cts_mean, cts_stdev, tube_output_std)
plot_fn(2, kVp, cts_mean, cts_stdev, None)

# Adjust layout and save the figure
plt.subplots_adjust(top=0.98, bottom=0.07, left=0.06, right=0.995, hspace=0.3, wspace=0.2)
plt.savefig('results/relationships.pdf')
