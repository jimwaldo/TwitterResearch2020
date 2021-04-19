#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 13:50:33 2020

@author: jimwaldo

General routines that only need to be written once.
"""
import json
import pickle
import subprocess
import string

"""
Basic reading and writing of pickled objects or json objects to/from a file. These functions will not
check to see if the file exists (for reading) and will overwrite (when writing). 
"""
def read_pkl(fname):
    """
    Read a pickled object from a file with path name fname. Returns the object after closing the file.
    :param fname: Path name of the file containing the pickle
    :return: The object contained in the pickle file
    """
    fout = open(fname, 'rb')
    ret_o = pickle.load(fout)
    fout.close()
    return ret_o

def write_pkl(fname, to_write):
    """
    Write and object in pickle form to the file named by the path fname. Will open and close the
    output file.
    :param fname: The path of the file in which to write the pickle. Note that existing files will be
    over-written. Assumes the user has access to the file
    :param to_write: the python object to be written to the pickle file
    :return None
    """
    fout = open(fname, 'wb')
    pickle.dump(to_write, fout)
    fout.close()
    return None

def read_json(fname):
    """
    Read an object from a json file. Assumes that the input file is the result of a json.dump serialization
    of a json object.
    :param fname: Path of the file to be read
    :return the deserialized object
    """
    fin = open(fname, 'r')
    ret_j = json.load(fin)
    fin.close()
    return ret_j

def write_json(fname, to_write):
    """
    Write an object to a file in json format.
    :param fname: path of the file to write. If the file already exists, it will be overwritten
    :param to_write: the object to be written
    :return None
    """
    fout = open(fname, 'w')
    json.dump(to_write, fout)
    fout.close()
    return None


def file_decompress(start_name):
    """
    Uncompress a file if needed. Will handle both compressed and gzipped files. If the file is neither compressed (determined
    by having a .Z extension) or gzipped (determined by having a .gz extenstion) return the name of the file and do
    nothing
    :param start_name: name of the file to be uncompressed or unzipped
    :return: The name of the uncompressed file, or the name of the original file if it was neither compressed nor
    gzipped.
    """
    if start_name[-2:] == '.Z':
        print ('Uncompressing ', start_name)
        subprocess.run(['uncompress', start_name])
        return start_name[:-2]
    elif start_name[-3:] == '.gz':
        print ('Unzipping', start_name)
        subprocess.run (['gunzip', start_name])
        return start_name[:-3]
    else:
        return start_name


def file_compress(fname):
    """
    Gzip a file; this is run when the extraction is done to save space.
    :param fname: Name of the file to gzip
    :return: None
    """
    print ('Running gzip on', fname)
    subprocess.run (['gzip', fname])
    return

def count_english(check_s, dic_s):
    """
    Count the number of words in a string that are also in the supplied set of words

    This function takes a string and a set of words, and returns the count of the number of words in the string that
    are also in the word set. The intended use is to have a word set that is taken from a language dictionary. Words
    are all converted to lower case, and trailing punctuation is stripped from a word

    :param check_s A string with words separated by spaces
    :param dic_s: a set of lower-case words that act as the count authority
    :return an integer indicating the number of words in check_s that occur in dic_s
    """
    eng_c = 0
    word_l = check_s.lower().split()
    for w in word_l:
        if w in dic_s:
            eng_c += 1
        else:
            if w[-1] in string.punctuation:
                while len(w) > 0 and w[-1] in string.punctuation:
                    w = w[:-1]
                if w in dic_s:
                    eng_c += 1
    return eng_c