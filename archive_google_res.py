import hashlib
import pickle
import urllib, socket, ssl
import os
from plyer import notification
from bs4 import BeautifulSoup
from datetime import datetime



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

    #except (urllib.error.URLError, socket.timeout, ssl.CertificateError):
    except:
        bundle.site_dict[link] = "0"*128


def pickle_dict(bundle):
    update_count = 0
    update_index = [False] * len(bundle.site_dict)
    if not bundle.last_updated:
        bundle.last_updated = [datetime.now()] * len(bundle.site_dict)
    if not bundle.was_checked:
        bundle.was_checked = ['red'] * len(bundle.site_dict)

    pickle_filename = bundle.google_query.replace('\"', "") + '.pickle'
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
        update_count, update_index = compare_dicts(old_dict, bundle)


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

def compare_dicts(dict1, bundle): #OLD vs NEW
    dict2 = bundle.site_dict
    was_checked  = bundle.was_checked
    update_count = 0
    update_index = [False] * len(dict1)
    i = 0
    for key in dict1.keys():
        try:
            if dict1[key] == dict2[key]:
                update_index[i] = False
                i += 1

            elif dict1[key] != dict2[key]:
                update_count += 1
                update_index[i] = True
                bundle.last_updated[i] = datetime.now()
                bundle.was_checked[i] = 'red'
                i += 1
        except KeyError:
            #exception for when len(dict1) (old_dict) < len(dict2) (new_dict)
            pass

    for key in dict2.keys() - dict1.keys():
        finder = 0
        for key2 in dict2.keys():
            if key == key2:
                update_index.insert(finder, True)
                bundle.last_updated.insert(finder, datetime.now())
                bundle.was_checked.insert(finder, 'red')
                update_count += 1
            else:
                finder += 1

    return update_count, update_index




