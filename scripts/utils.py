import pandas as pd
import os
import sys
import numpy as np
import torch
import pyBigWig
#convert comma csv into \t csv
def convert_all_csvs_to_tsv(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder_path, filename)
            try:
                df = pd.read_csv(filepath, sep=',')
                if len(df.columns) == 1:
                    print(f"[SKIP] '{filename}' is likely already tab-separated.")
                    continue
                df.to_csv(filepath, sep='\t', index=False)
                print(f"[CONVERTED] '{filename}' converted to tab-separated.")
            except Exception as e:
                print(f"[ERROR] Failed to process '{filename}': {e}")
#generate genome coordinate
def process_crispr_csv(filepath):
    # Step 1: Read the CSV
    df = pd.read_csv(filepath, sep="\t")

    # Step 2: Combine Sequence and PAM
    df["Full_sequence"] = df["Sequence"].str[:-3] + df["PAM"]

    # Step 3: Get the first On-target = TRUE sequence
    on_target_seq = df[df["On-target"] == True]["Full_sequence"].values[0]

    # Step 4: Add new On_target column
    df["On_target"] = on_target_seq

    # Step 5: Compute start and end
    def compute_start_end(row):
        if row["Strand"] == -1:
            start = row["Position"] - 6
        else:
            start = row["Position"] - 17
        end = start + 22
        return pd.Series([start, end])

    df[["start", "end"]] = df.apply(compute_start_end, axis=1)

    return df
#extract data from bigWigs
def extract_and_save_tensor(csv_path, bigwig_dir, output_path):
    bw_files = {
        'ATAC':    'ATAC.bigWig',
        'CTCF':    'CTCF.bigWig',
        'H3K9me3': 'H3K9me3.bigWig',
        'H3K4me1': 'H3K4me1.bigWig',
        'H3K27ac': 'H3k27ac.bigWig',
        'H3K4me3': 'H3k4me3.bigWig',
        'DNase':   'DNase.bigWig',
        'RRBS':    'RRBS.bigWig',
        'H3K27me3': 'H3K27me3.bigWig',
        'H3K36me3': 'H3K36me3.bigWig'
    }

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path, index_col=0)
    N = len(df)
    L = int(df.iloc[0]['end'] - df.iloc[0]['start'] + 1)

    epi = np.zeros((N, len(bw_files), L), dtype=np.float32)
    for i, (_, row) in enumerate(df.iterrows()):
        chrom, start, end, strand = row['Chromosome'], int(row['start']), int(row['end']), row['Strand']
        if (end - start + 1) != L:
            raise ValueError(f"Region length mismatch at row {i+2}, expected {L}.")

        for j, filename in enumerate(bw_files.values()):
            path = os.path.join(bigwig_dir, filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing bigWig file: {path}")

            with pyBigWig.open(path) as bw:
                vals = np.array(bw.values(chrom, start, end + 1), dtype=np.float32)
            vals = np.nan_to_num(vals, nan=0.0)
            if strand == '-':
                vals = vals[::-1]
            epi[i, j, :] = vals

    def one_hot(seqs, length):
        base2idx = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
        M = len(seqs)
        oh = torch.zeros((M, 4, length), dtype=torch.float32)
        for i, s in enumerate(seqs):
            s = s.upper()
            if len(s) != length:
                raise ValueError(f"Seq {i} length {len(s)} ≠ {length}")
            for k, nt in enumerate(s):
                idx = base2idx.get(nt)
                if idx is not None:
                    oh[i, idx, k] = 1.0
        return oh

    sg_oh = one_hot(df['Full_sequence'].tolist(), L)
    off_oh = one_hot(df['On_target'].tolist(), L)

    epi_t = torch.from_numpy(epi)
    stacked = torch.cat([epi_t, sg_oh, off_oh], dim=1)
    torch.save(stacked, output_path)
    print(f"Saved {output_path} with shape {tuple(stacked.shape)}")
