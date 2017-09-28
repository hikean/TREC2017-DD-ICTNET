# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/22 下午3:30
# @version: 1.0

'''
从clean 读取，
'''


CONTENT = 'content'
TAGS = ["p", "h1", "h2", "h3", "h4", "h5", "title",]
JOIN_TAGS = ["p", "h1", "h2", "h3", "h4", "h5",]
METAS = ["site_name","description","generator", "title", "url", "image", "twitter:card", "robots", "twitter:image:src", "twitter:site", "google-site-verification", "type","viewport", ]
URL = 'url'
KEY = 'key'
DOC_ID = 'doc_id'

TO_COMBINE_KEYWORDS = [
"content_title", "content_metas_description", "content_p", "content_h1",  "content_h2", "content_h3", "content_h4", "content_h5", "content_metas_title"
]

import sys
import codecs
import json
from os.path import exists
import threading


def rearrange_ebola(in_file_name, out_file_name, fid, log=False):
    # if exists(out_file_name):
    #     return
    if not exists(in_file_name):
        print "[ERROR] file not exists:", in_file_name
        return
    ret = {}
    js = json.load(codecs.open(in_file_name, 'r'))
    ret[URL] = js[URL]
    ret[KEY] = js[KEY]
    ret[DOC_ID] = fid

    full_content = []
    for field in TO_COMBINE_KEYWORDS:
        if js.has_key(field):
            full_content.append( js[field].strip() )

    ret[CONTENT] = ' '.join(full_content)

    # with codecs.open(out_file_name, 'w', 'utf-8') as fl:
    with codecs.open(out_file_name, "w", "utf-8") as fl:
        if log:
            print "ret:", ret
        fl.write(json.dumps(ret))
        if log:
            print "succ dump:", out_file_name
        # json.dump(ret, fl)

def ebola_thread(in_dir, out_dir, thread_id, thread_count, file_count=194481):
    for i in range(file_count/thread_count + 2):
        file_id = i + thread_id * file_count / thread_count
        if i%100 == 0:
            # print "in, out:",in_dir.format(file_id), out_dir.format(file_id)
            rearrange_ebola(in_dir.format(file_id), out_dir.format(file_id), file_id, False)
        else:
            rearrange_ebola(in_dir.format(file_id), out_dir.format(file_id), file_id)

def main(in_dir, out_dir, thread_count):
    threads = [threading.Thread(target=ebola_thread, args=(i, thread_count, in_dir, out_dir)) for i in range(thread_count)]
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    # test()

    in_dir = "/home/zhangwm/Data/extract_ebola/clean_ebola_json/{}.json"
    out_dir = "/home/zhangwm/Data/ebola_full/ebola_clean_full/{}.json"
    if len(sys.argv) == 1:
        main(in_dir, out_dir, 4)
    elif len(sys.argv) == 3:
        ebola_thread(in_dir, out_dir, int(sys.argv[1]), int(sys.argv[2]))
    else:
        print "usage:\n\tpython ebola_extract.py <process_id> <process_count>"

__END__ = True