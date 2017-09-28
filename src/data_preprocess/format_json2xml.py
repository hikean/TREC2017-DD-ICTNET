# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/8 下午3:45
# @version: 1.0

from xml.dom.minidom import Document
from os.path import exists
import json
import sys
import codecs
import threading

def doc2xml(html_doc, doc_key):
    xml_doc = Document()
    cDOC = xml_doc.createElement('DOC')
    xml_doc.appendChild(cDOC)

    DCNO = xml_doc.createElement('DOCNO')
    DCNO_text = xml_doc.createTextNode(doc_key)
    DCNO.appendChild(DCNO_text)
    cDOC.appendChild(DCNO)

    TEXT = xml_doc.createElement('TEXT')
    TEXT_text = xml_doc.createTextNode(html_doc)
    TEXT.appendChild(TEXT_text)
    cDOC.appendChild( TEXT )

    return xml_doc

def parse_json(fn, out_fn):
    js = json.load(codecs.open(fn, 'r'))
    html_doc = js['content']
    key = js['key']
    xml_doc = doc2xml(html_doc, key)
    out_fn = out_fn.format(key)
    with codecs.open(out_fn, "w", "utf-8") as fobj:
        for node in xml_doc.childNodes:
            node.writexml(fobj, indent='', addindent='', newl='\n')

    # with codecs.open(out_fn, "w") as fobj:
    #     print type(xml_doc.toprettyxml(encoding='utf-8'))
    #     fobj.write( xml_doc.toprettyxml(encoding='utf-8') )
        # fobj.write(xml_doc.toxml(encoding='utf-8'))

def test():
    data_dir = "/Users/zhangweimin/Desktop/FileTransfer/"
    fn = data_dir + "100001.json"
    out = data_dir + "100001.xml"

    parse_json(fn, out)


# test()

def ebola_thread(in_dir, out_dir, thread_id, thread_count, file_count=194481):
    for i in range(file_count/thread_count + 2):
        file_id = i + thread_id * file_count / thread_count
        in_fn = in_dir.format(file_id)
        if exists(in_fn):
            parse_json(in_fn, out_dir)


def main(in_dir, out_dir, thread_count):
    threads = [threading.Thread(target=ebola_thread, args=(i, thread_count, in_dir, out_dir)) for i in range(thread_count)]
    for thread in threads:
        thread.start()

if __name__ == '__main__':
    # test()
    in_dir = "/home/zhangwm/Data/ebola/{}.json"
    out_dir = "/home/zhangwm/Data/ebola_trectext/{}"
    if len(sys.argv) == 1:
        main(in_dir, out_dir, 4)
    elif len(sys.argv) == 3:
        ebola_thread(in_dir, out_dir, int(sys.argv[1]), int(sys.argv[2]))
    else:
        print "usage:\n\tpython ebola_extract.py <process_id> <process_count>"

__END__ = True