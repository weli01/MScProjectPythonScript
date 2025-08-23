## Annealing Profiles

For generating annealing heat profiles from oven data.

The data folder contains 6 Excel files. For every annealing process there are 2 files: **original** and **edited**. 
The originals are the files with the raw data as produced by the oven software (Thermosoft).
The edited files have their _Set Temperature_ (Controller1SP) changed such that a linear ramp from 0 to the maximum temperature is plotted (the Thermosoft software had an issue with this, thus it had to be corrected manually).
The edited files were used as the input data for the script.
