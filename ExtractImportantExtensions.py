import pandas as pd
import re
import sys

"""
Program to filter significant file extensions
USAGE: ~$ python ExtractImportantExtensions.py file_to_read.csv file_to_write.csv
"""

import_file = sys.argv[1]
export_file = sys.argv[2]

if sys.argv != 2:
    print("You need to supply two arguments for this program to work. The import filename and export filename.")
    sys.exit(1)

df = pd.DataFrame()

df = df.from_csv(import_file, sep=',', index_col='Date')

# other extensions that might be useful.
other_stuff = '\.pdf|\.ain|\.dbg|\.torrent\.ts'

programming_stuff = '\.cbl|\.class|\.cob|\.cs$|\.cxx\.def\.di\.erl\.f$|\.m$|\.p$|\.pli|\.sym'

pattern = r'\.exe|\.rar|\.bi|\.ps|\.sys|\.jar|\.bcp|\.ctl|\.ctt|\.b|\.pf|\.rb|\.s$|\.swift|\.vbs +' \
          r'|\.rs$|\.lnk|\.bat|compiler|tmp|\.c$|\.vb|\.cc|\.cp|\.scala|\.pl|.asm|\.sh|\.bash'
regex1 = re.compile(pattern, flags=re.IGNORECASE)
df['mask'] = df[['File Name']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
df = df[df['mask'] == True]

pattern2 = r'm|b'
regex2 = re.compile(pattern2, flags=re.IGNORECASE)

df['mask2'] = df[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
df = df[df['mask2'] == True]
df.drop(['mask', 'mask2'], axis=1, inplace=True)

df.to_csv(export_file, index=True)
