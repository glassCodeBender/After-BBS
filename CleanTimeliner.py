import pandas as pd
import re
import sys

"""
Program filters timeliner to only include created and updated files. 
"""

import_file = sys.argv[1]
export_file = sys.argv[2]

if sys.argv != 2:
    print("You need to supply two arguments for this program to work. The import filename and export filename.")
    sys.exit(1)

df = pd.DataFrame()

df = df.from_csv(import_file, sep=',', index_col='Date')

df['mask2'] = df[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
df = df[df['mask2'] == True]
df.drop(['mask', 'mask2'], axis=1, inplace=True)

df.to_csv(export_file, index=True)
