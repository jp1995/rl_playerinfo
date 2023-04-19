import signal

from webdriver.webdriver_conf import chromedriver_conf, geckodriver_conf, choosedriver
from threading import Thread
import queue

"""I totally wrote all of this myself and definitely didn't copy from SO :)"""


def threaded_requests(addresses, no_workers, useragent_arr):
    class Worker(Thread):
        def __init__(self, request_queue):
            Thread.__init__(self)
            self.queue = request_queue
            self.results = []

        def run(self):
            while True:
                content = self.queue.get()
                if content == "":
                    break

                if choosedriver() == 'Chrome':
                    resp = chromedriver_conf(content, useragent_arr).split(';">')[1].split('</pre>')[0]
                elif choosedriver() == 'Firefox':
                    resp = geckodriver_conf(content, useragent_arr).split('json">')[1].split('</div>')[0]
                else:
                    'Chrome or Firefox not installed, cannot continue.'
                    quit(signal.SIGTERM)

                self.results.append(resp)
                self.queue.task_done()

    # Create queue and add addresses
    q = queue.Queue()
    for url in addresses:
        q.put(url)

    # Workers keep working till they receive an empty string
    for _ in range(no_workers):
        q.put("")

    # Create workers and add tot the queue
    workers = []
    for _ in range(no_workers):
        worker = Worker(q)
        worker.start()
        workers.append(worker)
    # Join workers to wait till they finished
    for worker in workers:
        worker.join()

    # Combine results from all workers
    r = []
    for worker in workers:
        r.extend(worker.results)
    return r
