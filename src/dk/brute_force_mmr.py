import os
import threading

def mmr_thread(lam_a,lam_b,n_subtopic,n_round,n_doc_solr=1000,n_testtopic=27):
    os.popen("nohup python lda_mmr_scale.py " + "{} {} {} {}".format(lam_a,lam_b,n_subtopic,n_round) +" 1000 27 > ./result/" + "{}-{}-{}-{}".format(lam_a,lam_b,n_subtopic,n_round) +"-1000-27.log &")

def muti_thread(lam_a,k):
    lam_b = 0.0
    for lamb in range(100):
        lam_b +=0.01
        for n_subtopic in range(5,11):
            for n_round in [1,2,5,10]:
                th = threading.Thread(target=mmr_thread,args=(lam_a, lam_b, n_subtopic, n_round))  
                th.start()
                th.join()
    
    
if __name__ == '__main__':
    threads = []
    lam_a = 0.5
    
    for lama in range(50):
        lam_a += 0.01
        threads.append(threading.Thread(target = muti_thread,  args=(lam_a,0) ) ) 
        
    for thread in threads:
        thread.start()