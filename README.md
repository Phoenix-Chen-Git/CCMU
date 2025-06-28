# CCMU: CRISPR-Cas9 Off‑target Prediction
![Cover](docs/Cover.png)
# Table of Contents
- [Overview](#overview)
- [How to Use](#how-to-use)
- [Data Sources](#data-sources)
  - [Table 1. Data Sources](#table-1-data-sources)
- [Hyperparameters](#hyperparameters)
  - [Table 2. Main Hyperparameters](#table-2-main-hyperparameters)
- [Model Architecture](#model-architecture)
- [Benchmark on MIT and CFD Datasets](#benchmark-on-mit-and-cfd-datasets)
  - [Table 3. MIT Algorithm Metrics](#table-3-mit-algorithm-metrics)
  - [Figure 2. MIT: FNR and FPR vs. Cutoff](#figure-2-mit-fnr-and-fpr-vs-cutoff)
  - [Table 4. CFD algorithm metrics](#table-4-cfd-algorithm-metrics)
  - [Figure 3. CFD: FNR and FPR vs. Cutoff](#figure-3-cfd-fnr-and-fpr-vs-cutoff)
  - [Table 5. Mixed model five-fold cross-validation metrics](#table-5-mixed-model-five-fold-cross-validation-metrics)
  - [Figure 4. Combined Model Performance](#figure-4-combined-model-performance)
  - [Table 6. Epigenetic-only model five-fold cross-validation metrics](#table-6-epigenetic-only-model-five-fold-cross-validation-metrics)
  - [Figure 5. Epigenetic-only Model Performance](#figure-5-epigenetic-only-model-performance)
  - [Table 7. Sequence-only model five-fold cross-validation metrics](#table-7-sequence-only-model-five-fold-cross-validation-metrics)
  - [Figure 6. Sequence-only Model Performance](#figure-6-sequence-only-model-performance)
- [Comparison Across Models](#comparison-across-models)
  - [Figure 7. Comparison Across Models](#figure-7-comparison-across-models)
- [Attention Mechanism](#attention-mechanism)
  - [Figure 8. Positive](#figure-8-positive)
  - [Figure 9. Negative](#figure-9-negative)
- [Acknowledgments](#acknowledgments)
- [Project Status](#project-status)
# Overview
CCMU (Combined Multi-feature Unified model) is a Transformer-based classifier for predicting CRISPR-Cas9 off-target activity. The model integrates nucleotide sequence context with ten epigenetic tracks and is trained using five-fold cross-validation. This repository provides scripts to download the example dataset and to run inference using the released weights.

# How to Use
Follow these steps to reproduce the example results:

1. **Create the environment** (requires Conda):
   ```bash
   conda env create -f CCMU.yml
   conda activate CCMU
   ```

2. **Download the data and pre-trained weights**:
   ```bash
   bash download.sh
   ```
   This runs the helper scripts in `download_scripts/` to fetch epigenetic data,
   mean and standard deviation files, training data, and weight checkpoints.

3. **Run inference** with one of the provided Python scripts:
   ```bash
   python infer_combined.py       # full model using sequence + epigenetics
   python infer_epi_only.py       # model using only epigenetic channels
   python infer_seq_only_model.py # model using only sequence information
   ```

# Data Sources
## Table 1. Data Sources
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
# Hyperparameters
## Table 2. Main Hyperparameters
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
# Model Architecture
## Figure 1. Model Architecture
<p align="center">
  <img src="docs/Model_architecture.png" alt="model architecture"/>
</p>
Schematic of the model architecture. The input tensor [N,18,23] is linearly embedded into a 256-dimensional space, followed by positional encoding and layer normalization. The processed sequence passes through three stacked transformer encoder layers, each consisting of multi-head self-attention, add & norm, and a feed-forward network (256→512→256). The output is globally pooled across the sequence dimension, then passed through a linear layer and sigmoid activation to produce the final prediction.
This design enables the model to capture contextual dependencies within sequences and output a probability score for each sample.

# Benchmark on MIT and CFD Datasets
## Table 3. MIT Algorithm Metrics
| Fold | FNR Constraint | FPR    | ROC-AUC | PR-AUC |
|------|---------------|--------|---------|--------|
| 1    | FNR=0.1       | 1.0000 | 0.681   | 0.110  |
| 2    | FNR=0.1       | 0.5120 | 0.720   | 0.101  |
| 3    | FNR=0.1       | 1.0000 | 0.672   | 0.100  |
| 4    | FNR=0.1       | 1.0000 | 0.707   | 0.128  |
| 5    | FNR=0.1       | 0.5150 | 0.704   | 0.106  |

Across the five folds, the FNR constraint of 0.1 leads to variable but generally high FPRs (ranging from 0.512 to 1.000), with moderate ROC-AUC values (0.672 to 0.720), and consistently low PR-AUCs (0.100 to 0.128).

## Figure 2. MIT Algorithm Metrics
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

Figure 2a. FNR and FPR vs. Score Cutoff:
This plot shows how the False Negative Rate (FNR) and False Positive Rate (FPR) change with respect to varying score thresholds. Despite the FNR being fixed at 0.1, the FPR remains extremely high (~1.0) across most thresholds, indicating substantial misclassification of negative instances.

Figure 2b. ROC Curve:
The Receiver Operating Characteristic (ROC) curve shows moderate performance with an Area Under the Curve (AUC) of 0.681 for Fold 1. However, this relatively high AUC is misleading due to the extremely imbalanced dataset, which inflates performance metrics that depend on true negatives.

Figure 2c. Precision-Recall (PR) Curve:
The PR curve shows very low precision at almost all recall levels, with an AUC of only 0.11. This reflects a high rate of false positives when attempting to identify true positives, consistent with the elevated FPR.

Figure 2d. Confusion Matrix:
The confusion matrix further illustrates the skewed predictions. All 33,495 negative samples were misclassified as positive (false positives), while only 106 positive samples were correctly predicted. No true negatives were identified, underscoring the extremely poor specificity.

## Table 4. CFD algorithm metrics
| Fold | FNR Constraint | FPR    | ROC-AUC | PR-AUC |
|------|---------------|--------|---------|--------|
| 1    | FNR=0.1       | 0.720  | 0.825   | 0.230  |
| 2    | FNR=0.1       | 0.576  | 0.801   | 0.203  |
| 3    | FNR=0.1       | 0.886  | 0.794   | 0.279  |
| 4    | FNR=0.1       | 0.590  | 0.832   | 0.242  |
| 5    | FNR=0.1       | 0.589  | 0.826   | 0.270  |

Across the five folds, the FPR ranges from 0.576 to 0.886, while ROC-AUC remains high (0.794 to 0.832). PR-AUC ranges from 0.203 to 0.279, consistently outperforming MIT. The model satisfies the FNR constraint while offering improved—but still imperfect—balance between precision and recall.

## Figure 3. CFD algorithm metrics
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

Figure 3a. FNR and FPR vs. Score Cutoff:
The FNR sharply drops to the target 0.1 level as the score threshold increases, while the False Positive Rate (FPR) rises quickly and saturates around 0.72. This trade-off highlights the cost of meeting the FNR constraint—many negative samples are incorrectly flagged as positives.

Figure 3b. ROC Curve:
The ROC curve for Fold 1 yields an AUC of 0.825, suggesting strong discriminative ability. However, the high ROC-AUC may be influenced by the highly imbalanced dataset, where true negatives dominate the sample space.

Figure 3c. Precision-Recall (PR) Curve:
The PR curve shows better performance than the MIT algorithm, with a PR-AUC of 0.23. Still, precision decreases substantially as recall increases, showing that many predicted positives are false.

Figure 3d. Confusion Matrix:
Of 33,495 total negatives, 24,128 were misclassified (false positives), and only 9,367 were correctly identified. Among 107 true positives, 96 were correctly predicted. This shows a marked improvement in both recall and precision relative to the MIT model, but with considerable false positives remaining.

## Table 5. Mixed model five-fold cross-validation metrics
| Fold | FNR Constraint |  FPR    | ROC-AUC | PR-AUC |
|------|---------------|---------|---------|--------|
| 1    | FNR < 0.1     | 0.0694  | 0.97    | 0.14   |
| 2    | FNR < 0.1     | 0.0789  | 0.97    | 0.11   |
| 3    | FNR < 0.1     | 0.0553  | 0.97    | 0.11   |
| 4    | FNR < 0.1     | 0.0742  | 0.96    | 0.09   |
| 5    | FNR < 0.1     | 0.1446  | 0.97    | 0.13   |

The model consistently meets the FNR constraint (<0.1) across all folds. FPR values are low (0.055–0.145), ROC-AUC remains consistently high at 0.96–0.97, and PR-AUC values range from 0.09 to 0.14. This reflects the model’s robustness and superior precision-recall tradeoff compared to MIT and CFD.

## Figure 4. Combined Model Performance
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

Figure 4a. One Sample:
A heatmap of a single input sample illustrates the input feature space, which includes chromatin accessibility (e.g., ATAC-seq), histone modifications, DNAse-seq, and sgRNA/off-site encodings across 23 sequence positions.

Figure 4b. Loss & Accuracy Over Iterations:
The model shows rapid convergence of both loss and accuracy. Training and test losses decrease smoothly across 300 epochs, with training loss reaching ~0.1. Accuracy curves show high final values: ~0.95 for training and ~0.92 for testing, suggesting effective generalization.

Figure 4c. ROC Curve:
The ROC curve for Fold 1 yields a very high AUC of 0.97, indicating excellent discriminative power between classes.

Figure 4d. Precision-Recall (PR) Curve:
Despite the high ROC-AUC, the PR-AUC remains relatively low at 0.14. This reflects the impact of class imbalance—many false positives remain despite strong separation ability.

Figure 4e. FNR and FPR Over Iterations:
Both FNR and FPR decrease sharply during early epochs. FPR stabilizes around 0.05–0.07, and FNR remains below the 0.1 constraint throughout, satisfying the target while maintaining balanced performance.

Figure 4f. Confusion Matrix:
Of 32,336 true negatives, 1,159 were falsely predicted as positives (FPR ~0.069). Among 107 true positives, 80 were correctly predicted, with 27 missed—resulting in FNR ~0.25. This mismatch suggests epoch selection might differ from the per-fold optimal point.

## Table 6. Epigenetic-only model five-fold cross-validation metrics
| Fold | FNR Constraint |  FPR    | ROC-AUC | PR-AUC |
|------|---------------|---------|---------|--------|
| 1    | FNR < 0.1     | 0.5709  | 0.83    | 0.02   |
| 2    | FNR < 0.1     | 0.5923  | 0.86    | 0.03   |
| 3    | FNR < 0.1     | 0.3681  | 0.85    | 0.02   |
| 4    | FNR < 0.1     | 0.3501  | 0.86    | 0.03   |
| 5    | FNR < 0.1     | 0.5748  | 0.83    | 0.03   |

The FPR ranges from 0.35 to 0.59 across folds, with ROC-AUC between 0.83–0.86. PR-AUC values are consistently minimal (0.02–0.03), suggesting limited effectiveness in identifying true positives under strong class imbalance.

## Figure 5. Epigenetic-only Model Performance
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

Figure 5a. One Sample:
A heatmap illustrates a sample input profile across 18 epigenetic channels over 23 sequence positions. Notably, several channels are inactive (flat at zero), reflecting feature sparsity.

Figure 5b. Loss & Accuracy Over Iterations:
The model shows modest convergence over 50 epochs. Training loss decreases steadily, while test loss exhibits periodic fluctuations—suggesting some instability. Accuracy peaks at ~0.75 (train) and ~0.65 (test), showing limited generalization.

Figure 5c. ROC Curve:
The ROC-AUC of 0.83 indicates reasonable ability to distinguish positive and negative classes, though lower than the combined model. As with previous models, AUC may be inflated by dataset imbalance.

Figure 5d. Precision-Recall (PR) Curve:
PR-AUC is extremely low (0.02), reflecting poor precision regardless of recall. This highlights that while the model separates classes moderately well (ROC), it rarely makes confident, correct positive predictions.

Figure 5e. FNR and FPR Over Iterations:
The model keeps FNR slightly below 0.1, fulfilling the constraint. However, FPR remains high throughout (fluctuating near 0.4–0.6), signaling high false alarm rates.

Figure 5f. Confusion Matrix:
From Fold 1, out of 33,495 total negatives, 12,041 are false positives (FPR ~0.57), while 89 out of 107 positives are correctly predicted (FNR ~0.17, which is higher than the target—possibly an off-epoch snapshot). Precision is low due to heavy false positive burden.

## Table 7. Sequence-only model five-fold cross-validation metrics
| Fold | FNR Constraint |  FPR    | ROC-AUC | PR-AUC |
|------|---------------|---------|---------|--------|
| 1    | FNR < 0.1     | 0.0390  | 0.99    | 0.31   |
| 2    | FNR < 0.1     | 0.0316  | 0.99    | 0.40   |
| 3    | FNR < 0.1     | 0.0393  | 0.99    | 0.40   |
| 4    | FNR < 0.1     | 0.0340  | 0.99    | 0.36   |
| 5    | FNR < 0.1     | 0.0348  | 0.99    | 0.40   |

Across all five folds, FNR remains under 0.1. FPR is consistently low (0.0316–0.0393), ROC-AUC remains fixed at 0.99, and PR-AUC values range from 0.31 to 0.40. These are the best overall PR-AUC values among all tested models.

## Figure 6. Sequence-only Model Performance
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

Figure 6a. One Sample:
The input heatmap reveals binary patterning from nucleotide encoding channels (e.g., sgRNA and off-site base identities), spanning 23 positions. No epigenetic signal is present, focusing purely on sequence features.

Figure 6b. Loss & Accuracy Over Iterations:
Both training and test loss decline steadily across 200 epochs, indicating stable convergence. Accuracy improves in parallel, peaking around ~0.96 (train) and ~0.93 (test), suggesting good generalization and low overfitting.

Figure 6c. ROC Curve:
The ROC-AUC is exceptionally high (0.99), indicating near-perfect class discrimination. As with other models, this metric is affected by data imbalance, though its magnitude still reflects strong separation capability.

Figure 6d. Precision-Recall (PR) Curve:
The PR-AUC reaches 0.31 for Fold 1—significantly better than the MIT, CFD, and epigenetic-only models. While precision still drops at high recall, it maintains acceptable levels across a broad range.

Figure 6e. FNR and FPR Over Iterations:
Both FNR and FPR decrease steadily during training. FNR remains below the 0.1 constraint, and FPR stabilizes under 0.05 by the end of training, reflecting balanced performance.

Figure 6f. Confusion Matrix:
Out of 32,336 true negatives, only 1,159 are misclassified (FPR ~0.035). Of 107 positives, 80 are correctly predicted and 27 are missed (FNR ~0.25, likely due to epoch mismatch). Overall, the model demonstrates low error rates in both classes.

# Comparison Across Models
## Figure 7. Comparison Across Models
![Model comparison](docs/Comparision_between_models.png)

The box plots confirm that the Seq-Only model dominates overall performance, achieving low FPR, high ROC-AUC, and the best PR-AUC. CCMU also shows promise with low FPR and high ROC-AUC but lower PR-AUC. In contrast, MIT suffers from extreme false positives, while Epi Only fails in precision. CFD occupies the middle ground with moderate scores across all metrics.

# Attention Mechanism
## Figure 8. Positive
![Positive layer1](docs/Positive_attention/layer_1.png)
![Positive layer2](docs/Positive_attention/layer_2.png)
![Positive layer3](docs/Positive_attention/layer_3.png)

Figure 8 shows the attention patterns across all heads and layers for a positively predicted sample. While most heads across all layers exhibit global attention—highlighted by vertical stripes indicating distributed focus over all key positions—certain heads display distinct local behaviors. Specifically, Heads 1 and 2 in both Layer 1 and Layer 2 show diagonal or cross-line patterns characteristic of local attention, suggesting sensitivity to position-specific context such as short motifs. Additionally, Head 3 in Layer 3 also exhibits a similar local pattern amidst otherwise global behavior. This suggests the model uses a combination of localized and global attention mechanisms, where early layers extract local sequence features and deeper layers integrate global context. Such a structured distribution of attention may underlie the model’s ability to accurately classify positive examples.

## Figure 9. Negative
![Negative layer1](docs/Negative_attention/layer_1.png)
![Negative layer2](docs/Negative_attention/layer_2.png)
![Negative layer3](docs/Negative_attention/layer_3.png)

Figure 9 illustrates the attention head outputs across three layers for a negatively predicted sequence. Most attention maps exhibit classic global patterns—vertical stripes indicating widespread attention to all key positions. Notably, only Head 2 in Layer 1, Layer 2, and Layer 3 shows local attention behavior, characterized by cross-diagonal bands, suggesting these heads focus on localized sequence relationships. The persistence of local focus in Head 2 across all layers may indicate a dedicated path for local pattern extraction. However, the lack of diverse local heads, compared to positive cases, suggests that negative predictions rely more heavily on uniform global aggregation rather than positional specificity. This may reflect the model’s strategy of deemphasizing precise motif matching when rejecting potential positives.

# Acknowledgments
I gratefully thank my parents for supporting this project and providing the funds to rent cloud servers for model training.

# Project Status
Due to the current low level of interest in this repository, updates will be infrequent. If the project reaches 20 stars, development will resume with improvements such as an evolved tensor generator, additional protocols, and better architectures.
