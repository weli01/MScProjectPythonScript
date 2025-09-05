# BSc Project Python Script 
<img src="umlogo_full_red.png" width="200">


## Description

This repository contains the Python code developed as part of my M.Sc. Medical Physics project:
**“Environmental dose evaluation following the installation of a SPECT/CT scanner in a major public hospital using Monte Carlo simulation.”**

The codebase was used for both data analysis and visualisation.

Development and execution were carried out in **PyCharm 2024.3.3** with **Python 3.12**.


## Structure

At the top level, the project includes three directories and two standalone scripts:

* **`data/`**
  Contains isotope-specific subdirectories (`tc99m/` and `lu177/`) with simulation outputs.

* **`data_analysis/`**
  Holds the core analysis scripts for different tasks, along with supporting subfolders.

* **`plot_2Dmaps/`**
  Scripts for extracting and generating 2D visualisations, plus a subdirectory for storing plots.

* **`run_times.py`**
  Extracts simulation run times and particle counts, calculating the average runtime per simulation (or simulation set).

* **`update_data.py`**
  Collects relevant outputs (`tab.lis`, `bnn.lis`, and `.out` files) from the FLUKA project directory and organises them under the correct isotope subfolders in `data/`.

## Packages
The packages and their versions installed in the used PyCharm environment are listed below:
```
choreographer   1.0.9
contourpy       1.3.1
cycler          0.12.1
Deprecated      1.2.18
et_xmlfile      2.0.0
fonttools       4.56.0
imageio         2.37.0
joblib          1.4.2
kaleido         1.0.0
kiwisolver      1.4.8
lazy_loader     0.4
logistro        1.1.0
lxml            6.0.1
markdown-it-py  3.0.0
matplotlib      3.10.0
mdurl           0.1.2
narwhals        2.1.0
networkx        3.4.2
numpy           2.2.3
opencv-python   4.11.0.86
openpyxl        3.2.0b1
orjson          3.11.1
packaging       24.2
pandas          2.2.3
pikepdf         9.10.2
pillow          11.1.0
pip             25.2
plotly          6.2.0
Pygments        2.19.1
PyMuPDF         1.26.4
pyparsing       3.2.1
python-dateutil 2.9.0.post0
pytz            2025.1
PyWavelets      1.8.0
rich            13.9.4
scikit-image    0.25.2
scikit-learn    1.6.1
scipy           1.15.2
seaborn         0.13.2
simplejson      3.20.1
six             1.17.0
tabulate        0.9.0
threadpoolctl   3.6.0
tifffile        2025.3.13
tzdata          2025.1
wrapt           1.17.3
```

## License

This project is licensed under the MIT License.
