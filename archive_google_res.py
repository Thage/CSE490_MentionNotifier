import google_search_iter as google
#from google import google
import hashlib
import requests
import pickle
import os
from plyer import notification
from tabbedLayout import google_threads

site_dict = {}

def iterThis(res):
    link = res.link
    print(link)
    try:
        page = requests.get(link,headers=None,proxies=None,timeout=3)
        site_dict[link] = hashlib.sha3_512(page.text.encode('utf-8')).hexdigest()
    except (requests.exceptions.ReadTimeout, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
        site_dict[link] = "0"*128


def pickle_dict(search_keywords):
    update_count = 0
    update_index = [False] * len(site_dict)
    pickle_filename = search_keywords + '.pickle'
    os.chdir('pickles')
    if os.path.isfile(pickle_filename):
        #print("yay")
        with open(pickle_filename, 'rb') as handle:
            old_dict = pickle.load(handle)
            #print(old_dict.keys())
        print(site_dict.keys() - old_dict.keys())
        print("SITE_DICT_KEYS")
        print(site_dict.keys())
        print("OLD_DICT_KEYS")
        print(old_dict.keys())
        if (site_dict.keys() - old_dict.keys()) == set():
            #print("**")
            update_count, update_index = compare_dicts(site_dict, old_dict)
            print(update_index)
            #print(">>" + str(update_count))
            msg = str(update_count) + " sites have updated!"
            notification.notify(search_keywords, msg)

    else:
        with open(pickle_filename, 'wb') as handle:
            pickle.dump(site_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
            notification.notify(search_keywords, (str(len(site_dict)) + " sites are being tracked!"))
    os.chdir('..')
    return update_count, update_index


def compare_dicts(dict1, dict2):
    update_count = 0
    update_index = [False] * len(dict1)
    i = 0
    for key in dict1.keys():
        if dict1[key] == dict2[key]:
            pass
            # TODO howto handle 0000 hashes?
            #print("Same hash!")
        else:
            update_count += 1
            update_index[i] = True
            #print(key + " has been updated!")
        i += 1
    return update_count, update_index
