# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/8 涓嬪崍12:12
# @version: 1.0

from basic_init import *
from constants import *
from src.global_settings import *
from commands import getstatusoutput
import json as js


class JigClient(object):
    def __init__(self, topic_id='DD16-1', tot_itr_times=5, run_id_file=JIG_RUN_ID_FILE, base_jig_dir=EBOLA_JIG_DIR):
        self.runid = None
        self.dict_result = {}
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
        self.jig_dir =  base_jig_dir  + "jig/jig.py" #JIG_DIR
        self.tot_itr_times = tot_itr_times
        self.base_dir = base_jig_dir

    def run_itr(self, docs, topic_id = None):
        if topic_id is not None:
            self.topic_id = topic_id
        print "run topic id:", self.topic_id
        # if self.itr_cnt >= self.tot_itr_times:
        #     logging.error("already itr %d times" % (self.tot_itr_times))
        #     return None

        logging.info("start run itr:" + str(self.itr_cnt) + ", run_id:" + str(self.runid))
        docs_str = ""
        for d in docs:
            # DOCNO SCORE
            docs_str += ' ' + d[1] + ':' + str(d[2])
        cmd = self.py3 + ' ' + self.jig_dir + " -runid " + str(
            self.runid) + " -topic " + self.topic_id + " -docs" + docs_str

        # cmd = 'cd /home/zhangwm/Software/ebola_jig/trec-dd-jig && ' + cmd
        cmd = 'cd %s && %s' % ( self.base_dir, cmd )
        # necessary
        cmd = 'export LC_ALL=en_US.utf-8 && export LANG=en_US.utf-8 && ' + cmd

        print "cmd:", cmd

        stat, output = getstatusoutput(cmd)

        if stat == 0 or stat == 256:
            if stat == 256:
                logging.warn("256 WARN")
            offset = output.find('\n')
            output = output[offset + 1:]
            output = output.replace('\n', '')
            output = output.replace('\t', '')
            output = output.replace('''}{    "topic_id":''', '''}=&&={    "topic_id":''')
            output = output.split('=&&=')

            logging.info("run itr succ, runid, itr cnt:" + str(self.runid) + " " + str(self.itr_cnt))

            try:
                # print "output:", output
                # for _ in output:
                #     print _
                rslt = [js.loads(_.strip()) for _ in output]
                self.itr_cnt += 1
                # rslt = js.loads(output.strip())
                return rslt
            except Exception, e:
                logging.error("run itr, error:" + str(e))
                print "offset:", offset
                print "print cmd:", cmd
                print "error output:"
                # for _ in output.split('=&&='):
                #     print _
                return None
        else:
            logging.error("run jig error:" + str(docs) + " status:" + str(stat))
            print "err info:", output
            print "print cmd:", cmd
            return None


            # '''
            # python3 scorer/cubetest.py --runfile testrun.txt --topics sample_run/topic.xml --params sample_run/params --cutoff 5
            # python3 scorer/sDCG.py --runfile testrun.txt --topics sample_run/topic.xml --params sample_run/params --cutoff 5
            # python3 scorer/expected_utility.py --runfile testrun.txt --topics sample_run/topic.xml --params sample_run/params --cutoff 5
            # python3 scorer/precision.py -run testrun.txt -qrel sample_run/qrels.txt
            # '''

    def judge(self, runid=None):
        if runid is None:
            runid = self.runid
        runid_filename = str(runid) + '.txt'
        result = []
        # for v in ['cubetest.py', 'sDCG.py', 'expected_utility.py']:
        for v in ['cubetest.py']:
            if self.base_dir == EBOLA_JIG_DIR:
                cmd = (
                      self.py3 + ' scorer/%s --runfile %s --topics topics/dynamic-domain-2016-truth-data.xml --params ebola_run/params --cutoff %d') % (
                      v, runid_filename, self.tot_itr_times)
            else:
                cmd = (
                          self.py3 + ' scorer/%s --runfile %s --topics topics/truth_data_nyt_2017_v2.3.xml --params nyt_run/params --cutoff %d') % (
                          v, runid_filename, self.tot_itr_times)
            # cmd = 'cd /home/zhangwm/Software/ebola_jig/trec-dd-jig && ' + cmd
            cmd = 'cd %s && %s' % ( self.base_dir, cmd)
            # necessary
            cmd = 'export LC_ALL=en_US.utf-8 && export LANG=en_US.utf-8 && ' + cmd

            print "judge cmd:", cmd

            stat, output = getstatusoutput(cmd)
            try:
                logging.info("run %s  state %d:%s" % (v, stat, output))
                result.append(output)
            except Exception, e:
                logging.error("run %s  fail, exception: %s, state %d:%s" % (v, str(e), stat, output))

        # TODO:add judge precision
        # cmd = (self.py3 + ' scorer/precision.py --runfile %s --topics topics/dynamic-domain-2016-truth-data.xml --params ebola_run/params --cutoff 5')%(v, runid_filename)
        print("result:\n")
        for v in result:
            print v

        #by jrq:...
        # for v in result:
        #     new_list = v.split("\n")
        #     name_row = new_list[1].split()
        #     for row_n in range(2, len(new_list)):
        #         score_row = new_list[row_n].split()
        #         for col_n in range(1, len(name_row)):
        #             key = (name_row[col_n], score_row[0])
        #             value = float(score_row[col_n])
        #             self.dict_result[key] = value

        return result

    def get_result_dict(self):
        return self.dict_result


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
    print jig.get_result_dict()

__END__ = True
