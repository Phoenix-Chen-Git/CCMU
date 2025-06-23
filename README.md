# CCMU: CRISPR-Cas9 Off‑target Prediction

CCMU (Combined Multi-feature Unified model) is a Transformer-based classifier for predicting CRISPR-Cas9 off-target activity. The model integrates nucleotide sequence context with ten epigenetic tracks and was trained using five-fold cross-validation. This repository provides scripts to download the example dataset and run inference using the released weights.

## Data overview

The training and test data originate from the open dataset used by DeepCRISPR (`https://zenodo.org/records/1246320`). It contains 535 positive off-target events and 167,472 negatives derived from multiple genome-wide assays such as GUIDE-seq and BLESS. To supply epigenetic context around each locus we processed ten bigWig tracks from ENCODE and GEO:

- ATAC‑seq
- CTCF ChIP‑seq
- DNase‑seq
- H3K9me3 ChIP‑seq
- H3K4me1 ChIP‑seq
- H3K27ac ChIP‑seq
- H3K4me3 ChIP‑seq
- H3K27me3 ChIP‑seq
- H3K36me3 ChIP‑seq
- RRBS methylation levels

For each candidate site a window of 23 bases (20 sgRNA bases plus the PAM) is encoded as a tensor of shape `[18, 23]`. Channels 1–10 correspond to the epigenetic signals while channels 11–14 and 15–18 hold one‑hot encodings of the sgRNA and off‑target sequences respectively. Epigenetic channels are z‑score normalised.

## Model architecture

The classifier is an encoder‑only Transformer with the following configuration:

- Input dimension: 18 channels per position
- Sequence length: 23 bases
- Three encoder layers
- Eight attention heads per layer
- Hidden dimension: 256
- Feed‑forward dimension: 512
- Dropout: 0.1

Outputs from all positions are average pooled and passed through a sigmoid‑activated linear layer to obtain the off‑target probability. Training used weighted binary cross‑entropy with positive samples given twice the weight of negatives. Each fold sampled 400 positives and 400 negatives per epoch for 300 epochs, and the best model was selected with the constraint that the false negative rate (FNR) remained below 0.1.

## Repository contents

- `download.sh` — fetches the dataset and pre‑trained weights from Zenodo.
- `download_scripts/` — individual helper scripts called by `download.sh`.
- `infer_combined.py` — evaluate the ensemble using both sequence and epigenetic channels.
- `infer_seq_only_model.py` — inference using only sequence information.
- `infer_epi_only.py` — inference using only epigenetic tracks.
- `CCMU.yml` — conda environment listing the required Python packages.

Each inference script loads the five released models, normalises the input tensors and reports metrics including the confusion matrix, ROC curve and precision–recall curve.

## Getting started

1. **Create the environment**
   ```bash
   conda env create -f CCMU.yml
   conda activate CCMU
   ```

2. **Download data and weights**
   ```bash
   bash download.sh
   ```
   This creates `epi_data`, `mean_std`, `train_test_data` and `weights` directories containing all required files.

3. **Run inference**
   ```bash
   python infer_combined.py
   ```
   The script displays evaluation plots. Replace the script name to run the sequence‑only or epigenetic‑only models.

## License

The code is released under the MIT License.

