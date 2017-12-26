
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



from random import sample
from string import ascii_lowercase





class ResultBundle:

    bundles = []

    def __init__(self, thread):
        self.google_query = ""
        self.thread = thread
        self.results = []
        self.update_index = []
        self.site_dict = {}



class TabbedLayout(TabbedPanel):




    def thread_id_pr (self):

        print(id(ResultBundle.bundles))

        for bundle in ResultBundle.bundles:
            print("query", bundle.google_query)
            print("thread id", bundle.thread.thread_id)
            print("results", bundle.results)
            print("updates", bundle.update_index)
            print("keys:")
            print(bundle.site_dict.keys())




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


    def sortFields(self):
        self.ids.fields.data = sorted(self.ids.fields.data, key=lambda x: x['text'])
        print(self.ids)

    def google_this(self, search_keywords, pages=2):

        if search_keywords in [bundle.google_query for bundle in ResultBundle.bundles]:
            bundle = ResultBundle.bundles[[bundle.google_query for bundle in ResultBundle.bundles].index(search_keywords)]
            bundle.results = google.search_iter(bundle,agr.iterThis, pages=pages)
            bundle.update_index = agr.pickle_dict(bundle)[1]

    def google_thread(self, pages):
        ls = [d['text'] for d in self.ids.fields.data if d['selected'] == True]
        if len(ls) == 0: return

        search_keywords = " ".join(ls)


        bundle = ResultBundle(trayNotification.intervalFuncTimer(40, self.google_this, xargs=[search_keywords, int(pages)]))
        bundle.google_query = search_keywords
        ResultBundle.bundles.append(bundle)
        bundle.thread.start()


        print(self.ids.keys())
        self.ids.threads.data.append({'text': bundle.google_query, 'selected': False})

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''''''


class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    is_not = BooleanProperty(True)

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


    def list_results(self, selection_list):

        print(selection_list)
        bundles = ResultBundle.bundles
        query = [d['text'] for d in selection_list if d['selected'] == True]
        query = query[0]
        print(query)

        
        bundle = bundles[[bundle.google_query for bundle in bundles].index(query)]

        self.rv.data = [{'name': x.name, 'link': x.link, 'description': x.description,
                         'was_updated': bundle.update_index[bundle.results.index(x)]} for x in bundle.results]


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

    def float_updated(self):
        self.rv.data = [x for x in self.rv.data if x['was_updated'] == True] +\
                       [x for x in self.rv.data if x['was_updated'] == False]



class TabbedLayoutApp(App):
    def build(self):
        return TabbedLayout()


if __name__ == '__main__':
    TabbedLayoutApp().run()


