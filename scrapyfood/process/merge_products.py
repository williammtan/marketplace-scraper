import argparse
import pandas as pd

from scrapyfood.utils import read_df

def merge_products(files, output, columns=None):
    if columns is None:
        merged = pd.concat([
            read_df(f)
            for f in files
        ])
    else:
        merged = pd.concat([
            read_df(f)[columns]
            for f in files
        ]).drop_duplicates()

    merged.to_csv(output, index=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', help='Files to merge')
    parser.add_argument('-c', '--columns', nargs='+', help='Columns in which to merge (not required)', required=False, default=None)
    parser.add_argument('-o', '--output', help='File to output')
    args = parser.parse_args()

    merge_products(args.files, args.output, args.columns)
