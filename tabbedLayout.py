
from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.tabbedpanel import TabbedPanel
import google_search_iter as google
import archive_google_res as agr
import trayNotification
from kivy.properties import StringProperty
from HoverBehavior import HoverBehavior


from random import sample
from string import ascii_lowercase

google_queries = []
google_results = []
google_threads = []
update_index = []



class ResultBundle:

    def __init__(self, thread):
        self.google_query = ""
        self. thread = thread
        self.results = []
        update_index = []

class TabbedLayout(TabbedPanel):


    def thread_id_pr (self):
        global google_threads
        for thread in google_threads:
            print(thread.thread_id)



    def addField(self, text, selected=False):
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
        for keyword in self.ids.fields.data:
            if keyword['selected']:
                self.ids.fields.data.remove(keyword)

        #print(self.ids.fields.data)
        #self.ids.fields.data.pop()
        #self.ids.fields.refresh_views()

    def print_google_results(self):
        print((google_threads))
        print((google_results))

    def sortFields(self):
        self.ids.fields.data = sorted(self.ids.fields.data, key=lambda x: x['text'])
        print(self.ids)

    def google_this(self, ls):
        global update_index
        if len(ls) == 0: return
        search_keywords = " ".join(ls)
        if search_keywords in google_queries:
            google_results.insert(google_queries.index(search_keywords),
                                       google.search_iter(search_keywords, agr.iterThis, pages=2))
        else:
            google_results.append(google.search_iter(search_keywords, agr.iterThis, pages=2))
        update_index = agr.pickle_dict(search_keywords)[1]

        #print(google_results[0])

    def google_thread(self):
        global google_threads
        ls = [d['text'] for d in self.ids.fields.data if d['selected'] == True]
        thread = trayNotification.intervalFuncTimer(40, self.google_this, xargs=ls)
        thread.start()
        google_threads.append(thread)

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''''''


class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):

        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):

        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):

        self.selected = is_selected
        if is_selected:
            rv.data[index]['selected'] = True
            #print("selection changed to {0}".format(rv.data[index]))
        else:
            rv.data[index]['selected'] = False
            #print("selection removed for {0}".format(rv.data[index]))
        #print("current selection: {0}".format([d for d in rv.data if d['selected'] == True]))



class Row(BoxLayout):

    name = StringProperty()
    link = StringProperty()
    description = StringProperty()
    was_updated = BooleanProperty(False)



class GoogleResultRow(BoxLayout):

    def list_results(self):
        if len(google_results) == 0: return
        #self.rv.data = [{'value': ''.join(sample(ascii_lowercase, 6))} for x in range(50)]
        self.rv.data = [{'name': x.name, 'link': x.link, 'description': x.description,
                         'was_updated': update_index[google_results[0].index(x)]} for x in google_results[0]]
        #test
        # self.rv.data = [{'name': "name", 'link': "http://www.google.com", 'description': "blahblah"} for x in range(20)]

        #print([([y.name for y in x]) for x in google_results])
         #self.rv.data = [x[0].name for x in google_results]
    def highlight_updated(self):
        self.rv.data = sorted(self.rv.data, key=lambda x: x['value'])

    def clear(self):
        self.rv.data = []

    def insert(self, value):
        self.rv.data.insert(0, {'value': value or 'default value'})

    def update(self, value):
        if self.rv.data:
            self.rv.data[0]['value'] = value or 'default new value'
            self.rv.refresh_from_data()

    def remove(self):
        if self.rv.data:
            self.rv.data.pop(0)



class TabbedLayoutApp(App):
    def build(self):
        return TabbedLayout()


if __name__ == '__main__':
    TabbedLayoutApp().run()


