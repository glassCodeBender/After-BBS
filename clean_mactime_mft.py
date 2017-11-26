import pandas as pd
import re
import sys

"""
Program to filter an MFT Body file in a variety of ways.
Creates:
File that includes cleaned up file that includes important extensions.
File with prefetch and lnk files.
Instances with the compiler
A timeline with only true file names. 

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
          r'|\.rs$|\.lnk|\.bat|compiler|tmp|\.c$|\.vb|\.cc|\.cp|\.scala|\.pl|.asm|\.sh|\.bash|\.com'
regex1 = re.compile(pattern, flags=re.IGNORECASE)
df['mask'] = df[['File Name']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
df = df[df['mask'] == True]

pattern2 = r'm|b'
regex2 = re.compile(pattern2, flags=re.IGNORECASE)

df['mask2'] = df[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
df = df[df['mask2'] == True]
df.drop(['mask', 'mask2'], axis=1, inplace=True)

normal_filter_filename = 'general_' + import_file

df.to_csv(export_file, index=True)

# Create new df w/ only lnk and prefetch files.

lnkdf = pd.DataFrame()

lnkdf = lnkdf.from_csv(import_file, sep=',', index_col='Date')

pattern = r'\.lnk|\.pf|prefetch'
regex1 = re.compile(pattern, flags=re.IGNORECASE)
lnkdf['mask'] = lnkdf[['File Name']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
lnkdf = lnkdf[lnkdf['mask'] == True]
pattern2 = r'm|b'
regex2 = re.compile(pattern2, flags=re.IGNORECASE)

lnkdf['mask2'] = lnkdf[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
lnkdf = lnkdf[lnkdf['mask2'] == True]
lnkdf.drop(['mask', 'mask2'], axis=1, inplace=True)

lnk_filename = "lnk_" + export_file

lnkdf.to_csv(lnk_filename, index=True)

# Look for occurences of the word compiler and cmd.exe

compiler_df = pd.DataFrame()

compiler_df = compiler_df.from_csv(import_file, sep=',', index_col='Date')

pattern = r'compiler|cmd\.exe'
regex1 = re.compile(pattern, flags=re.IGNORECASE)
compiler_df['mask'] = compiler_df[['File Name']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
compiler_df = compiler_df[compiler_df['mask'] == True]
pattern2 = r'm|b'
regex2 = re.compile(pattern2, flags=re.IGNORECASE)

compiler_df['mask2'] = compiler_df[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
compiler_df = compiler_df[compiler_df['mask2'] == True]
compiler_df.drop(['mask', 'mask2'], axis=1, inplace=True)

compiler_filename = 'compiler' + export_file

compiler_df.to_csv(compiler_filename, index=True)

# Filter to only include System32 so we can verify timestomping.

time_df = pd.DataFrame()

time_df = time_df.from_csv(import_file, sep=',', index_col='Date')

pattern = r'system32'
regex1 = re.compile(pattern, flags=re.IGNORECASE)
time_df['mask'] = time_df[['File Name']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
time_df = time_df[time_df['mask'] == True]
pattern2 = r'm|b'
regex2 = re.compile(pattern2, flags=re.IGNORECASE)

time_df['mask2'] = time_df[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
time_df = time_df[time_df['mask2'] == True]
time_df.drop(['mask', 'mask2'], axis=1, inplace=True)

timestomp_filename = 'timestomp_' + export_file

time_df.to_csv(timestomp_filename, index=True)

# Filter in way that gives us a true timeline of events

true_df = pd.DataFrame()

true_df = true_df.from_csv(import_file, sep=',', index_col='Date')

pattern = r'\.exe|\.rar|\.bi|\.ps|\.sys|\.jar|\.bcp|\.ctl|\.ctt|\.b|\.pf|\.rb|\.s$|\.swift|\.vbs +' \
          r'|\.rs$|\.lnk|\.bat|compiler|tmp|\.c$|\.vb|\.cc|\.cp|\.scala|\.pl|.asm|\.sh|\.bash|\.com'

regex1 = re.compile(pattern, flags=re.IGNORECASE)
true_df['mask'] = true_df[['File Name']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
true_df = true_df[true_df['mask'] == True]

pattern2 = r'm|b'
regex2 = re.compile(pattern2, flags=re.IGNORECASE)

true_df['mask2'] = true_df[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
true_df = true_df[true_df['mask2'] == True]

pattern3 = r'FILE_NAME'
regex3 = re.compile(pattern3)

true_df['mask3'] = true_df[['File Name']].apply(lambda x: x.str.contains(regex3, regex=True)).any(axis=1)
true_df = true_df[true_df['mask2'] == True]

true_df.drop(['mask', 'mask2', 'mask3'], axis=1, inplace=True)

true_timeline = 'timeline_' + export_file

true_df.to_csv(export_file, index=True)

# Need to include program that uses the regex created by BBS Volatile IDS
