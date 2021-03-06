#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 14:47:05 2020

@author: jimwaldo

Merge a set of lists of thinned_tweets into a single file. When run alone, takes the directory in which the data
is stored (and where the combined file will be written) and a pattern of the files that will be merged. The pattern
must be a simple string; we aren't doing anything fancy with regular expressions. The program will do duplicate
elimination (based on the id of the tweet) in the output file.
"""

import os, sys
import general_utilities as ut

def get_flist(from_dir, pattern):
    """
    Given a directory, return all of the files in that directory that contain the string passed as the pattern.
    :param from_dir: A string indicating the directory in which to look for files fitting the pattern
    :param pattern: A string that will be exactly matched to select files in the directory
    :return a list of pathnames including both the directory and the filename of files that match
    """
    all_f = os.listdir(from_dir)
    ret_list = []
    for f in all_f:
        if pattern in f:
            ret_list.append('/'.join([from_dir, f]))
    return ret_list

def build_tweet_list(f_list):
    """
    Combine the contents of the files in file_list into a single list. The files are assumed to
    be pickles of lists of thinned_tweet objects. Duplicates (based on twitter_id) will be
    eliminated.
    :param f_list: a list of files to be combined
    :return a list of the thinned tweets in the files supplied
    """
    tweet_list = []
    tweet_set = set()
    for f_name in f_list:
        t_l = ut.read_pkl(f_name)
        for t in t_l:
            if t.tweet_id not in tweet_set:
                tweet_list.append(t)
                tweet_set.add(t)
                    
    return tweet_list

if __name__ =='__main__':
    if len(sys.argv) < 3:
        print('Usage: python merge_tweet_files.py target_directory file_pattern')
        sys.exit(1)

    f_list = get_flist(sys.argv[1], sys.argv[2])
    out_fname = '-'.join(['combined_tweets', sys.argv[2]])
    out_fname = '.'.join([out_fname, 'pkl'])
    out_name = '/'.join([sys.argv[1], out_fname])
    if os.path.exists(out_name):
        print('Output file already exists...Continue? [y/n]')
        if (input() != 'y'):
            exit()
    comb_tweet_l = build_tweet_list(f_list)
    ut.write_pkl(out_name, comb_tweet_l)