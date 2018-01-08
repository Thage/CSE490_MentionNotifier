from threading import Timer

"""
.. module:: IntervalFuncTimer
    :platform: Windows
    :synopsis: holds the IntervalFuncTimer class, a modified Timer object recursively calling upon itself. Used to make continuous searches.

.. moduleauthor:: Berk Ergun
"""

class intervalFuncTimer:
    '''
    Class representing a perpetual python Timer object. Calls a it's function at initialization and then keeps calling
    it in set intervals. Can be stopped by setting the running bool flag as False.

    :var int thread_count: Number of intervalFuncTimer instances running.

    '''

    thread_count = 0

    def __init__(self,t,func, xargs):
        '''
        Initialization method for intervalFuncTimer.
        :param t: The interval as seconds that the Timer will be set to run at.
        :param func: The function to be iterated.
        :param xargs: Arguments for the function.

        :var bool running: Flag representing if the thread is running or not.
        :var t t: The interval as seconds that the Timer will be set to run at.
        :var func: The function to be iterated.
        :var xargs: Arguments for the function.
        :var  Timer thread: A thread that executes a function after a specified interval has passed.
        :var int thread_id: Thread id.
        '''

        self.running = False
        self.t=t
        self.func = func
        self.xargs = xargs
        self.thread = Timer(0,self.handle_function)
        intervalFuncTimer.thread_count += 1
        self.thread_id = intervalFuncTimer.thread_count


    def handle_function(self):
        '''
        Function deciding whether the self.func function should be called by checking the running flag.
        If it does, initializes and starts a new Timer for self that will call upon self.func at initialization.
        :return:
        '''
        if self.running:
            self.func(*self.xargs)
            self.thread = Timer(self.t,self.handle_function)
            self.thread.start()

    def start(self):
        '''
        Function that sets self as running and starts self's Timer thread.
        :return:
        '''
        self.running = True
        self.thread.start()

    def cancel(self):
        '''
        Function that sets self as not running. As there is no thread termination in Python threads, the thread will be
        running till it's nex iteration.
        :return:
                '''
        self.running = False
        intervalFuncTimer.thread_count += 1

