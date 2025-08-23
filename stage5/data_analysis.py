import pandas as pd
import statistics
import matplotlib as mp
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np

# Load data from CSV files and store them in lists
kVp50, kVp80 = [pd.read_csv(f'data/results{data}.csv', encoding='ANSI') for data in ('50', '80')]
RaySafe = pd.read_csv(f'data/X2.csv')

# Function to analyse data
def data_analyis(data, kVp):
    '''
    :param data: TLD data from reader
    :param kVp: 50 or 80 kVp
    :return: TLDdose_mean, TLDdose_std, SSDdose_mean, SSDdose_std
    '''

    # Obtain TLD dose data and calculate mean and standard deviation
    TLDdose = pd.Series([data.iloc[[i], 9].squeeze() for i in range(0, 45, 3)])
    TLDdose_mean = [statistics.mean(TLDdose[i::5]) for i in range(5)]
    TLDdose_std = [statistics.stdev(TLDdose[i::5]) for i in range(5)]

    # Calculate SSD dose mean and standard deviation
    SSDdose_mean = RaySafe[[f'{kVp}dose_1', f'{kVp}dose_2', f'{kVp}dose_3']].mean(axis=1)
    SSDdose_std = RaySafe[[f'{kVp}dose_1', f'{kVp}dose_2', f'{kVp}dose_3']].std(axis=1)

    return TLDdose_mean, TLDdose_std, SSDdose_mean, SSDdose_std

# Obtain results of both kVp settings using the data_analysis function
analysis_50 = data_analyis(kVp50, 50)
analysis_80 = data_analyis(kVp80, 80)

# Adding mean results from both kVp settings into one list
TLD = pd.concat([pd.Series(analysis_50[0]), pd.Series(analysis_80[0])])
SSD = pd.concat([analysis_50[2], analysis_80[2]])

# Same for standard deviation
TLD_std = pd.concat([pd.Series(analysis_50[1]), pd.Series(analysis_80[1])])
SSD_std = pd.concat([analysis_50[3], analysis_80[3]])


## Bland-Altman analysis

mean = (TLD + SSD) / 2 # Mean of doses
diff = TLD - SSD  # Difference between TLD and SSD measurments
pd = diff / SSD * 100 # Percentage difference
bias = np.mean(diff) # Mean of the differences
sd = np.std(diff, axis=0) # Standard deviation of the difference
UL = bias + 1.96*sd # Upper limit
LL = bias - 1.96*sd # Lower limit

# Formatting and printing
formatted_pd = pd.apply(lambda x: f'{x:.1f}')
print(f'Percentage Difference:\n'
      f'\033[4m50kVp\033[0m:\n'
      f'{formatted_pd[0:5].to_string(index=False)}\n'
      f'\033[4m80kVp\033[0m:\n'
      f'{formatted_pd[5:10].to_string(index=False)}')

# Adjustments for plotting
x_adjust = 5400
y_adjust = 20

# Create Bland-Altman plot
fig = plt.figure(figsize=(8, 5))
plt.scatter(mean[0:5], diff[0:5], color='#0554f2', s=120, marker='+', label='50 kVp')
plt.scatter(mean[5:10], diff[5:10], color='#fa6007', s=45, marker='x', label='80 kVp')
plt.axhline(bias, color='gray', linestyle='--', zorder=-1)
plt.axhline(y=0, color='grey', linestyle='-', linewidth=1, zorder=-1, alpha=0.3)
plt.axhline(UL, color='gray', linestyle=':')
plt.axhline(LL, color='gray', linestyle=':')

# Annotate plot with mean and limit lines
for line, pos, label in zip([UL, LL, bias], [y_adjust / 2, y_adjust / 2, y_adjust / 2],
                            ['+1.96 SD', '-1.96 SD', 'Mean']):
    plt.text(x=x_adjust, y=line + pos, s=label, ha='right', fontsize=12)
    plt.text(x=x_adjust, y=line - y_adjust * 1.5, s=f'{line:.2f}', ha='right', fontsize=12)

# Add annotations to the 80 kVp data points
plt.annotate('5 mAs', (mean.reset_index(drop=True)[5], diff.reset_index(drop=True)[5]-10), xytext=(-10, -35), textcoords='offset points', fontsize=9, arrowprops=dict(arrowstyle='-', color='black', lw=0.7))
plt.annotate('10 mAs', (mean.reset_index(drop=True)[6], diff.reset_index(drop=True)[6]+10), xytext=(-10, 25), textcoords='offset points', fontsize=9, arrowprops=dict(arrowstyle='-', color='black', lw=0.7))
plt.annotate('20 mAs', (mean.reset_index(drop=True)[7], diff.reset_index(drop=True)[7]+10), xytext=(-17, 1), textcoords='offset points', fontsize=9)
plt.annotate('50 mAs', (mean.reset_index(drop=True)[8], diff.reset_index(drop=True)[8]), xytext=(-20, -13), textcoords='offset points', fontsize=9)
plt.annotate('100 mAs', (mean.reset_index(drop=True)[9]-50, diff.reset_index(drop=True)[9]+2), xytext=(-100, 15), textcoords='offset points', fontsize=9, arrowprops=dict(arrowstyle='-', color='black', lw=0.7))

# Configure axis labels and limits, and add legend
plt.xlabel(f'Mean Dose [μGy]', fontsize=12)
plt.ylabel('Difference', fontsize=12)
plt.ylim(-400, 200)
plt.legend()

# Adjust layout and save the figure
plt.subplots_adjust(top=0.985, bottom=0.1, left=0.1, right=0.995)
plt.savefig(f'results/BA.pdf', dpi=1200)
