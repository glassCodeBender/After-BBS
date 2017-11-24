"""
@Author: glassCodeBender
@Date: 11/23/2007
@Version: 1.0

Program Purpose: This program helps forensic practitioners filter a Master File Table dumped into a csv file by mactime 
to only include the most useful file extensions, directories, or occurrences of certain viruses. 

The program (hopefully) creates multiple csvs based on different filters. Eventually I'll add filters for lnk 
and prefetch files. I'll also write a filter to search for compilers.

I don't plan on making the program easy for others to use (argparse already wasted too much of my time)

NOTE: This program was written with python 3.6. If you are using this after volatility was run, you'll need to 
switch environments.

Example Usage: 
~$ python clean_mactime_mft.py filename_to_read.csv output_filename.csv

"""

import pandas as pd
import re
import sys
import os

if len(sys.argv) != 2:
    print("You must include a filename to read and filename to output to for this program to work. ")
    print("Usage: ~$ python clean_mactime_mft.py filename_to_read.csv output_filename.csv")
    sys.exit(1)

# This should be added as a command line argument
mft_csv = sys.argv[1]
# Do we want to look for executables run outside of a standard directory.
suspicious = True
# Use the following to filter the mft by a time
sdate = ''
edate = ''
stime = ''
etime = ''
# this should be included w/ argv
output_file = sys.argv[2]
# a boolean to determine if a numbered index should be added.
index_bool = True
# not sure what this is yet
filter_index = ''
reg_file = ''


# This is the main method of the program.
def run():

    # not going to worry about this section for now.
    if filter_index:
        sindex, eindex = [x.strip() for x in filter_index.split(',')]

        if sindex.contains(',') or eindex.contains(','):
            sindex.replace(',', '')
            eindex.replace(',', '')

    if not sindex.isdigit and eindex.isdigit:
        raise ValueError("ERROR: The index value you entered to filter the table by was improperly formatted. \n"
                         "Please try to run the program again with different values.")
    df = pd.DataFrame()

    df = df.from_csv(mft_csv, sep=',', index_col='Date', parse_dates=True)

    # df = df.from_csv("MftDump_2015-10-29_01-27-48.csv", sep='|')
    # df_attack_date = df[df.index == '2013-12-03'] # Creates an extra df for the sake of reference

    filter_by_extension(df)
    # if reg_file:
    #   df = filter_by_extension(df)
 
    if sdate or edate or stime or etime:
        filter_by_dates(df)
    if suspicious:
        filter_suspicious(df)
    if index_bool:
        df.reset_index(level=0, inplace=True)

        # times need to be converted to do this.
        if sindex and eindex:
            df = df[sindex:eindex]

    df.to_csv(output_file, index=True)


""" 
Read a file line by line and return a list with items in each line.
@Param A Filename
@Return A list 
"""


def read_file(file):
    list = []
    with open(file) as f:
        for line in f:
            list.append(line)
    return list


""" 
Method to filter a list of words and concatenate them into a regex
@Param List of words provided by user to alternative file.
@Return String that will be concatenated to a regex. 
"""


def update_reg(list):
    s = '|'
    new_reg = s.join(list)
    return new_reg


""" 
Filters a MFT csv file that was converted into a DataFrame to only include relevant extensions.
@Param: DataFrame 
@Return: DataFrame - Filtered to only include relevant file extensions. 
"""


def filter_by_extension(df):
    user_reg = ''

    if reg_file:
        reg_list = read_file(reg_file)
        user_reg = update_reg(reg_list)

    if user_reg:
        pattern = r'' + user_reg
    else:
        pattern = r'.exe|.rar|.sys|.jar|.pref|.lnk'

    regex1 = re.compile(pattern, flags=re.IGNORECASE)
    df['mask'] = df[['Filename', 'Desc']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
    filt_df = df[df['mask'] == True]

# M – Modified Time A – Accessed Time C – Metadata (MFT) Changed Time B – Born Time (created)

    # regex to filter by time file was created or accesse
    pattern2 = r'm|b'
    regex2 = re.compile(pattern2, flags=re.IGNORECASE)

    filt_df['mask2'] = filt_df[['Type']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
    filtered_df = filt_df[filt_df['mask2'] == True]
    filtered_df.drop(['mask', 'mask2'], axis=1, inplace=True)

    new_filename = 'by_ext_' + mft_csv
    filtered_df.to_csv(new_filename, index=True)


""" 
Filters a MFT so that only the executables that were run outside Program Files are 
included in the table. 
@Param: DataFrame 
@Return: DataFrame - Filtered to only include relevant file extensions. 
"""
def filter_suspicious(df):

    pattern = r'^.+(Program\sFiles|System32).+[.exe]$'
    regex1 = re.compile(pattern)
    df['mask'] = df[['Filename', 'Desc']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
    filt_df = df[df['mask'] == False]

    pattern2 = r'.exe$'
    regex2 = re.compile(pattern2)
    filt_df['mask2'] = filt_df[['Filename', 'Desc']].apply(lambda x: x.str.contains(regex2, regex=True)).any(axis=1)
    filtered_df = filt_df[filt_df['mask2'] == True]
    filtered_df.drop(['mask', 'mask2'], axis=1, inplace=True)

    filtered_df.to_csv('suspicious_' + mft_csv, index=True)



def look_for_timestomp(df):

    pattern = r'^.+(System32).+[.exe]$'
    regex1 = re.compile(pattern, flags=re.IGNORECASE)
    df['mask'] = df[['Filename', 'Desc']].apply(lambda x: x.str.contains(regex1, regex=True)).any(axis=1)
    filt_df = df[df['mask'] == True]
    filt_df.drop(['mask'], axis=1, inplace=True)
    filt_df.to_csv('timestomp_check_' + mft_csv, index=True)


""" 
Filters a MFT csv file that was converted into a Dataframe to only include the 
occurrences of certain dates and/or times.
@Param: DataFrame 
@Return: DataFrame - Filtered to only include relevant virus names. 
"""
def filter_by_dates(df):


    if edate and sdate and etime and stime:
        s_stamp = pd.Timestamp(sdate + ' ' + stime)
        e_stamp = pd.Timestamp(edate + ' ' + etime)
        filtered_df = df[s_stamp:e_stamp]
    elif sdate and edate and etime and not stime:
        s_stamp = pd.Timestamp(sdate)
        e_stamp = pd.Timestamp(edate + ' ' + etime)
        filtered_df = df[s_stamp:e_stamp]
    elif sdate and edate and stime:
        s_stamp = pd.Timestamp(sdate + ' ' + stime)
        e_stamp = pd.Timestamp(edate)
        filtered_df = df[s_stamp:e_stamp]
    elif sdate and stime:
        s_stamp = pd.Timestamp(sdate + ' ' + stime)
        filtered_df = df[s_stamp:]
    elif edate and etime:
        e_stamp = pd.Timestamp(edate + ' ' + etime)
        filtered_df = df[:e_stamp]
    elif sdate:
        s_stamp = pd.Timestamp(sdate)
        filtered_df = df[s_stamp:]
    elif edate:
        e_stamp = pd.Timestamp(edate)
        filtered_df = df[:e_stamp]
    else:
        raise ValueError("You entered an invalid date to filter the table by or you did not include a date\n"
                         "to filter by. Please try again."
                         "\n\tExample Usage: $ python cleanMFT.py -f MFT.csv -r regex.csv -s 2015-06-08 -e 2015-06-30 -t 06:30:00 -u 06:31:20")
    return filtered_df

