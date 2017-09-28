# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/21 下午5:19
# @version: 1.0


from basic_init import *
from constants import *
from src.global_settings import *
from commands import getstatusoutput
import json as js


class JigClient_OLD(object):
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
        self.py3 = '/home/zhangwm/Software/anaconda2/bin/python'
        self.topic_id = topic_id
        print "base_jig_dir:", base_jig_dir
        self.jig_dir =  base_jig_dir  + "jig/jig.py" #JIG_DIR
        self.tot_itr_times = tot_itr_times
        self.base_dir = base_jig_dir


    def run_itr_str(self, docs, topic_id = None):
        if topic_id is not None:
            self.topic_id = topic_id

        # if self.itr_cnt >= self.tot_itr_times:
        #     logging.error("already itr %d times" % (self.tot_itr_times))
        #     return None

        # python jig/jig.py -runid baseline_LMD_ebola_pola_round2_0.txt -topic DD16-53 -docs gov_noaa_arctic_www_d8a34d5f3091ea5eb11927abeec4a4d69dc0c652_1424192786000:9.404923 org_aoncadis_www_11d8ee018007c2e131b36d8191a6b61d5256aed0_1424411940000:9.091631 org_aoncadis_www_11d8ee018007c2e131b36d8191a6b61d5256aed0_1424402850000:9.091631 org_nsidc_3893dd07b8e0a25a153f5dee9a47e2153cca41ac_1424234318000:9.056754 org_aoncadis_www_befe4ad6e466033a546ddfc7f33cd75b01b999b2_1424404116000:8.716417

        logging.info("start run itr:" + str(self.itr_cnt) + ", run_id:" + str(self.runid))
        docs_str = ""
        for d in docs:
            # DOCNO SCORE
            docs_str += ' ' + d[1] + ':' + str(d[2])
        docs_str = unicode(docs_str)
        cmd = self.py3 + ' ' + self.jig_dir + " -runid " + str(
            self.runid) + " -topic " + self.topic_id + " -docs" + docs_str

        # cmd = 'cd /home/zhangwm/Software/ebola_jig/trec-dd-jig && ' + cmd
        cmd = 'cd %s && %s' % ( self.base_dir, cmd )
        # necessary
        # cmd = 'export LC_ALL=en_US.utf-8 && export LANG=en_US.utf-8 && ' + cmd

        print "RUNING cmd:", cmd

        stat, output = getstatusoutput(cmd)

        print output
        return output


    def run_itr(self, docs, topic_id = None):
        if topic_id is not None:
            self.topic_id = topic_id
        # python jig/jig.py -runid baseline_LMD_ebola_pola_round2_0.txt -topic DD16-53 -docs gov_noaa_arctic_www_d8a34d5f3091ea5eb11927abeec4a4d69dc0c652_1424192786000:9.404923 org_aoncadis_www_11d8ee018007c2e131b36d8191a6b61d5256aed0_1424411940000:9.091631 org_aoncadis_www_11d8ee018007c2e131b36d8191a6b61d5256aed0_1424402850000:9.091631 org_nsidc_3893dd07b8e0a25a153f5dee9a47e2153cca41ac_1424234318000:9.056754 org_aoncadis_www_befe4ad6e466033a546ddfc7f33cd75b01b999b2_1424404116000:8.716417

        logging.info("start run itr:" + str(self.itr_cnt) + ", run_id:" + str(self.runid))
        docs_str = ""
        for d in docs:
            # DOCNO SCORE
            docs_str += ' ' + d[1] + ':' + str(d[2])
        docs_str = unicode(docs_str)
        cmd = self.py3 + ' ' + self.jig_dir + " -runid " + str(
            self.runid) + " -topic " + self.topic_id + " -docs" + docs_str

        # cmd = 'cd /home/zhangwm/Software/ebola_jig/trec-dd-jig && ' + cmd
        cmd = 'cd %s && %s' % ( self.base_dir, cmd )
        # necessary
        # cmd = 'export LC_ALL=en_US.utf-8 && export LANG=en_US.utf-8 && ' + cmd

        print "RUNING cmd:", cmd

        stat, output = getstatusoutput(cmd)

        # print output
        # return output

        if stat == 0:
            offset = output.find('\n')
            output = output[offset + 1:] #处理第一行的runid

            output = output.replace('\n', '')
            output = output.replace('\t', '')
            output = output.replace('''}{''', '''}=&&={''')
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
        # perl scorer/cubeTest_dd.pl scorer/qrels.txt baseline_LMD_ebola_pola_round2_0.txt.txt 5
        if runid is None:
            runid = self.runid
        runid_filename = '/home/zhangwm/Software/ebola_pola_jig/trec-dd-jig/' +  str(runid) + '.txt'

        cmd = 'perl  ' + self.base_dir + 'scorer/cubeTest_dd.pl ' + self.base_dir + 'scorer/qrels.txt ' + \
              runid_filename + ' ' + str(self.tot_itr_times)
        print "judge cmd:", cmd


        stat, output = getstatusoutput(cmd)
        try:
            logging.info("run %s  state %d:%s" % ("ct & act", stat, output))
            result = output
            print "result:"
            print result
        except Exception, e:
            print output
            logging.error("run %s  fail, exception: %s, state %d:%s" % (v, str(e), stat, output))

        return result

    def get_result_dict(self):
        return self.dict_result


