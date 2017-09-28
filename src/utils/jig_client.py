# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/8 下午12:12
# @version: 1.0

from basic_init import *
from constants import *
from src.global_settings import *
from commands import getstatusoutput
import json as js


class JigClient(object):
    def __init__(self, topic_id, run_id_file=JIG_RUN_ID_FILE):
        self.runid = None
        with open(run_id_file, 'r') as fobj:
            self.runid = int(fobj.readline().strip()) + 1

        with open(run_id_file, 'w') as fobj:
            fobj.write(str(self.runid))
        if self.runid is None:
            logging.error("run id read write error")
            return
        else:
            logging.info("jig run id:" + str(self.runid))

        self.itr_cnt = 0
        self.py3 = PY3
        self.topic_id = topic_id
        self.jig_dir = JIG_DIR

    def run_itr(self, docs):
        logging.info("start run itr:" + str(self.itr_cnt) + ", run_id:" + str(self.runid))
        docs_str = ""
        for d in docs:
            # DOCNO SCORE
            docs_str += ' ' + d[1] + ':' + str(d[2])
        cmd = self.py3 + ' ' + self.jig_dir + " -runid " + str(
            self.runid) + " -topic " + self.topic_id + " -docs" + docs_str

        cmd = 'cd /home/zhangwm/Software/ebola_jig/trec-dd-jig && ' + cmd
        # necessary
        cmd = 'export LC_ALL=en_US.utf-8 && export LANG=en_US.utf-8 && ' + cmd

        # print "cmd:", cmd
        print "[#] run_id: ", self.runid

        stat, output = getstatusoutput(cmd)

        if stat == 0:
            offset = output.find('\n')
            output = output[offset+1:]
            output = output.replace('\n','')
            output = output.replace('\t','')
            output = output.replace('}{    "topic_id":', '}=&&={    "topic_id":')
            output = output.split('=&&=')

            logging.info("run itr succ, runid, itr cnt:" + str(self.runid) + " " + str(self.itr_cnt))
            try:
                rslt = [ js.loads(_.strip()) for _ in output ]

                # rslt = js.loads(output.strip())
                return rslt
            except Exception, e:
                logging.error("run itr, error:" + str(e))
                print "offset:", offset
                print "error output:"
                # for _ in output.split('=&&='):
                #     print _
        else:
            logging.error("run jig error:" + str(docs))
            print "err info:", output
            return None


# '''
# python3 scorer/cubetest.py --runfile testrun.txt --topics sample_run/topic.xml --params sample_run/params --cutoff 5
# python3 scorer/sDCG.py --runfile testrun.txt --topics sample_run/topic.xml --params sample_run/params --cutoff 5
# python3 scorer/expected_utility.py --runfile testrun.txt --topics sample_run/topic.xml --params sample_run/params --cutoff 5
# python3 scorer/precision.py -run testrun.txt -qrel sample_run/qrels.txt
# '''



    def judge(self, runid=None):
        if runid is None: runid = self.runid
        runid_filename = str(runid) + '.txt'
        result = []
        for v in ['cubetest.py','sDCG.py','expected_utility.py']:
            cmd = (self.py3 + ' scorer/%s --runfile %s --topics topics/dynamic-domain-2016-truth-data.xml --params ebola_run/params --cutoff 5')%(v, runid_filename)
            cmd = 'cd /home/zhangwm/Software/ebola_jig/trec-dd-jig && ' + cmd
            # necessary
            cmd = 'export LC_ALL=en_US.utf-8 && export LANG=en_US.utf-8 && ' + cmd

            # print "judge cmd:", cmd 

            stat, output = getstatusoutput(cmd)
            try:
                logging.info("run %s  state %d:%s"%(v, stat, output))
                result.append(output)
            except Exception,e:
                logging.error("run %s  fail, exception: %s, state %d:%s"%(v, str(e), stat, output))

        #TODO:add judge precision
        # cmd = (self.py3 + ' scorer/precision.py --runfile %s --topics topics/dynamic-domain-2016-truth-data.xml --params ebola_run/params --cutoff 5')%(v, runid_filename)

        for v in result:
            print v
        return result

if __name__ == '__main__':
    docs = [
        (1, 'ebola-45b78e7ce50b94276a8d46cfe23e0abbcbed606a2841d1ac6e44e263eaf94a93', 833.00),
        (2, 'ebola-0000e6cdb20573a838a34023268fe9e2c883b6bcf7538ebf68decd41b95ae747', 500.00),
        (3, 'ebola-012d04f7dc6af9d1d712df833abc67cd1395c8fe53f3fcfa7082ac4e5614eac6', 123.00),
        (4, 'ebola-0002c69c8c89c82fea43da8322333d4f78d48367cc8d8672dd8a919e8359e150', 34.00),
        (5, 'ebola-9e501dddd03039fff5c2465896d39fd6913fd8476f23416373a88bc0f32e793c', 5.00)
    ]
    topic_id = 'DD16-1'

    jig = JigClient(topic_id)
    # jig.run_itr(docs)
    jig.judge(7000047)
__END__ = True
