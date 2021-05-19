# Script to find the count of a document
import argparse
import json
import pandas as pd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    args = parser.parse_args()

    with open(args.file) as f:
        txt = f.read()
        # txt = txt.replace('[', '')
        # txt = txt.replace(']', '')
        while True:
            if txt[-1] in [' ', ',', '\n']:
                txt = txt[:-2]
            else:
                break
        txt = txt + ']'
        df = pd.DataFrame(json.loads(txt))
        df = df.drop_duplicates(subset='id').reset_index()
        print(df)
