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
import pandas as pd
# ——— Define model architecture ———
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
#execute
def execute():
        # ——— Constants ———
    continuous_channels = list(range(10))
    batch_size = 64
        # ——— Load Data ———
    path = '../temp/'
    X = torch.load(os.path.join(path, 'tensor.pt')).float()
    # Normalization
    def apply_z_score_normalization(X, channels, means, stds):
        X_norm = X.clone()
        for i, ch in enumerate(channels):
            X_norm[:, ch, :] = (X[:, ch, :] - means[i]) / stds[i]
        return X_norm

    means = torch.tensor([
        5.9085e-01, 7.9270e-01, 3.4642e-01, 8.6793e+00, 3.5640e-02,
        3.5389e-02, 6.8667e-03, 2.5599e-02, 2.6569e+00, 4.3789e+00
    ])

    stds = torch.tensor([
        8.0447e-01, 6.6048e-01, 6.5337e-01, 1.7684e+01, 2.4862e-01,
        7.0592e-02, 1.0449e-02, 1.5282e+00, 4.8302e+00, 8.0125e+00
    ])
    X = apply_z_score_normalization(X, continuous_channels, means, stds)

    # ——— Load the 5 models ———
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    models = []
    for fold in range(1, 6):
        m = TransformerClassifier().to(device)
        ckpt = torch.load(f'../weights/best_model_{fold}th.pth', map_location=device)
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
    pd.DataFrame(y_pred).to_csv('../temp/results.csv', index=False)
