from threading import Timer

class intervalFuncTimer:

    thread_count = 0

    def __init__(self,t,func, xargs):
        self.running = False
        self.t=t
        self.func = func
        self.xargs = xargs
        self.thread = Timer(0,self.handle_function)
        intervalFuncTimer.thread_count += 1
        self.thread_id = intervalFuncTimer.thread_count


    def handle_function(self):
        if self.running:
            self.func(*self.xargs)
            self.thread = Timer(self.t,self.handle_function)
            self.thread.start()

    def start(self):
        self.running = True
        self.thread.start()

    def cancel(self):
        self.running = False

