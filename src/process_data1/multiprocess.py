#!/usr/bin/python
# -*- encoding: utf-8 -*-

import logging
import os
import sys
import threading

from multiprocessing import Process
from functools import partial


def multithread(target, thread_count, *args, **kwargs):
    threads = [
        threading.Thread(target=target, args=targs, kwargs=kwargs)
        for targs in [
            (i, thread_count) + args for i in range(thread_count)
        ]
    ]
    for thread in threads:
        thread.start()


def multiprocess(target, process_count, *args, **kwargs):
    processes = [
        Process(target=target, args=pargs, kwargs=kwargs)
        for pargs in [
            (process_id, process_count) + args
            for process_id in range(process_count)
        ]
    ]
    for process in processes:
        process.start()


def multi_main(target, test_target=None, argv=sys.argv, *args, **kwargs):
    def usage():
        print((
            "Usage:\n" +
            "   python {0} test\n" +
            "   python {0} process <process_count>\n" +
            "   python {0} thread <thread_count>\n"
        ).format(os.path.basename(argv[0])))

    def self_main():
        if len(argv) == 2 and argv[1] == "test":
            if test_target is not None:
                test_target()
                return True
            else:
                return False
        elif len(argv) == 3 and argv[1] in ("process", "thread"):
            process_count = int(argv[2])
            if argv[1] == "process":
                multiprocess(target, process_count, *args, **kwargs)
            else:
                multithread(target, process_count, *args, **kwargs)
            return True
        return False
    try:
        if not self_main():
            usage()
    except Exception as e:
        logging.exception("exception: %s", e)


def target_example(process_id, process_count, file_count, in_dir, out_dir):
    """an example for target function:

    a target function must have arguments named `process_id`, `process_count`
    """
    def thread_example(in_file, out_file):
        import random
        import time
        t = random.randint(0, 50) / 5.0
        time.sleep(t)
        print(in_file, out_file, t)

    file_id = process_id
    while file_id < file_count:
        in_file = in_dir.format(file_id)
        out_file = out_dir.format(file_id)
        print("ID<{}>".format(process_id))
        thread_example(in_file, out_file)
        file_id += process_count


def simple_main(process_count):
    multiprocess(
        target_example, process_count,
        20, in_dir="in_dir/{}", out_dir="out_dir/{}"
    )


if __name__ == "__main__":
    in_dir, out_dir = "in/{}", "out/{}"
    test_target = partial(
        target_example, process_id=0, process_count=1,
        file_count=10, in_dir=in_dir, out_dir=out_dir
    )
    multi_main(
        target=target_example, test_target=test_target, argv=sys.argv,
        file_count=40, in_dir=in_dir, out_dir=out_dir
    )
