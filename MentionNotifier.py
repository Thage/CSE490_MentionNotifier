
from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.tabbedpanel import TabbedPanel
import GoogleSearchIter as google
import ArchiverComperator as archComp
import IntervalFuncTimer
from kivy.properties import StringProperty
from kivy.uix.textinput import TextInput
import re

"""
.. module:: MentionNotifier
    :platform: Windows
    :synopsis: holds the Kivy Application of our project and mainly holds the functions used by the UI elements and the User. 

.. moduleauthor:: Berk Ergun
"""



class ResultBundle:
    '''
    Class holding the data for each ongoing search task.

    :var list bundles: List holding the ResultBundle instances.

    '''

    bundles = []

    def __init__(self, thread):

        '''

        Initialization method for ResultBundle.

        :param thread: intervalFuncTimer thread

        :var str google_query: Search query sent to Google Search.
        :var intervalFuncTimer thread: Recursive timer thread that runs a function at set intervals.
        :var list results: List holding the GoogleResult instances for the search.
        :var dict site_dic: Dictionary holding the key-value pairs for a link and it's hash.
        :var list last_updated: List of Python datetime objects, indicating when the last time each GoogleResult were updated.
        :var was_checked: List of booleans indicating whether a result was viewed by the User or not.

        '''

        self.google_query = ""
        self.keywords = None
        self.thread = thread
        self.results = []
        self.update_index = []
        self.site_dict = {}
        self.last_updated =[]
        self.was_checked = []




class MentionNotifier(TabbedPanel):

    '''
    Base UI element for the application inheriting from the kivy TabbedPanel class.
    The TabbedPanel widget manages different widgets in tabs, with a header area for the actual tab buttons and a content area for showing the current tab content.

    '''


    '''
    def thread_id_pr (self):

        print(id(ResultBundle.bundles))

        for bundle in ResultBundle.bundles:
            print("query", bundle.google_query)
            print("thread id", bundle.thread.thread_id)
            print("results", bundle.results)
            print("updates", bundle.update_index)
            print("keys:")
            print(bundle.site_dict.keys())

    '''


    def addField(self, text, selected=False):
        '''
        Function for adding a keyword in to the list of keywords.

        :param text: Keyword to be added.
        :param selected: Denotes whether the keyword t obe created is selected or not. Not accessible through user, for auxiliary purposes. Defaults to False.

        :return: Returns empty if text == "".
        '''


        #self.ids.fields.refresh_from_viewport()
        #print(self.ids.fields.data)
        if text == "": return
        self.ids.fields.data.append({'text': text, 'selected': selected})
        #self.ids.fields.refresh_from_layout()
        #
        self.ids.field_input.text = ""
        self.ids.fields.refresh_views()
        #print(self.ids.fields.data)

    def removeField(self):

        '''
        Function for removing selected a keyword from the keywords list.

        :return:
        '''
        for keyword in self.ids.fields.data:
            if keyword['selected']:
                self.ids.fields.data.remove(keyword)

        #print(self.ids.fields.data)
        #self.ids.fields.data.pop()
        #self.ids.fields.refresh_views()


    def google_this(self, search_keywords, pages=2):

        '''
        Function repeatedly called by a ResultBundle's intervalFuncTimer thread. Makes sure that the ResultBundle
        corresponding to it's query is still in the bundles list, then retrieves it. Then retrieves the GoogleResult
        instances for the google query with given page depth. Then sets the ResultBundle update_index by comparing
        it to a pickled iteration of the search, by matching the two's queries.

        :param search_keywords: The google query to be searched.
        :param pages: Depth of the google search to be done.

        :return:
        '''

        if search_keywords in [bundle.google_query for bundle in ResultBundle.bundles]:
            bundle = ResultBundle.bundles[[bundle.google_query\
                                           for bundle in ResultBundle.bundles].index(search_keywords)]
            bundle.results = google.search_iter(bundle, archComp.iterThis, pages=pages)
            bundle.update_index = archComp.pickle_dict(bundle)[1]


    def google_thread(self, pages, interval):

        '''
        Function for starting a search. Makes sure that a keywords is selected, then creates a google query string out
        of it. Then it creates a ResultBundle and creates it's thread with the given interval parameter. The thread
        calls on to the google_this function with the google query created and the number of pages to be searched.
        The function then adds this ResultBundle into the ResultBundle.bundles list and then starts the ResultBundle thread.

        '''

        ls = [d['text'] for d in self.ids.fields.data if d['selected'] == True]
        if len(ls) == 0: return

        ls = ['\"' + w + '\"' for w in ls if not w.startswith("-")] + [w for w in ls if w.startswith("-")]

        google_query = " ".join(ls)


        bundle = ResultBundle(IntervalFuncTimer.intervalFuncTimer(int(interval),
                                                                  self.google_this, xargs=[google_query, int(pages)]))
        bundle.google_query = google_query
        bundle.keywords = ls
        ResultBundle.bundles.append(bundle)
        bundle.thread.start()


        print(self.ids.keys())
        self.ids.threads.data.append({'text': bundle.google_query, 'selected': False})



class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    '''

    Custom UI element created by inheriting from multiple Kivy classes. Used for listing Keywords and Searches.
    The FocusBehavior mixin class provides keyboard focus behavior. (instances of self can be cycled by pressing tab.)
    LayoutSelectionBehavior adds selection behavior to layouts.
    RecycleBoxLayout provides a BoxLayout type layout for use with RecycleView widget.

    '''


