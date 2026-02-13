# Colony matters: How density shapes predator access in two Antarctic fur seal (*Arctocephalus gazella*) colonies

**Authors:** Johannes Bartl, Ane Liv Berthelsen, Alexander Winterl, Cameron Fox-Clarke, Jaume Forcada, Rebecca Nagel, Joseph I. Hoffman, Ben Fabry

[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXX)

This repository contains the code, models, and analysis scripts associated with the paper **"Colony matters: How density shapes predator access in two Antarctic fur seal (*Arctocephalus gazella*) colonies"**.

## Repository Structure

### Code & Notebooks
* **`training.ipynb`**: Pipeline to train the YOLOv8 neural network.
* **`analysis.ipynb`**: Main analysis script for generating statistical results and figures.

### Models
* **`model.pt`**: Trained YOLOv8-large weights file used to predict the full dataset.

### Data & Detections
* **`FWB.csv`**: Neural network detection results for Freshwater Beach.
* **`SSB.csv`**: Neural network detection results for Special Study Beach.

### Map Data
* **`FWB.kml` / `FWB.png` / `FWB_v1.cdb`**: Georeferencing and annotation data for Freshwater Beach.
* **`SSB.kml` / `SSB.png` / `SSB_v1.cdb`**: Georeferencing and annotation data for Special Study Beach.
* **`both_areas.kml` / `both_areas.png` / `both_areas_v1.cdb`**: Combined map data.

## Dataset Access (Zenodo)

The raw imagery and primary annotation databases are hosted on Zenodo.

**Dataset DOI:** [10.5281/zenodo.XXXXXX](https://doi.org/10.5281/zenodo.XXXXXX)

The Zenodo dataset includes:
1.  **Raw Imagery:** 110 high-resolution `.jpg` images.
2.  **Annotations:** Corresponding `.cdb` (ClickPoints) databases containing ground-truth annotations.

## Analysis & Figures

The `analysis.ipynb` notebook reproduces the following key results:

* **(a) Temporal trends in abundance at Special Study Beach** (Figure 2)
* **(b) Abundance ratios of birds to pups between colonies** (Figure 3)
* **(c) Demographic patterns in seal density** (Figure 4)
* **(d) Spatial associations between birds and pups** (Figure 5)