import pandas as pd
import os

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
convert_all_csvs_to_tsv("examples")

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
df_processed = process_crispr_csv("examples/example2.csv")
print(df_processed.head())

