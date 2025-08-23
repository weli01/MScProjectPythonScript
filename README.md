# BSc Project Python Script 
<img src="umlogo_full_red.png" width="200">

## Description

Repository for storing all the Python code implemented in my BSc (Hons.) in Physics, Medical Physics and Radiation Protection project titled "**Setup and operation of a thermoluminescent dosimetry system for patient organ dosimetry**."
This code was used to both analyse the data and generate plots.

The code was excuted on **PyCharm 2021.2.2** running **Python 3.9**.

## Structure

There are 6 top folders. The first folder contains the files needed for producing the annealing heat profiles and the other five are related to each stage carried out during the project.

In each folder you will find the following:
- _data_ folder: contains the data produced either by the oven or the TLD reader
- _results_ folder: contains plots (numerical results are printed out*)
- _scripts_: the .py files containg the scripts for each individual task
- _README_: a short description of each stage

*For ease, most results were printed directly in a very raw format. These have been omitted from the final code for conciseness. However, if one wishes to format the output more neatly or save it to a CSV file, they can refer to the example in _data_analysis.py_ of stage 1 (lines 44-57).

## Packages
The packages and their versions used for this project are listed below:
```
animation==0.0.7
brokenaxes==0.6.1
contourpy==1.2.1
cycler==0.10.0
et-xmlfile==1.1.0
fonttools==4.53.0
importlib-resources==6.4.0
joblib==1.2.0
kaleido==0.2.1
kiwisolver==1.3.2
matplotlib==3.9.0
mpmath==1.2.1
numpy==1.23.0
opencv-python==4.7.0.72
openpyxl==3.0.9
packaging==23.2
pandas==1.3.3
patsy==0.5.6
Pillow==8.3.2
plotly==5.13.0
PyAudio==0.2.12
pychalk==2.0.1
pydicom==2.2.2
pyparsing==2.4.7
python-dateutil==2.8.2
pytz==2021.3
researchpy==0.3.6
scikit-learn==1.1.3
scipy==1.7.1
seaborn==0.11.2
shapely==2.0.1
six==1.16.0
sklearn==0.0.post1
statsmodels==0.14.1
sympy==1.11.1
tenacity==8.2.1
threadpoolctl==3.1.0
xlrd==2.0.1
youtube-dl==2021.12.17
zipp==3.19.2
```

## License

This project is licensed under the MIT License.
