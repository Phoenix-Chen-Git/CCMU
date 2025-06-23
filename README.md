# CCMU

This repository contains scripts to download data and run inference for a pre-trained transformer model that predicts CRISPR on/off-target activity from both sequence and epigenomic features.

## Repository structure

- `download.sh` – fetches all required data and model weights from Zenodo.
- `download_scripts/` – individual helper scripts called by `download.sh`.
- `infer_combined.py` – runs inference using both sequence and epigenetic channels.
- `infer_epi_only.py` – evaluates the model when sequence channels are ablated.
- `infer_seq_only_model.py` – evaluates the model when epigenetic channels are ablated.

Each inference script loads the five pre-trained models, normalizes the input tensors and reports metrics such as the confusion matrix, ROC curve and precision–recall curve.

## Getting started

1. **Install dependencies**
   Ensure Python with PyTorch, `numpy`, `scikit-learn`, `matplotlib` and `seaborn` is installed.

2. **Download data and weights**
   ```bash
   bash download.sh
   ```
   This creates `epi_data`, `mean_std`, `train_test_data` and `weights` directories and downloads the files from Zenodo.

3. **Run inference**
   ```bash
   python infer_combined.py
   ```
   Adjust the command to run any of the other inference scripts. Results are displayed with plots.

## License

The code is released under the MIT License.