class SelectableLabel(RecycleDataViewBehavior, Label):

    '''
    Custom selectable UI element created by inheriting from two Kivy classes. Used for representing and selecting each keyword or search.

    '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    is_not = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        '''
        Internal RecycleDataView Kivy class function overridden. Syncs the view and brings it up to date with the data.

        :param rv: RecycleView instance.
        :param index: The index of the SelectableLabel.
        :param data: Updated data dictionary kept in the back.
        :return: Calls the function onto self.

        :var index: Sets the index as self's index within a list.
        '''

        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        '''
        Internal Widget Kivy class function overrridden. When a new touch is registered, tests if it collides with the
         bounding box of another known gesture. Used for click detection for our purposes.


        :param touch: Touch Kivy object used to initialize the gesture container.

        :return:
        '''

        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        '''
        Applies a selection to the data dictionary of the RecycleView object in the background.


        :param rv: Recycleview instance.
        :param index: Index of self.
        :param is_selected: Whether if self is selected.

        :return:
        '''

        self.selected = is_selected
        if is_selected:
            rv.data[index]['selected'] = True
            #print("selection changed to {0}".format(rv.data[index]))
        else:
            rv.data[index]['selected'] = False
            #print("selection removed for {0}".format(rv.data[index]))
        #print("current selection: {0}".format([d for d in rv.data if d['selected'] == True]))



class Row(BoxLayout):
    '''
    Custom UI element created by inheriting from Kivy class BoxLayout. Used as the view class to represent each
    GoogleResult column in the ResultsList.

    :var str name: Kivy property that represents a string value. Title of a google result.
    :var str link: Kivy property that represents a string value. Link of a google result.
    :var str description: Kivy property that represents a string value. Description text of a google result.
    :var bool was_updated: Kivy property that represents a boolean value. Denotes whether the result was updated or not.
    :var str last_updated: Kivy property that represents a string value. Date when the object was last updated.
    :var str time_updated: Kivy property that represents a string value. Time when the object was last updated.
    :var str was_checked: Kivy property that represents a string value. Denotes whether the result was checked by the user or not.
    '''

    name = StringProperty()
    link = StringProperty()
    description = StringProperty()
    was_updated = BooleanProperty(False)
    last_updated_cal = StringProperty()
    last_updated_time = StringProperty()
    was_checked = StringProperty()




class GoogleResultsList(BoxLayout):
    '''
    Custom UI element created by inheriting from Kivy class BoxLayout. Used as the layout for Row class elements to be
    listed.
    '''



    def list_results(self, selection_list):
        '''
        Function listing the results of a ResultBundle as a Row in self.

        :param selection_list: List of searches. Used to pick the one that is selected.

        :return: Returns None if no search is selected.
        '''

        if not [d for d in selection_list if d['selected'] == True]: return

        bundles = ResultBundle.bundles
        query = [d['text'] for d in selection_list if d['selected'] == True]
        query = query[0]
        print(query)

        
        bundle = bundles[[bundle.google_query for bundle in bundles].index(query)]


        print("bun_res:", len(bundle.results))
        print("bun_lst:", len(bundle.last_updated))
        print("bun_was:", len(bundle.was_checked))

        print(bundle.results)
        self.rv.data = [{'name': x.name, 'link': x.link, 'description': x.description,
                         'was_updated': bundle.update_index[bundle.results.index(x)],
                         'was_checked': bundle.was_checked[bundle.results.index(x)],
                         'last_updated_time': '{:%H:%M:%S}'.format(bundle.last_updated[bundle.results.index(x)]),
                         'last_updated_cal': '{:%d/%b/%Y}'.format(bundle.last_updated[bundle.results.index(x)])}\
                        for x in bundle.results]


        #print([([y.name for y in x]) for x in google_results])
         #self.rv.data = [x[0].name for x in google_results]



    def float_updated(self):
        '''
        Brings the result Rows that are updated to the top of self.

        :returns:
        '''

        self.rv.data = [x for x in self.rv.data if x['was_updated'] == True] +\
                       [x for x in self.rv.data if x['was_updated'] == False]

    def set_blue(self, link, selection_list):
        '''
        Marks a Row as checked if it's link was used. This makes it's Updated text color blue, instead of red.

        :param link: Link that was just reacehd by the user.
        :param selection_list: List of searches. Used to pick the one that is selected.

        :return:
        '''

        bundles = ResultBundle.bundles
        query = [d['text'] for d in selection_list if d['selected'] == True][0]
        bundle = bundles[[bundle.google_query for bundle in bundles].index(query)]

        bundle.was_checked[[res.link for res in bundle.results].index(link)] = 'blue'
        [x for x in self.rv.data if x['link'] == link][0]['was_checked'] = 'blue'


    def stop_search(self, selection_list):

        '''
        Sets a SearchBundle to cancel it's thread and removes that SearchBundle from the list bundles.

        :param selection_list: List of searches. Used to pick the one that is selected.

        :return:
        '''


        d = [d for d in selection_list if d['selected'] == True]
        if not d: return

        print(selection_list)
        print(d)

        bundles = ResultBundle.bundles
        query = [d['text'] for d in selection_list if d['selected'] == True][0]
        bundle = bundles[[bundle.google_query for bundle in bundles].index(query)]

        bundle.thread.cancel()
        bundles.remove(bundle)
        selection_list.remove(d[0])




class MentionNotifierApp(App):
    '''
    Custom class inheriting from the Kivy App class. The base for our application, holds the entry point for the Kivy
    run loops.

    '''
    def build(self):
        '''
        Initializes the application; it will be called only once. Returns the MentionNotifier widget (tree), that will
        be used as the root widget and added to the window.

        :returns: MentionNotifier instance

        '''
        return MentionNotifier()

    def on_stop(self):
        '''
        Event function fired when the application stops. Useed to cancel each search thread running.

        :returns:

        '''
        for bundle in ResultBundle.bundles:
            bundle.thread.cancel()
            ResultBundle.bundles.remove(bundle)



if __name__ == '__main__':
    MentionNotifierApp().run()


