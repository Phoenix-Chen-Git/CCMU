# CCMU: CRISPR-Cas9 Off‑target Prediction
![Cover](docs/Cover.png)

## Overview
CCMU (Combined Multi-feature Unified model) is a Transformer-based classifier for predicting CRISPR-Cas9 off-target activity. The model integrates nucleotide sequence context with ten epigenetic tracks and is trained using five-fold cross-validation. This repository provides scripts to download the example dataset and to run inference using the released weights.

## Data Sources
### Table 1. Data Sources
| Epigenetic Feature | Source Database | Sample ID      | File Size |
|--------------------|-----------------|---------------|------------------|
| ATAC-seq           | ENCODE          | ENCFF615UQB   | 248 MB           |
| CTCF ChIP-seq      | GEO             | GSM2423745    | 1.6 GB           |
| DNase-seq          | GEO             | GSM1008573    | 3.2 GB           |
| H3K4me3 ChIP-seq   | GEO             | GSM2711412    | 225 MB           |
| H3K27ac ChIP-seq   | GEO             | GSM2711409    | 336 MB           |
| H3K4me1 ChIP-seq   | GEO             | GSM4287413    | 196 MB           |
| H3K9me3 ChIP-seq   | GEO             | GSM1624501    | 172 MB           |
| H3K36me3 ChIP-seq  | GEO             | GSM2643621    | 450 MB           |
| H3K27me3 ChIP-seq  | GEO             | GSM3907592    | 162 MB           |
| RRBS               | ENCODE          | ENCSR794HFF   | 28 MB            |
## Hyperparameters
### Table 2. Main Hyperparameters
| Hyperparameter Name         | Value               | Description                                    |
|----------------------------|---------------------|------------------------------------------------|
| Input Channels              | 18                  | 10 epigenetic features + 8 sequence features   |
| Sequence Length             | 23                  | sgRNA binding sequence + PAM sequence          |
| Transformer Layers          | 3                   | Three consecutive attention encodings          |
| Attention Heads per Layer   | 8                   | Each attention layer uses 8 heads              |
| Hidden Layer Dimension      | 256                 | Embedding dimension per sample                 |
| Feedforward Hidden Dim      | 512                 | Feedforward network hidden layer dimension     |
| Dropout                     | 0.1                 | Prevent overfitting                            |
| Initial Learning Rate       | 0.0001              | Learning rate at the start of training         |
| Weight Decay                | 0.01                | Each update reduces parameter by 1%            |
| Positive:Negative Weight Ratio | 2:1              | Positive sample weight is twice negative sample|
| Training Epochs             | 300                 | Number of cross-validation training epochs     |
| Samples per Epoch           | 800 (400+400)       | 400 positive and 400 negative samples per epoch|
## Model Architecture
**Figure 1. Model Architecture**
<p align="center">
  <img src="docs/Model_architecture.png" alt="model architecture"/>
</p>

## Benchmark on MIT and CFD Datasets
### Table 3. MIT Algorithm Metrics
| Fold | FNR Constraint | FPR    | ROC-AUC | PR-AUC |
|------|---------------|--------|---------|--------|
| 1    | FNR=0.1       | 1.0000 | 0.681   | 0.110  |
| 2    | FNR=0.1       | 0.5120 | 0.720   | 0.101  |
| 3    | FNR=0.1       | 1.0000 | 0.672   | 0.100  |
| 4    | FNR=0.1       | 1.0000 | 0.707   | 0.128  |
| 5    | FNR=0.1       | 0.5150 | 0.704   | 0.106  |
### Figure 2. MIT: FNR and FPR vs. Cutoff
<table align="center">
  <tr>
    <td align="center">
      <img src="docs/MIT/FNR_FPR_vs_Cutoff.jpg" width="350"/><br>
      <b>a. FNR and FPR vs. Cutoff</b>
    </td>
    <td align="center">
      <img src="docs/MIT/ROC_Curve.jpg" width="350"/><br>
      <b>b. ROC Curve</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="docs/MIT/PR_Curve.jpg" width="350"/><br>
      <b>c. PR Curve</b>
    </td>
    <td align="center">
      <img src="docs/MIT/MIT_confusion.jpg" width="350"/><br>
      <b>d. Confusion matrix</b>
    </td>
  </tr>
</table>

### Table 4. CFD algorithm metrics
| Fold | FNR Constraint | FPR    | ROC-AUC | PR-AUC |
|------|---------------|--------|---------|--------|
| 1    | FNR=0.1       | 0.720  | 0.825   | 0.230  |
| 2    | FNR=0.1       | 0.576  | 0.801   | 0.203  |
| 3    | FNR=0.1       | 0.886  | 0.794   | 0.279  |
| 4    | FNR=0.1       | 0.590  | 0.832   | 0.242  |
| 5    | FNR=0.1       | 0.589  | 0.826   | 0.270  |
### Figure 3. CFD: FNR and FPR vs. Cutoff
<table align="center">
  <tr>
    <td align="center">
      <img src="docs/CFD/FNR_FPR_vs_Cutoff.jpg" width="350"/><br>
      <b>a. FNR and FPR vs cutoff</b>
    </td>
    <td align="center">
      <img src="docs/CFD/ROC_Curve.jpg" width="350"/><br>
      <b>b. ROC Curve</b>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="docs/CFD/PR_Curve.jpg" width="350"/><br>
      <b>c. PR Curve</b>
    </td>
    <td align="center">
      <img src="docs/CFD/CFD_confusion.jpg" width="350"/><br>
      <b>d. Confusion matrix</b>
    </td>
  </tr>
</table>

