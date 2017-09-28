# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/7/20 下午4:37
# @version: 1.0

'''
由于ebola的数据是嵌套的
读取hyk的json数据，然后写成做index的json格式

'''

CONTENT = 'content'
TAGS = ["p", "h1", "h2", "h3", "h4", "h5", "title",]
JOIN_TAGS = ["p", "h1", "h2", "h3", "h4", "h5",]
METAS = ["site_name","description","generator", "title", "url", "image", "twitter:card", "robots", "twitter:image:src", "twitter:site", "google-site-verification", "type","viewport", ]
URL = 'url'
KEY = 'key'
DOC_ID = 'doc_id'

import sys
import codecs
import json
from os.path import exists
import threading

def process_str_list(str_list):
    ret = []
    for i,s in enumerate(str_list):
        s = s.strip()
        if len(s) == 0:
            continue
        s1 = s.replace('\r', ' ').replace('\n', ' ')
        s2 = ' '.join([_.strip() for _ in s1.split(' ') if len(_.strip()) != 0])
        ret.append( s2 )
    return ret

def rearrange_ebola(in_file_name, out_file_name, fid, log=False):
    # if exists(out_file_name):
    #     return
    if not exists(in_file_name):
        print "[ERROR] file not exists:", in_file_name
        return
    ret = {}
    js = json.load(codecs.open(in_file_name, 'r'))
    inner_content = js[CONTENT]
    # print "Json type:", type(js)
    # print "CHECK inner_content:", type(inner_content)
    ret[URL] = js[URL]
    ret[KEY] = js[KEY]
    ret[DOC_ID] = fid
    for tag in TAGS:
        tag_key = 'content_' + tag
        if not inner_content.has_key(tag) or inner_content[tag] is None:
            inner_content[tag_key] = ""
            continue

        if type(inner_content[tag]) == list:
            inner_content[tag] = ' '.join(process_str_list(inner_content[tag]))
        else:
            try:
                inner_content[tag] = inner_content[tag].strip()
            except Exception, e:
                print "Error type:", type(inner_content[tag])
                inner_content[tag] = ""

        ret[tag_key] = inner_content[tag]

    inner_metas = inner_content["metas"]
    prefix = "content_metas_"
    for tag in METAS:
        if not inner_metas.has_key(tag) or inner_metas[tag] is None:
            ret[prefix+tag] = ""
        else:
            ret[prefix + tag] = inner_metas[tag]

            # print "ret:", ret

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

def test():
    in_file = "/Users/zhangweimin/Desktop/FileTransfer/99998.json"
    out_file = "/Users/zhangweimin/Desktop/FileTransfer/rearrange_99998.json"
    rearrange_ebola(in_file, out_file, 99998)

# test()

if __name__ == '__main__':
    # test()
    in_dir = "/home/zhangwm/Data/extract_ebola/clean_ebola_json/{}.json"
    out_dir = "/home/zhangwm/Data/extract_ebola/clean_ebola_full/{}.json"
    if len(sys.argv) == 1:
        main(in_dir, out_dir, 4)
    elif len(sys.argv) == 3:
        ebola_thread(in_dir, out_dir, int(sys.argv[1]), int(sys.argv[2]))
    else:
        print "usage:\n\tpython ebola_extract.py <process_id> <process_count>"

__END__ = True