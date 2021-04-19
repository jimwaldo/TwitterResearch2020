#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 08:51:42 2020

@author: jimwaldo
"""

import general_utilities as gt
import os

def build_count_d(t_l):
    ret_d = {}
    for t in t_l:
        tuid = t.get_user_id()
        if tuid is not None:
            count = ret_d.setdefault(tuid, 0)
            ret_d[tuid] = count + 1
    return ret_d

def build_id_name_d(t_l):
    ret_d = {}
    for t in t_l:
        uid = t.get_user_id()
        if uid is not None:
            if uid not in ret_d:
                ret_d[uid] = t.get_user_name()
    return ret_d

def build_count_id_d(count_d):
    ret_d = {}
    for k,v in count_d.items():
        id_s = ret_d.setdefault(v, [])
        id_s.append(k)
        ret_d[v] = id_s
    return ret_d

def build_count_posters(count_id_d):
    c_l = list(count_id_d.keys())
    c_l.sort(reverse = True)
    ret_l = []
    for c in c_l:
        ret_l.append((c,len(count_id_d[c])))
    return ret_l

def find_break(count_l):
    count_l.sort(reverse = True)
    max_diff = 0
    high_end = 0
    low_end = 0
    prev = count_l[0]
    for l in count_l[1:]:
        diff = prev - l
        if diff > max_diff:
            max_diff = diff
            high_end = prev
            low_end = l
        prev = l
    return (max_diff, low_end, high_end)

def build_top_n_d(tweet_l, num, top_n_d, day):
    '''
    Build a dictionary, keyed by user id, of the top num tweeters in tweet_l

    The dictionary has as values the tuple (count, day) where count is the number of tweets for tha user and day is the
    numerical day passed in as an argument. The dictionary is passed in as an argument; the dictionary passed in is
    updated with the values in the tweet_l, which is a list of thinned tweets.

    :param tweet_l: A list of thinned tweets to be processed
    :param num: The number of top tweets to add to the dictionary
    :param top_n_d: A dictionary of user_id, (number of tweets, day) to be updated
    :param day : a parameter indicating the day to record as part of the value of the dictionary
    :return: the dictionary passed in as top_n_d, updated with the top num tweeters in tweet_l
    '''
    count_d = build_count_d(tweet_l)
    count_id_d = build_count_id_d(count_d)
    count_l = list(count_id_d.keys())
    count_l.sort(reverse = True)
    for i in count_l[:num]:
        ids = count_id_d[i]
        for id in ids:
            id_list = top_n_d.setdefault(id, [])
            id_list.append((i, day))
    
    return top_n_d

def distill_counts(t_l, fname_date):
    """


    """
    count_d = build_count_d(t_l)
    id_name_d = build_id_name_d(t_l)
    count_id = build_count_id_d(count_d)
    count_posters = build_count_posters(count_id)
    
    gt.write_pkl('count_d_' + fname_date + base_ext, count_d)
    gt.write_pkl('id_name_d_' + fname_date + base_ext, id_name_d)
    gt.write_pkl('count_id_' + fname_date + base_ext, count_id)
    gt.write_pkl('count_posters_' + fname_date + base_ext, count_posters)

def generate_to_n(n, out_f_name):
    """
    Generate a dictionary, keyed by user twitter id, with values a list of number of tweets and date of that number of tweets
    for the top n tweeters of the day. This is mean to be run over the combined_tweet files for a month

    :param n: generate a dictionary that contains the top n tweeters for each day
    :param out_f_name: name of the file in which a pickle of the dictionary will be written
    """
    all_f = os.listdir('.')
    f_list = []
    for f in all_f:
        if ('combined') in f:
            f_list.append(f)

    top_10_d = {}
    for f in f_list:
        print('Reading file', f)
        tweet_l = gt.read_pkl(f)
        top_10_d = build_top_n_d(tweet_l, n, top_10_d, f[-6:-4])
        
    gt.write_pkl(out_f_name, top_10_d)

def separate_by_user(tweet_l, separation_set):
    """
    Separate a list of tweets by the user id of the tweeters

    Creates two lists of tweets. One is all of the tweets in tweet_l that are from a user_id in the user_id set
    separation_set; the other is all of the other tweets in the list
    :param tweet_l: A list of thinned tweets
    :param separation_set: A set of user_id for those users whose thinned tweets are to be separated
    :return: a pair of lists, the first of which is all tweets from users in separation_set, the other all other tweets
    in tweet_l
    """
    remain_l = []
    sep_l = []
    for t in tweet_l:
        if t.get_user_id() in separation_set:
            sep_l.append(t)
        else:
            remain_l.append(t)

    return sep_l, remain_l