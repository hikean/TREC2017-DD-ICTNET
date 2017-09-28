# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/9/11 下午3:26
# @version: 1.0


from src.utils.basic_init import *
from src.utils.constants import *
from src.utils.SolrClient import *


def get_all_ebola_solrs():
    solrs = [
        SolrClient(solr_url=FULL_SOLR_URL), #LMD, FULL
        SolrClient(solr_url=SOLR_FULL_BM25_URL),
        SolrClient(solr_url=SOLR_FULL_Classic_URL),
        SolrClient(solr_url=SOLR_FULL_IBS_URL),
        SolrClient(solr_url=SOLR_FULL_LMJM_URL),
        # SolrClient(solr_url=SOLR_FULL_DFR_G_L_H2)
    ]

    return solrs


def get_lm_ebola_solr():
    solrs = [
        SolrClient(solr_url=FULL_SOLR_URL),  # LMD, FULL
    ]
    return solrs


def get_all_polar_solrs():
    solrs = [
        SolrClient(solr_url=POLAR_FULL_URL), #LMD, FULL
    ]

    return solrs


def get_all_nyt_solrs():
    solrs = [
        SolrClient(SOLR_FULL_nyt_LMD_URL),

        SolrClient(SOLR_NYT_FULL_BM25_URL),
        SolrClient(SOLR_NYT_FULL_Classic_URL),
        SolrClient(SOLR_NYT_FULL_IBS_URL),
        SolrClient(SOLR_NYT_FULL_LMJM_URL),
    ]
    return solrs


def get_all_nyt_seg_solrs():

    # paths = [
    #     SOLR_SEG_nyt_LMD_URL,
    #     SOLR_SEG_nyt_BM25_URL,
    #     SOLR_SEG_nyt_DFR_URL,
    #
    # ]

    solrs = [
        SolrClient(SOLR_SEG_nyt_LMD_URL),
        # SolrClient(SOLR_SEG_nyt_IBS_URL),  # 0.44
        # SolrClient(SOLR_SEG_nyt_BM25_URL), #0.42
        # SolrClient(SOLR_SEG_nyt_DFR_URL), #0.41
        # SolrClient(SOLR_SEG_nyt_Classic_URL), #0.387
        # SolrClient(SOLR_SEG_nyt_LMJK_URL), #0.38
    ]
    return solrs

if __name__ == '__main__':
    pass

__END__ = True