### Table 5. Mixed model five-fold cross-validation metrics
| Fold | FNR Constraint |  FPR    | ROC-AUC | PR-AUC |
|------|---------------|---------|---------|--------|
| 1    | FNR < 0.1     | 0.0694  | 0.97    | 0.14   |
| 2    | FNR < 0.1     | 0.0789  | 0.97    | 0.11   |
| 3    | FNR < 0.1     | 0.0553  | 0.97    | 0.11   |
| 4    | FNR < 0.1     | 0.0742  | 0.96    | 0.09   |
| 5    | FNR < 0.1     | 0.1446  | 0.97    | 0.13   |
### Figure 4. Combined Model Performance
<table align="center">
  <tr>
    <td align="center" colspan="2">
      <img src="docs/combined_model/example.png" width="500"/><br>
      <b>a. One sample</b>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <img src="docs/combined_model/combine_Loss&accuracy.png" width="730"/><br>
      <b>b. Loss & accuracy over iterations</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="350">
      <img src="docs/combined_model/combine_ROC.png" width="350"/><br>
      <b>c. ROC Curve</b>
    </td>
    <td align="center" width="350">
      <img src="docs/combined_model/combine_PR.png" width="350"/><br>
      <b>d. PR Curve</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="350">
      <img src="docs/combined_model/combine_FNR_FPR.png" width="350"/><br>
      <b>e. FNR & FPR over iteration</b>
    </td>
    <td align="center" width="350">
      <img src="docs/combined_model/Confusion_matrix.png" width="350"/><br>
      <b>f. Confusion Matrix</b>
    </td>
  </tr>
</table>

### Table 6. Epigenetic-only model five-fold cross-validation metrics
| Fold | FNR Constraint |  FPR    | ROC-AUC | PR-AUC |
|------|---------------|---------|---------|--------|
| 1    | FNR < 0.1     | 0.5709  | 0.83    | 0.02   |
| 2    | FNR < 0.1     | 0.5923  | 0.86    | 0.03   |
| 3    | FNR < 0.1     | 0.3681  | 0.85    | 0.02   |
| 4    | FNR < 0.1     | 0.3501  | 0.86    | 0.03   |
| 5    | FNR < 0.1     | 0.5748  | 0.83    | 0.03   |
### Figure 5. Epigenetic-only Model Performance
<table align="center">
  <tr>
    <td align="center" colspan="2">
      <img src="docs/epi_only_model/epi_only_exsample.png" width="500"/><br>
      <b>a. One sample</b>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <img src="docs/epi_only_model/epi_loss.png" width="730"/><br>
      <b>b. Loss & accuracy over iterations</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="350">
      <img src="docs/epi_only_model/epi_roc.png" width="350"/><br>
      <b>c. ROC Curve</b>
    </td>
    <td align="center" width="350">
      <img src="docs/epi_only_model/epi_pr.png" width="350"/><br>
      <b>d. PR Curve</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="350">
      <img src="docs/epi_only_model/epi_fnr_fpr.png" width="350"/><br>
      <b>e. FNR & FPR over iteration</b>
    </td>
    <td align="center" width="350">
      <img src="docs/epi_only_model/epi_confusion_matrix.png" width="350"/><br>
      <b>f. Confusion Matrix</b>
    </td>
  </tr>
</table>

### Table 7. Sequence-only model five-fold cross-validation metrics
| Fold | FNR Constraint |  FPR    | ROC-AUC | PR-AUC |
|------|---------------|---------|---------|--------|
| 1    | FNR < 0.1     | 0.0390  | 0.99    | 0.31   |
| 2    | FNR < 0.1     | 0.0316  | 0.99    | 0.40   |
| 3    | FNR < 0.1     | 0.0393  | 0.99    | 0.40   |
| 4    | FNR < 0.1     | 0.0340  | 0.99    | 0.36   |
| 5    | FNR < 0.1     | 0.0348  | 0.99    | 0.40   |
### Figure 6. Sequence-only Model Performance
<table align="center">
  <tr>
    <td align="center" colspan="2">
      <img src="docs/seq_only_model/seq_exsample.png" width="500"/><br>
      <b>a. One sample</b>
    </td>
  </tr>
  <tr>
    <td align="center" colspan="2">
      <img src="docs/seq_only_model/seq_loss.png" width="730"/><br>
      <b>b. Loss & accuracy over iterations</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="350">
      <img src="docs/seq_only_model/seq_roc.png" width="350"/><br>
      <b>c. ROC Curve</b>
    </td>
    <td align="center" width="350">
      <img src="docs/seq_only_model/seq_PR.png" width="350"/><br>
      <b>d. PR Curve</b>
    </td>
  </tr>
  <tr>
    <td align="center" width="350">
      <img src="docs/seq_only_model/seq_FNR_FPR.png" width="350"/><br>
      <b>e. FNR & FPR over iteration</b>
    </td>
    <td align="center" width="350">
      <img src="docs/combined_model/Confusion_matrix.png" width="350"/><br>
      <b>f. Confusion Matrix</b>
    </td>
  </tr>
</table>

## Comparison Across Models
![Model comparison](docs/Comparision_between_models.png)

## Attention Mechanism
## Positive
![Positive layer1](docs/Positive_attention/layer_1.png)
![Positive layer2](docs/Positive_attention/layer_2.png)
![Positive layer3](docs/Positive_attention/layer_3.png)
## Negative
![Negative layer1](docs/Negative_attention/layer_1.png)
![Negative layer2](docs/Negative_attention/layer_2.png)
![Negative layer3](docs/Negative_attention/layer_3.png)

## Acknowledgments
I gratefully thank my parents for supporting this project and providing the funds to rent cloud servers for model training.

Due to the current low level of interest in this repository, updates will be infrequent. If the project reaches 20 stars, development will resume with improvements such as an evolved tensor generator, additional protocols, and better architectures.
