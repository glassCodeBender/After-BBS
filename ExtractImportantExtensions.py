import pandas as pd
import re
import sys

"""
Program to filter significant file extensions
USAGE: ~$ python ExtractImportantExtensions.py file_to_read.csv file_to_write.csv
"""

import_file = sys.argv[1]
export_file = sys.argv[2]

df = pd.DataFrame()

df = df.from_csv(import_file, sep=',', index_col='Date')

pattern = r'\.exe|\.rar|\.sys|\.jar|\.pf|\.lnk|\.bat'
regex1 = re.compile(pattern, flags=re.IGNORECASE)
df['mask'] = df[['File Name']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
df = df[df['mask'] == True]
pattern2 = r'm|b'
regex2 = re.compile(pattern2, flags=re.IGNORECASE)

df['mask2'] = df[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
df = df[df['mask2'] == True]
df.drop(['mask', 'mask2'], axis=1, inplace=True)

new_filename = 'by_ext_' + 'test.csv'
df.to_csv(export_file, index=True)
