from threading import Thread
from queue import Queue
from functools import partial
import time

# Execute a given function concurrently using multiple threads
# and manage input and output queues.
class mt_Woker:
    def __init__(self,
                 exec_func: callable,
                 post_func: callable,
                 n_thread: int = 4):
        self.n_thread = n_thread
        self.exec_func = exec_func
        self.post_func = post_func
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.queue_end_value = "##END##"
        self.thread_list = []

    def add_item(self, item):
        self.input_queue.put(item)

    def _add_end_item(self):
        for i in range(self.n_thread):
            self.add_item(self.queue_end_value)

    def thread_exec_func(self,
                    func: callable):
        while True:
            try:
                current_input_value = self.input_queue.get(block=False)
            except:
                time.sleep(0.1)
                continue
            if isinstance(current_input_value,str) and current_input_value == self.queue_end_value:
                self.output_queue.put(self.queue_end_value)
                break
            else:
                result = func(*current_input_value)
                self.output_queue.put(result)
                

    def create_threads(self):
        for i in range(self.n_thread):
            _thread = Thread(
                target = partial(self.thread_exec_func, func = self.exec_func), 
                args = (),
                daemon = True
            )
            self.thread_list += [_thread]
        _thread = Thread(
                target = partial(self.post_func, 
                                 output_queue = self.output_queue,
                                 nthread = self.n_thread,
                                 end_value = self.queue_end_value), 
                args = (),
                daemon = True
            )
        self.thread_list += [_thread]
        
    def start_threads(self):
        for _thread in self.thread_list:
            _thread.start()
        for _thread in self.thread_list:
            _thread.join()

    def run(self):
        self._add_end_item()
        self.create_threads()
        self.start_threads()

