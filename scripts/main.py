from utils import convert_all_csvs_to_tsv
from utils import process_crispr_csv
convert_all_csvs_to_tsv("../examples")
df_processed = process_crispr_csv("../examples/example2.csv")
print(df_processed.head())
df_processed.to_csv('../temp/temp.csv', index=False)
