import os
import torch
import torch.nn as nn
import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    roc_curve, auc,
    precision_recall_curve, average_precision_score
)
import matplotlib.pyplot as plt
import seaborn as sns

# ——— Constants ———
continuous_channels = list(range(10))
batch_size = 64

# ——— Define your exact same model architecture ———
class TransformerClassifier(nn.Module):
    def __init__(self, input_dim=18, seq_length=23, hidden_dim=256, num_layers=3, nhead=8, dropout=0.1):
        super(TransformerClassifier, self).__init__()
        self.embedding = nn.Linear(input_dim, hidden_dim)
        self.positional_encoding = nn.Parameter(torch.zeros(1, seq_length, hidden_dim))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim, nhead=nhead,
            dim_feedforward=hidden_dim*2, dropout=dropout, activation='relu'
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.layernorm = nn.LayerNorm(hidden_dim)
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = x.transpose(1, 2)
        x = self.embedding(x) + self.positional_encoding
        x = self.layernorm(x)
        x = x.transpose(0, 1)
        x = self.transformer_encoder(x)
        x = x.transpose(0, 1).mean(dim=1)
        return self.sigmoid(self.fc(x)).squeeze()

# ——— Load Data ———
path = '.'
pos = torch.load(os.path.join(path, 'train_test_data/Positive.pt')).float()
neg = torch.load(os.path.join(path, 'train_test_data/Negative.pt')).float()
X = torch.cat([pos, neg], dim=0)
y = torch.cat([torch.ones(len(pos)), torch.zeros(len(neg))], dim=0).numpy()

# Normalization
def compute_channel_mean_std(X, channels):
    means = X[:, channels, :].mean(dim=(0, 2))
    stds = X[:, channels, :].std(dim=(0, 2)) + 1e-8
    return means, stds

def apply_z_score_normalization(X, channels, means, stds):
    X_norm = X.clone()
    for i, ch in enumerate(channels):
        X_norm[:, ch, :] = (X[:, ch, :] - means[i]) / stds[i]
    return X_norm

means, stds = compute_channel_mean_std(X, continuous_channels)
print(means,stds)
X = apply_z_score_normalization(X, continuous_channels, means, stds)

# ——— Load the 5 models ———
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
models = []
for fold in range(1, 6):
    m = TransformerClassifier().to(device)
    ckpt = torch.load(f'weights/best_model_{fold}th.pth', map_location=device)
    m.load_state_dict(ckpt['model_state_dict'])
    m.eval()
    models.append(m)

# ——— Inference: collect each model’s scores in batches ———
with torch.no_grad():
    all_scores = []
    for m in models:
        preds = []
        for i in range(0, X.shape[0], batch_size):
            batch = X[i:i+batch_size].to(device)
            pred = m(batch).cpu().numpy()
            preds.append(pred)
        preds = np.concatenate(preds, axis=0)
        all_scores.append(preds)
    all_scores = np.stack(all_scores, axis=0)

# ——— Ensemble by averaging ———
ensemble_scores = all_scores.mean(axis=0)
y_pred = (ensemble_scores >= 0.5).astype(int)

# ——— 1. Confusion Matrix ———
cm = confusion_matrix(y, y_pred)
cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

# Plot
plt.figure(figsize=(5, 4))
sns.heatmap(cm_normalized, annot=cm, fmt='d', cmap='Blues')
plt.title("Row-Normalized Confusion Matrix (Heat Separated)")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

# ——— 2. ROC Curve & AUC ———
fpr, tpr, _ = roc_curve(y, ensemble_scores)
roc_auc = auc(fpr, tpr)
plt.figure(figsize=(6,4))
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
plt.plot([0,1], [0,1], '--', alpha=0.5)
plt.title("Ensemble ROC Curve")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend(loc="lower right")
plt.show()

# ——— 3. Precision–Recall Curve & AP ———
precision, recall, _ = precision_recall_curve(y, ensemble_scores)
ap = average_precision_score(y, ensemble_scores)
plt.figure(figsize=(6,4))
plt.plot(recall, precision, label=f"AP = {ap:.3f}")
plt.title("Ensemble Precision–Recall Curve")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.legend(loc="upper right")
plt.show()