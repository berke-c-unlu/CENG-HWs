import csv
import sys
import pandas as pd

if __name__ == "__main__":
    file_path = sys.argv[1]
    output_path = sys.argv[2]

    # open csv file 
    df = pd.read_csv(file_path)
    # replace null values with 'null'
    df.fillna('null', inplace=True)
    # save as tsv file
    df.to_csv(output_path, sep='\t', index=False)
    
