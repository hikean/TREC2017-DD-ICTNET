#!/usr/bin/python
# -*- encoding: utf-8 -*-

import multiprocess as mp


def target(process_id, process_count):
    import time
    for i in range(10):
        print("id:", process_id, "count:", process_count, "value", i)
        time.sleep(0.5)


def test_target():
    target(0, 0)


if __name__ == "__main__":
    mp.multi_main(target=target, test_target=test_target)
