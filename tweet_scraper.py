import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import os, sys, json, pickle, random
from datetime import date
import time
import thinned_tweet_obj as tt

def load_dict(auth_d, l):
    '''
    Load the contents of a line into a dictionary, using the first word of the
    line as the key and the rest of the line as the value.
    :param auth_d: The dictionary to be populated
    :param l: The line that contains the key and the value, both as strings
    :return: None
    '''
    s = l.find(' ')
    k = l[ :s]
    v = l[s+1:]
    auth_d[k] = v

def read_config_file(file_name):
    '''
    Read a set of configuration parameters from a text file, and return a dictionary with those parameters.

    This assumes that the configuration file has each configuration parameter on a line, with the name of the parameter
    as the first word of the line, followed by a single space, followed by the value of the parameter. All names and
    parameters are assumed to be strings.

    The function will read each line, and place the name/parameter pair into a dictionary keyed by the name with value
    the parameter. Conversion of the parameters to something other than string should be done when the parameter is used.

    :param file_name: Name of the file containing the configuration
    :return: a dictionary with key the name of the configuration parameter and value the configuration value
    '''
    fin = open(file_name, 'r')
    config_dict = json.load(fin)
    fin.close()
    return config_dict

def make_auth(config_d):
    '''
    Create a tweepy auth object. This will use the contents of the dictionary that has been handed in that contains the
    access token and consumer keys. The assumption is that the dictionary contains the authorization tokens needed
    :param auth_dict: dictionary containing the authentication information
    :return: A tweepy auth object
    '''
    if os.path.exists(config_d['credentials']):
        fin = open(config_d['credentials'])
        auth_dict = json.load(fin)
        fin.close()
    else:
        print ('Unable to find credentials file')
        sys.exit(1)
    auth = OAuthHandler(auth_dict['consumer_key'], auth_dict['consumer_secret'])
    auth.set_access_token(auth_dict['access_token'], auth_dict['access_secret'])
    return auth


class MyListener(StreamListener):

    def __init__(self, out_directory, out_fname):
        super().__init__()
        self.count = 1
        self.directory = out_directory
        self.fname = out_fname
        self.date = date.today()
        self.out_buffer = []
        self.outname = os.path.sep.join([out_directory, out_fname])
        self.outname = self.outname + str(self.date) + '.pkl'

    def on_data(self, t_data):
        try:
            #self.outfile.write(t_data)
            jt = json.loads(t_data)
            self.out_buffer.append(tt.tweet(jt))
            if self.count < 1000:
                self.count += 1
            else:
                self.count = 1
                self.write_file()
                if self.check_new_date():
                    self.use_file()
                time.sleep(60 * random.randint(1,120))
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        print(status)
        return True

    def write_file(self):
        if os.path.exists(self.outname):
            fin = open(self.outname, 'rb')
            cur_l = pickle.load(fin)
            fin.close()
        else:
            cur_l = []
        cur_l.extend(self.out_buffer)
        fout = open(self.outname, 'wb')
        pickle.dump(cur_l, fout)
        fout.close()
        self.out_buffer = []
        return None

    def use_file(self):
        if self.date != date.today():
            self.date = date.today()
        self.outname = os.path.sep.join([self.directory, self.fname])
        self.outname = self.outname + str(self.date) + '.pkl'

    def check_new_date(self):
        if self.date != date.today():
            return True
        else:
            return False

def get_filter_list(config_d):
    '''
    Creates a string of comma-separated entries from a file. If there is no hashtag_file entry in
    the configuration file, returns the empty string.
    :param config_d: A
    :return:
    '''
    if os.path.exists(config_d['filter_by']):
        fin = open(config_d['filter_by'])
        ret_data = ','.join(json.load(fin)[:400])
        fin.close()
    else:
        print('Unable to find filter data file')
        sys.exit(1)
    return ret_data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python tweet_scraper.py config_file_name')
        sys.exit(1)

    fname = sys.argv[1]
    config = read_config_file(fname)

    auth = make_auth(config)
    api = tweepy.API(auth)

    data = get_filter_list(config)

    if 'output_directory' in config:
        out_dir = config['output_directory']
    else:
        out_dir = '..'
    if 'output_file' in config:
        out_file = config['output_file']
    else:
        out_file = 'test_output'

    if data == '':
        print('No terms specified for tracking, program exiting')
        sys.exit(1)

    while True:
        try:
            ml = MyListener(out_dir, out_file)
            twitter_stream = Stream(auth, ml)
            twitter_stream.filter(track=[data])
        except KeyboardInterrupt:
            ml.write_file()
            sys.exit(0)

        except:
            pass
