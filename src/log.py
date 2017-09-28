import time

log_level = 1

def log_info(s):
    print  time.strftime("%H:%M:%S",time.localtime(time.time())) +\
           " [INFO] " + s

def log_error(s):
    print  time.strftime("%H:%M:%S",time.localtime(time.time())) +\
           " [ERROR] " + s


def log_debug(s):
    if log_level == 1:
        print  time.strftime("%H:%M:%S",time.localtime(time.time())) +\
           " [DEBUG] " + s



def log_special_debug(s):
    print  time.strftime("%H:%M:%S",time.localtime(time.time())) +\
           " [DEBUG] " + s



def debug_list_ele_tuple(le):
    for i in le:
        print "debug_list_ele_tuple:" + str(i.to_tuple())