from plyer import notification
from threading import Timer

class intervalFuncTimer():

    #thread_id = 0

    def __init__(self,t,func, xargs):
        self.t=t
        self.func = func
        self.xargs = xargs
        self.thread = Timer(0,self.handle_function)
        #self.thread.name += str(self.thread_id)


    def handle_function(self):
        self.func(self.xargs)
        self.thread = Timer(self.t,self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


def notifier_test():
    notification.notify("Test Title", "Test Message")