if __name__ == '__main__':
    #python jig/jig.py -runid baseline_LMD_ebola_pola_round2_0.txt -topic DD16-53 -docs gov_noaa_arctic_www_d8a34d5f3091ea5eb11927abeec4a4d69dc0c652_1424192786000:9.404923 org_aoncadis_www_11d8ee018007c2e131b36d8191a6b61d5256aed0_1424411940000:9.091631 org_aoncadis_www_11d8ee018007c2e131b36d8191a6b61d5256aed0_1424402850000:9.091631 org_nsidc_3893dd07b8e0a25a153f5dee9a47e2153cca41ac_1424234318000:9.056754 org_aoncadis_www_befe4ad6e466033a546ddfc7f33cd75b01b999b2_1424404116000:8.716417
#baseline_LMD_ebola_pola_round2_0.txt
    docs = [
        (1, 'ebola-45b78e7ce50b94276a8d46cfe23e0abbcbed606a2841d1ac6e44e263eaf94a93', 833.00),
        (2, 'ebola-0000e6cdb20573a838a34023268fe9e2c883b6bcf7538ebf68decd41b95ae747', 500.00),
        (3, 'ebola-012d04f7dc6af9d1d712df833abc67cd1395c8fe53f3fcfa7082ac4e5614eac6', 123.00),
        (4, 'ebola-0002c69c8c89c82fea43da8322333d4f78d48367cc8d8672dd8a919e8359e150', 34.00),
        (5, 'ebola-9e501dddd03039fff5c2465896d39fd6913fd8476f23416373a88bc0f32e793c', 5.00)
    ]

    new_keys = [
        'ebola-ce7a8c22e0e70f53b0fbad9c833cd11763b3232e1a98d67ccb40f4613ea72e92',
        'ebola-2633ea7d217f20b55f526e307720099921aa7297b2aa6a516fa1fcae0b4dfec8',
        'ebola-91f6ec5acfaad446deeb6130a4d0c4b10c940933790aedbd4c9794412378d519',
        'ebola-c626b334499fe8bc8a49f132c7385e984d4ba9f15394d95f78fff36e1e3e09fd',
        'ebola-9d443104f755d5e6d4401d938ec8ca4cf204f41409804ab352a33d763962bafe'
        # 'ebola-ce7a8c22e0e70f53b0fbad9c833cd11763b3232e1a98d67ccb40f4613ea72e92',

    ]

    for i in range(len(new_keys)):
        docs[i] = list(docs[i])
        docs[i][1] = new_keys[i]
        docs[i] = tuple(docs[i])

    topic_id = 'DD16-27'

    jig = JigClient_OLD(topic_id, tot_itr_times=1, base_jig_dir=EBOLA_POLAR_JIG_DIR)
    dict_rslt = jig.run_itr(docs)
    for _ in dict_rslt:
        print _

    jig.judge()
    # print jig.get_result_dict()


__END__ = True