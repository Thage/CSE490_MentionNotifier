import hashlib
import requests
import pickle
import urllib, socket
import os
from plyer import notification
from bs4 import BeautifulSoup




def iterThis(res, bundle):
    link = res.link
    print(link)
    try:
        #page = requests.get(link,headers=None,proxies=None,timeout=3)
        page = urllib.request.Request(link)
        page_source = urllib.request.urlopen(page, timeout=3).read()
        soup = BeautifulSoup(page_source, "html.parser")
        body = str(soup.find("body"))
        bundle.site_dict[link] = hashlib.sha3_512(body.encode('utf-8')).hexdigest()

    except (urllib.error.URLError, socket.timeout, requests.exceptions.ConnectionError):
        bundle.site_dict[link] = "0"*128


def pickle_dict(bundle):
    update_count = 0
    update_index = [False] * len(bundle.site_dict)
    pickle_filename = bundle.google_query + '.pickle'
    os.chdir('pickles')
    if os.path.isfile(pickle_filename):
        #print("yay")
        with open(pickle_filename, 'rb') as handle:
            old_dict = pickle.load(handle)
            #print(old_dict.keys())
        '''
        print(site_dict.keys() - old_dict.keys())
        print("SITE_DICT_KEYS")
        print(site_dict.keys())
        print("OLD_DICT_KEYS")
        print(old_dict.keys())
        '''

        #print("**")
        update_count, update_index = compare_dicts(old_dict, bundle.site_dict)
        print(update_index)
        #print(">>" + str(update_count))
        msg = str(update_count) + " sites have updated!"

        with open(pickle_filename, 'wb') as handle:
            pickle.dump(bundle.site_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        notification.notify(bundle.google_query, msg)




    else:
        with open(pickle_filename, 'wb') as handle:
            pickle.dump(bundle.site_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
            notification.notify(bundle.google_query, (str(len(bundle.site_dict)) + " sites are being tracked!"))
    os.chdir('..')
    return update_count, update_index

'''

def compare_dicts(dict1, dict2):
    zero_hash = "0"*128
    update_count = 0
    update_index = [False] * len(dict1)
    i = 0
    for key in dict1.keys():
        if dict1[key] == dict2.get(key, zero_hash):
            pass
            # TODO howto handle 0000 hashes?
            #print("Same hash!")
        else:
            update_count += 1
            update_index[i] = True
            #print(key + " has been updated!")
        i += 1
    return update_count, update_index

'''

def compare_dicts(dict1, dict2): #OLD vs NEW
    update_count = 0
    update_index = [False] * len(dict1)
    i = 0
    for key in dict1.keys():
        if dict1[key] == dict2[key]:
            update_index[i] = False
            i += 1

        elif dict1[key] != dict2[key]:
            update_count += 1
            update_index[i] = True
            i += 1

    for key in dict2.keys() - dict1.keys():
        finder = 0
        for key2 in dict2.keys():
            if key == key2:
                update_index.insert(finder, True)
                update_count += 1
            else:
                finder += 1

    return update_count, update_index




