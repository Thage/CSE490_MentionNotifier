import hashlib
import pickle
import urllib, requests
import os
from plyer import notification
from bs4 import BeautifulSoup
from datetime import datetime


"""
.. module:: ArchiverComperator
    :platform: Windows
    :synopsis: holds the functions related to the creation, archival, retrieval and comparison of link:hash dictionaries both new and old.

.. moduleauthor:: Berk Ergun
"""

def iterThis(res, bundle):
    '''
    Function called for while iterating over GoogleResult's to hash them. Get's the source of a link (with a 3 second timmeout),
    pulls the <body> part from it and hashes that string. If body can't be retrieved, it uses the whole page instead. And if
    the page cannot be retreived at all, the hash is saved as an all-zero hash. Then stores it in the ResultBundle's
    site_dict as a value for the link's key.

    :param res: GoogleResult that the link of will be used.
    :param bundle: ResultBundle that it's site_dict will be used.
    :return:
    '''


    link = res.link
    print(link)
    try:
        #page = requests.get(link,headers=None,proxies=None,timeout=3)
        try:
            page = urllib.request.Request(link)
            page_source = urllib.request.urlopen(page, timeout=3).read()
            soup = BeautifulSoup(page_source, "html.parser")
            body = str(soup.find("body"))
        except:
            page = requests.get(link, headers=None, proxies=None, timeout=3)
            body = page.text

        bundle.site_dict[link] = hashlib.sha3_512(body.encode('utf-8')).hexdigest()

    #except (urllib.error.URLError, socket.timeout, ssl.CertificateError):
    except:
        bundle.site_dict[link] = "0"*128


def pickle_dict(bundle):

    '''
    Function called for when storing and comparing old and new site_dict values. Sets the update index, last_updated and
    was_checked values to default if they don't exist, then retrieves the pickle file corresponding to the bundle. Then it
    will compare the site_dict's of the old and the new and return the update_index which'll show whether a GoogleResult
    was updated or not. Then it'll save the new_dict into a pickle file, overwriting any existing one if it exists.
    Finally it'll file a notification announcing the number of updates within the bundle.

    :param bundle: ResultBundle
    :return:
    '''

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

    '''
    The comparator function for a new and old site_dict dictionary values.
        - If a link exists in both dicts and their hashes match, it'll do nothing.
        - If a link exists in both dicts but their hashes don't match, then it's and marked as updated.
        - If the old dict throws a KeyError, meaning it cannot find a link value in the new site_dict, it'll pass.

    After that, the links that are NOT in the old site_dict but are in the new site_dict are marked as updated.


    :param dict1: Old site_dict retrieved from a pickle stored.
    :param bundle: Bundle from which it's site_dict will be retrieved from and it's last_updated and was_checked values
    will be set.

    :returns: update_count, update_index

    '''

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




