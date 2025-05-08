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

if __name__ == '__main__':
    main()
