import argparse
import pandas as pd
from utils import convert_all_csvs_to_tsv, process_crispr_csv, extract_and_save_tensor
from inferring import execute

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_path', type=str, required=True, help='Path to the input CSV file')
    args = parser.parse_args()

    convert_all_csvs_to_tsv("../examples")

    df_processed = process_crispr_csv(args.csv_path)
    print(df_processed.head())

    df_processed.to_csv('../temp/temp.csv', index=False)
    extract_and_save_tensor('../temp/temp.csv','../epidata/','../temp/tensor.pt')
    execute()
    input = pd.read_csv(args.csv_path, sep="\t")
    result = pd.read_csv('../temp/results.csv',sep=',')
    combined_df = pd.concat([input, result], axis=1)
    # Save to a new CSV
    combined_df.to_csv('../output/combined_output.csv', index=False)

if __name__ == '__main__':
    main()
