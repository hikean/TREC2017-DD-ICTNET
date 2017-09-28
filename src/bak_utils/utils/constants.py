# -*- coding: utf-8 -*-
# @author: Weimin Zhang (weiminzhang199205@163.com)
# @date: 17/8/6 上午5:08
# @version: 1.0

from basic_init import *


#solr ebola
SOLR_EBOLA_LMD2500 = "http://172.22.0.11:8983/solr/ebola_lmd2500/select?"
SOLR_EBOLA_CLEAN_FULL_WITH_A = "http://10.61.2.164:8978/solr/ebola_lmd_atc/select?"
SOLR_EBOLA_PARAGRAPH = "http://10.61.2.168:8989/solr/ebola_paragraph/select?"
FULL_SOLR_URL = "http://172.22.0.11:8983/solr/ebola_extract/select?"
BASE_SOLR_URL = "http://172.22.0.17:8983/solr/ebola_v2/select?"
SOLR_BM25_URL = "http://172.22.0.17:8983/solr/ebola_v3_bm25/select?"
SOLR_DFR_URL = "http://172.22.0.17:8983/solr/ebola_v4_DFR/select?"
SOLR_FULL_BM25_URL = "http://172.22.0.17:8983/solr/ebola_full_BM25Similarity/select?"
SOLR_FULL_Classic_URL = "http://172.22.0.17:8983/solr/ebola_full_ClassicSimilarityFactory/select?" #ebola_full_ClassicSimilarityFactory
SOLR_FULL_IBS_URL = "http://172.22.0.17:8983/solr/ebola_full_IBSimilarityFactory/select?" # ebola_full_IBSimilarityFactory
SOLR_FULL_LMJM_URL = "http://172.22.0.17:8983/solr/ebola_full_LMJelinekMercerSimilarityFactory/select?"
SOLR_FULL_DFR_G_L_H2 = "http://172.22.0.17:8983/solr/ebola_full_DFR_G_L_H2/select?"

#solr nyt
SOLR_SEG_nyt_LMD_URL = "http://10.61.2.164:8983/solr/nyt_6_sep/select?"
SOLR_SEG_nyt_BM25_URL = "http://10.61.2.164:8981/solr/nyt_sep_BM25_v2/select?"
SOLR_SEG_nyt_DFR_URL = "http://10.61.2.164:8982/solr/nyt_sep_DFR_G_L_H2/select?" #ok
SOLR_SEG_nyt_Classic_URL = "http://10.61.2.164:8984/solr/nyt_sep_ClassicSimilarityFactory/select?"

SOLR_SEG_nyt_LMD10_URL = "http://10.61.2.164:8986/solr/nyt_lmd_10/select?"
SOLR_SEG_nyt_LMD1500_URL = "http://10.61.2.164:8986/solr/nyt_lmd_1500/select?"
SOLR_SEG_nyt_LMD768_URL = "http://10.61.2.164:8986/solr/nyt_lmd_768/select?"

#文档数目没有对应上,,, 1,831,096
SOLR_SEG_nyt_LMJK_URL = "http://10.61.2.164:8984/solr/nyt_sep_LMJelinekMercerSimilarityFactory/select?"
#1,831,096
SOLR_SEG_nyt_IBS_URL = "http://10.61.2.164:8981/solr/nyt_sep_IBS_v2/select?"
#nyt_sep_IBS_v2
SOLR_FULL_nyt_LMD_URL = "http://10.61.2.164:8983/solr/nyt_7_full/select?"
POLAR_FULL_URL = "http://172.22.0.11:8983/solr/polar_extract/select?"
SOLR_NYT_FULL_BM25_URL = "http://10.61.2.164:8981/solr/nyt_BM25_FULL/select?"
SOLR_NYT_FULL_Classic_URL = "http://10.61.2.164:8984/solr/nyt_full_ClassicSimilarityFactory/select?"
SOLR_NYT_FULL_IBS_URL = "http://10.61.2.164:8981/solr/nyt_full_IBSimilarityFactory/select?" #
SOLR_NYT_FULL_LMJM_URL = "http://10.61.2.164:8984/solr/nyt_full_LMJelinekMercerSimilarityFactory/select?"



RET_DOC_CNT = 1000
JIG_BASE_DIR = "/home/zhangwm/Software/ebola_jig/trec-dd-jig/"
JIG_DIR = JIG_BASE_DIR + "jig/jig.py"
RULT_FILES = ['cubetest', 'sDCG', 'expected_utility', 'precision' ]

#JIG
JIG_SCOCER_CUBETEST = JIG_BASE_DIR + "scorer/cubetest.py"
JIG_SCOCER_SDCG = JIG_BASE_DIR + "scorer/sDCG.py"
JIG_SCOCER_eu = JIG_BASE_DIR + "scorer/expected_utility.py"
JIG_SCOCRE_PRECISION = JIG_BASE_DIR + "scorer/precision.py"
JIG_RUN_ID_FILE = os.path.join(up, 'src', 'utils', 'jig_runid') #"./jig_runid"  #int(open("./jig_runid", 'r').readline().strip())

EBOLA_JIG_DIR = "/home/zhangwm/Software/ebola_jig/trec-dd-jig/"
NYT_JIG_DIR = "/home/zhangwm/Software/nyt_jig/trec-dd-jig/"

EBOLA_POLAR_JIG_DIR = "/home/zhangwm/Software/ebola_pola_jig/trec-dd-jig/"
EBOLA_NYT_JIG_DIR = "/home/zhangwm/Software/jig/trec-dd-jig/"

EBOLA_FULL_DATA_DIR = "/home/zhangwm/Data/ebola_full/ebola_htmls/"
EBOLA_CLEAN_SEG_DATA_DIR = "/home/zhangwm/Data/extract_ebola/clean_ebola_json/"
EBOLA_CLEAN_FULL_DATA_DIR = "/home/zhangwm/Data/ebola_full/ebola_clean_full/"
EBOLA_FULL_NOT_CLEAN = "/home/zhangwm/Data/ebola_full/ebola_htmls/"

NYT_SEG_DATA_DIR = "/home/zhangwm/trec/datas/nonested/"

ID2KEY_FILE = "/home/zhangwm/trec/datas/id2key.json"
KEY2ID_FILE = "/home/zhangwm/trec/datas/key2id.json"  #这个事真的对应的
FULL_KEY2ID = "/home/zhangwm/Data/ebola_full/key2id.json"

#fields
DOC_ID = 'doc_id'
KEY = 'key'
SCORE = 'score'
QFIELD = 'qfield'
DOCSEGMENT = 'docseg'


#env
PY3 = "/home/zhangwm/Software/anaconda2/envs/anaconda_py3/bin/python3"


#w2v
w2v_content_model = "/home/zhangwm/zhangweimin/Data/trec/build_data/ebola/textmodel/content_w2v.model"


#idf dic, idf_dic_path是ebola的
# idf_dic_path = "/home/zhangwm/Data/processed/idf_dict.json" #"/home/trec17dd/dk/data/dict.txt"
idf_dic_path = "/home/zhangwm/Data/processed/ebola_withoutstem_idf.json"
ebola_nostem_idf_dic_path_clean = "/home/zhangwm/Data/processed/ebola_withoutstem_idf.json"
nyt_idf_idf_dic_nostem = "/home/zhangwm/Data/processed/nyt_withoutstem_idf.json"
nyt_idf_idf_dic_stem = "/home/zhangwm/Data/processed/nyt_stem_idf.json"
nyt_idf_idf_dic_nostem_clean = "/home/zhangwm/Data/processed/nyt_withoutstem_idf_clean.json"
nyt_idf_idf_dic_stem_clean = "/home/zhangwm/Data/processed/nyt_stem_idf_clean.json"


#LM, clean表示做过poker
LMDirichlet_Json = "/home/zhangwm/Data/processed/lmdirichlet.json"
LMDirichlet_clean_Json = "/home/zhangwm/Data/processed/lmdirichlet_clean.json"
LMDirichlet_without_stem_raw = "/home/zhangwm/trec/datas/LangModel/ebola_words.lm.json"
LMDirichlet_without_stem = "/home/zhangwm/Data/processed/ebola_lmdirichlet_without_stem.json"
LMDirichlet_without_stem_lower = "/home/zhangwm/Data/processed/ebola_lmdirichlet_without_stem_lower.json"


#jig ret field
'''
{u'ranking_score': u'6.985157', u'on_topic': u'1', u'doc_id': u'ebola-0a1f583c29ebe8fce10acdf686a1f3b1d32d82985edb832066e7e6f0700e2d3b', u'subtopics': [{u'rating': 3, u'subtopic_id': u'DD16-1.3', u'passage_text': u'Defense Secretary Chuck Hagel on Wednesday approved a recommendation by military leaders that all US troops returning from Ebola response missions in West Africa be kept in supervised isolation for 21 days.'}], u'topic_id': u'DD16-1'}

doc_id: the id of a document
subtopic_id: the id of a relevant subtopic that the document covers
passage_text: the content of a relevant passage that the document covers
rating: the graded relevance judgments provided by NIST assessors. less than 2: marginally relevant, 2: relevant, 3: highly relevant, 4: key results. The relevance grades refer to the relevance level of the passage to a subtopic.
ranking score: the ranking score of a document provided by your system
'''

RATING = 'rating'
SUBTOPIC_ID = 'subtopic_id'
ON_TOPIC = 'on_topic'
SUBTOPICS = 'subtopics'
TEXT = 'passage_text'


#输入给jig的tuple的格式
DOC_ID_IDX_JIG = 0
KEY_IDX_JIG = 1
SCORE_IDX_JIG = 2
DOC_SEG_IDX = 3

#TOPICS
EBOLA_TOPICS_INIT = [('DD16-1', 'US Military Crisis Response'),
          ('DD16-2', 'Ebola Conspiracy Theories'),
          ('DD16-3', 'healthcare impacts of ebola'),
          ('DD16-4', 'Daniel Berehulak'),
          ('DD16-5', 'Ewedu as an Ebola Treatment'),
          ('DD16-6', 'Alleged Alternative Treatments for Ebola'),
        # ('DD16-7', 'Urbanisation/Urbanization'),
          ('DD16-7', 'Urbanisation Urbanization'),
          ('DD16-8', 'Dr. Olivet Buck'),
          ('DD16-9', 'Thomas Eric Duncan'),
          ('DD16-10', 'Economic impact of ebola'),
          ('DD16-11', 'U.S. healthcare workers'),
          ('DD16-12', 'is there a natural immunity to ebola'),
          ('DD16-13', 'Dr. Steven Hatch'),
          ('DD16-14', 'T.B. Joshua'),
          ('DD16-15', 'Maurice Iwu'),
          ('DD16-16', 'Modeling'),
          ('DD16-17', 'Kenema District Government Hospital'),
          ('DD16-18', 'Robots'),
          ('DD16-19', 'Attacks on ebola aid'),
          ('DD16-20', 'Pauline Cafferkey'),
          ('DD16-21', 'Ebola medical waste'),
          ('DD16-22', 'radio school'),
          ('DD16-23', 'Crowdfunding Crowdsourcing'),
          ('DD16-24', 'Olu-Ibukun Koye Spread EVD to Port Harcourt'),
          ('DD16-25', "Emory University's role in Ebola treatment"),
          ('DD16-26', 'Effects of African Culture'),
          ('DD16-27', 'kaci hickox'),
          ('DD16-28', 'Is the distribution of permafrost changing in the Arctic?'),
          ('DD16-29', 'ice sheet sea level rise'),
          ('DD16-30', 'Where are basal boundary conditions in East Antarctica?'),
          ('DD16-31', 'sea level rise change strom surge'),
          ('DD16-32', 'polar oceans freshwater sensitivity'),
          ('DD16-33', 'sea-level rise and coastal erosion'),
          ('DD16-34', 'melting ice sheet ocean circulation'),
          ('DD16-35', 'snow accumulation rate Greenland'),
          ('DD16-36', 'Is the rate of snow accumulation changing in Antarctica?'),
          ('DD16-37', 'west antarctic ice sheet'),
          ('DD16-38', 'Are significant changes occurring in ocean productivity'),
          ('DD16-39',
           'How will shipping be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-40', 'Polar terrestrial ecosystems CO2 trace gas'),
          ('DD16-41', 'Artic sea ice fishery'),
          ('DD16-42',
           'How will offshore mineral extraction be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-43', 'Is ice sheet elevation changing'),
          ('DD16-44',
           'Are changes occurring in the distribution and productivity of Arctic vegetation?'),
          ('DD16-45',
           'How will subsistence fishing and hunting be impacted by changes in Arctic sea ice characteristics?'),
          ('DD16-46', 'Are changes occurring the coverage of the Arctic Sea ice'),
          ('DD16-47', 'Arctic sea ice thickness'),
          ('DD16-48', 'polar ocean global ocean circulation'),
          ('DD16-49', 'Are changes occurring in the circulation of the Arctic Sea'),
          ('DD16-50', 'planning for sea level rise'),
          ('DD16-51',
           'How will changes in sea-level rise affect coastal freshwater supply'),
          ('DD16-52', 'albedo feedback future climate change Poles'),
          ('DD16-53', 'climate change polar bears')
                     ]

EBOLA_TOPICS = [('DD16-1', 'US Military Crisis Response'),
          ('DD16-2', 'Ebola Conspiracy Theories'),
          ('DD16-3', 'healthcare impacts of ebola'),
          ('DD16-4', 'Daniel Berehulak'),
          ('DD16-5', 'Ewedu as an Ebola Treatment'),
          ('DD16-6', 'Alleged Alternative Treatments for Ebola'),
          ('DD16-7', 'Urbanisation Urbanization'),
          ('DD16-8', 'Dr. Olivet Buck'),
          ('DD16-9', 'Thomas Eric Duncan'),
          ('DD16-10', 'Economic impact of ebola'),
          ('DD16-11', 'U.S. healthcare workers'),
          ('DD16-12', 'is there a natural immunity to ebola'),
          ('DD16-13', 'Dr. Steven Hatch'),
          ('DD16-14', 'T.B. Joshua'),
          ('DD16-15', 'Maurice Iwu'),
          ('DD16-16', 'Modeling'),
          ('DD16-17', 'Kenema District Government Hospital'),
          ('DD16-18', 'Robots'),
          ('DD16-19', 'Attacks on ebola aid'),
          ('DD16-20', 'Pauline Cafferkey'),
          ('DD16-21', 'Ebola medical waste'),
          ('DD16-22', 'radio school'),
          ('DD16-23', 'Crowdfunding Crowdsourcing'),
          ('DD16-24', 'Olu-Ibukun Koye Spread EVD to Port Harcourt'),
          ('DD16-25', "Emory University's role in Ebola treatment"),
          ('DD16-26', 'Effects of African Culture'),
          ('DD16-27', 'kaci hickox'),
                ]


EBOLA_TOPICS_TEST_TOPICS = [
    # ('DD16-27', 'kaci hickox'),

('DD16-1', 'US Military Crisis Response'),
                ]


POLAR_TOPICS = [
    ('DD16-28', 'Is the distribution of permafrost changing in the Arctic?'),
    ('DD16-29', 'ice sheet sea level rise'),
    ('DD16-30', 'Where are basal boundary conditions in East Antarctica?'),
    ('DD16-31', 'sea level rise change strom surge'),
    ('DD16-32', 'polar oceans freshwater sensitivity'),
    ('DD16-33', 'sea-level rise and coastal erosion'),
    ('DD16-34', 'melting ice sheet ocean circulation'),
    ('DD16-35', 'snow accumulation rate Greenland'),
    ('DD16-36', 'Is the rate of snow accumulation changing in Antarctica?'),
    ('DD16-37', 'west antarctic ice sheet'),
    ('DD16-38', 'Are significant changes occurring in ocean productivity'),
    ('DD16-39',
     'How will shipping be impacted by changes in Arctic sea ice characteristics?'),
    ('DD16-40', 'Polar terrestrial ecosystems CO2 trace gas'),
    ('DD16-41', 'Artic sea ice fishery'),
    ('DD16-42',
     'How will offshore mineral extraction be impacted by changes in Arctic sea ice characteristics?'),
    ('DD16-43', 'Is ice sheet elevation changing'),
    ('DD16-44',
     'Are changes occurring in the distribution and productivity of Arctic vegetation?'),
    ('DD16-45',
     'How will subsistence fishing and hunting be impacted by changes in Arctic sea ice characteristics?'),
    ('DD16-46', 'Are changes occurring the coverage of the Arctic Sea ice'),
    ('DD16-47', 'Arctic sea ice thickness'),
    ('DD16-48', 'polar ocean global ocean circulation'),
    ('DD16-49', 'Are changes occurring in the circulation of the Arctic Sea'),
    ('DD16-50', 'planning for sea level rise'),
    ('DD16-51',
     'How will changes in sea-level rise affect coastal freshwater supply'),
    ('DD16-52', 'albedo feedback future climate change Poles'),
    ('DD16-53', 'climate change polar bears')
]

# EBOLA_TOPICS = [
#     # ('DD16-40', 'Polar terrestrial ecosystems CO2 trace gas'),
#     # ('DD16-47', 'Arctic sea ice thickness'),
# # ('DD16-7', 'Urbanisation/Urbanization '),
# #     ('DD16-2', 'Ebola Conspiracy Theories'),
#
# # ('DD16-25', "Emory University's role in Ebola treatment"),
# # # ('DD16-26', 'Effects of African Culture'),
# #           ('DD16-27', 'kaci hickox'),
# ('DD16-6', 'Alleged Alternative Treatments for Ebola'),
#
# ]

NYT_TOPICS = [('dd17-1', 'Return of Klimt paintings to Maria Altmann'), ('dd17-2', 'Who Outed Valerie Plame?'), ('dd17-3', "First Women's Bobsleigh Debut 2002 Olympics"), ('dd17-4', 'Origins Tribeca Film Festival'), ('dd17-5', "Benazir Bhutto's legal problems"), ('dd17-6', 'Dwarf Planets'), ('dd17-7', 'Warsaw Pact Dissolves'), ('dd17-8', 'Concorde Crash'), ('dd17-9', 'Grenada-Cuba connections'), ('dd17-10', 'Leaning tower of Pisa Repairs'), ('dd17-11', 'Zebra mussel Hudson River'), ('dd17-12', 'Dental implants'), ('dd17-13', 'Albania pyramid scheme VEFA'), ('dd17-14', 'Montserrat eruption effects'), ('dd17-15', 'arik afek yair klein link'), ('dd17-16', 'Eggs actually are good for you'), ('dd17-17', 'Nancy Pelosi election as Speaker of the House'), ('dd17-18', 'Celebration of 50th Anniversary of Golden Gate Bridge'), ('dd17-19', 'Antioxidant food supplements'), ('dd17-20', 'Elizabeth Edwards Cancer'), ('dd17-21', 'Mega Borg Oil Spill'), ('dd17-22', 'Playstation 2 Console Sales and Prices'), ('dd17-23', 'USAF 1st Lt. Flinn discharged'), ('dd17-24', 'Melissa virus effect and monetary costs'), ('dd17-25', 'Last Checker Taxi Cab in NYC Auctioned'), ('dd17-26', 'New Scottish Parliament building'), ('dd17-27', 'Doping for professional sports'), ('dd17-28', 'Russian Organized Crime Involvement in Skating Scandal'), ('dd17-29', 'Chefs at Michelin 3- star Restaurants'), ('dd17-30', 'Nicotine addiction'), ('dd17-31', 'Implantable Heart Pump'), ('dd17-32', 'Million Man March on Washington'), ('dd17-33', 'refugees on nauru'), ('dd17-34', 'Rudolf Hess dies'), ('dd17-35', 'Bedbug infestation rising'), ('dd17-36', 'Global Warming Effect on NYC Region'), ('dd17-37', 'Gander Community Response After 9/11'), ('dd17-38', 'Iceland financial problems'), ('dd17-39', 'Munch Scream Recovered'), ('dd17-40', 'Church of England first female priests ordained'), ('dd17-41', 'Lion King Film'), ('dd17-42', 'Asian tiger mosquito'), ('dd17-43', 'Harry Connick Jr. on Broadway'), ('dd17-44', 'Whitney Museum Expansion to Meatpacking District'), ('dd17-45', 'Exhibitions of George Nakashima Works'), ('dd17-46', 'PGP'), ('dd17-47', 'Freon-12'), ('dd17-48', 'defense, precautions against modern ship piracy'), ('dd17-49', 'kangaroo survival'), ('dd17-50', 'Shrinking ice sheet in Greenland'), ('dd17-51', "Hurricane Katrina's Effects"), ('dd17-52', 'Solar power for U.S. homes'), ('dd17-53', "Alzheimer's and beta amyloid; detection, treatment?"), ('dd17-54', 'Indoor air pollution'), ('dd17-55', 'North Korea says it has nukes'), ('dd17-56', 'Abortion pill in the United States'), ('dd17-57', 'Libyan connection to Muslim coup in Trinidad Tobago'), ('dd17-58', 'cashew growing'), ('dd17-59', "Colonel Denard's mercenary activities"), ('dd17-60', 'Tupac Amaru and Shining Path, relationship, differences, similarities')]


TOT_TOPICS = EBOLA_TOPICS_INIT + NYT_TOPICS
# TOT_TOPICS = [
# ('DD16-1', 'US Military Crisis Response'),
#           # ('DD16-2', 'Ebola Conspiracy Theories'),
#           # ('DD16-3', 'healthcare impacts of ebola'),
# ]

STOPWORDS = [u'i', u'me', u'my', u'myself', u'we', u'our', u'ours', u'ourselves', u'you', u'your', u'yours', u'yourself', u'yourselves', u'he', u'him', u'his', u'himself', u'she', u'her', u'hers', u'herself', u'it', u'its', u'itself', u'they', u'them', u'their', u'theirs', u'themselves', u'what', u'which', u'who', u'whom', u'this', u'that', u'these', u'those', u'am', u'is', u'are', u'was', u'were', u'be', u'been', u'being', u'have', u'has', u'had', u'having', u'do', u'does', u'did', u'doing', u'a', u'an', u'the', u'and', u'but', u'if', u'or', u'because', u'as', u'until', u'while', u'of', u'at', u'by', u'for', u'with', u'about', u'against', u'between', u'into', u'through', u'during', u'before', u'after', u'above', u'below', u'to', u'from', u'up', u'down', u'in', u'out', u'on', u'off', u'over', u'under', u'again', u'further', u'then', u'once', u'here', u'there', u'when', u'where', u'why', u'how', u'all', u'any', u'both', u'each', u'few', u'more', u'most', u'other', u'some', u'such', u'no', u'nor', u'not', u'only', u'own', u'same', u'so', u'than', u'too', u'very', u's', u't', u'can', u'will', u'just', u'don', u'should', u'now', u'd', u'll', u'm', u'o', u're', u've', u'y', u'ain', u'aren', u'couldn', u'didn', u'doesn', u'hadn', u'hasn', u'haven', u'isn', u'ma', u'mightn', u'mustn', u'needn', u'shan', u'shouldn', u'wasn', u'weren', u'won', u'wouldn']

STOPWORDS = [
    w.encode('utf8') for w in STOPWORDS
]


BAD_WORDS = [
    'BidVertiser', 'Sierra', 'click', 'code', 'admin', 'advertising', 'Begin', 'End',
    'Highlight', 'oallowfullscreen', 'webkitallowfullscreen', 'mozallowfullscreen', 'Permalink', 'Galaxy', 'MacBook', 'Lollipop', 'Android', 'Samsung', 'PreOrder',
    'January', 'Astronomers'
]


# Ewedu as an Ebola Treatment pay^0.0154748865906,Island^0.0139631031979,Unit^0.0119249004243,allowfullscreen^0.0105955622192,Clinic^0.00732712672029,OCTOBER^0.00672170323867,Download^0.0066528252439,Flickr^0.00652893659381,hemorrhagic^0.0063851226109,Bing^0.00630827259726

#{|}等符号出现


#subqueries
subquery_dir = "/home/zhangwm/Data/subquerys/"
EBOLA_GOOGLE_RELATED = subquery_dir + "ebola_google_related.json"
EBOLA_GOOGLE_SUGGESTED = subquery_dir + "ebola_google_suggested.json"


#ebola_bing_related.json  ebola_bing_suggested.json  ebola_google_related.json  ebola_google_suggested.json  yandex_suggested.json
EBOLA_BING_RELATED = subquery_dir + "ebola_bing_related.json"
EBOLA_BING_SUGGESTED = subquery_dir + "ebola_bing_suggested.json"
EBOLA_GOOGLE_RELATED = subquery_dir + "ebola_google_related.json"
EBOLA_GOOGLE_SUGGESTED = subquery_dir + "ebola_google_suggested.json"
EBOLA_YANDEX_SUGGESTED = subquery_dir + "yandex_suggested.json"


POLAR_GOOGLE_SUGGESTED = subquery_dir + "google_polar_new.json"

GOOGLE_SUGGESTED = subquery_dir + "google_suggested.json"
GOOGLE_RELATED = subquery_dir + "google_related.json"


TITLE_BING = subquery_dir + "title_related_bing.json"
TITLE_GOOGLE = subquery_dir + "google_ebola.json"

STEM_IDF_DICT_EBOLA = "/home/zhangwm/Data/processed/ebola_stem_idf.json"
STEM_IDF_DICT_POLAR = "/home/zhangwm/Data/processed/polar_stem_idf.json"
STEM_IDF_DICT_EBOLA_CLEAN = "/home/zhangwm/Data/processed/ebola_stem_idf_clean.json"

STEM_IDF_DICT_CLEAN_EBOLA = "/home/zhangwm/Data/processed/ebola_stem_idf_clean.json"
# STEM_IDF_DICT_CLEAN_POLAR = "/home/zhangwm/Data/processed/polar_stem_idf.json"


NEW_NYT_SUGGESTOR = "/home/zhangwm/trec/datas/google_nytimes_all_sgst.json"

#rating..
RATE_0 = 0
RATE_1 = 1
RATE_2 = 2
RATE_3 = 3
RATE_4 = 4
RATES = [
RATE_4, RATE_3, RATE_2, RATE_1,
]


#SUGGESTED QUERY
GOOGLE_SUGGESTED_V1_EBOLA = "/home/zhangwm/trec/datas/google_ebola.sg.json"
GOOGLE_SUGGESTED_V1_NYT = "/home/zhangwm/trec/datas/google_nytimes.sg.json"

GOOGLE_SUGGESTED_EBOLA_WITH_CNT = "/home/zhangwm/trec/datas/filter_suggestion/ebola-merge.json"
GOOGLE_SUGGESTED_NYT_WITH_CNT = "/home/zhangwm/trec/datas/filter_suggestion/nytimes-merge.json"

GOOGLE_SUGGESTED_EBOLA_NGRAM_WITH_CNT = "/home/zhangwm/trec/datas/filter_suggestion/ebola_ngram-merge.json"


'''
/home/zhangwm/trec/datas ebola_rank.json  nytimes_rank.json'''
EBOLA_GOOGLE_RANK_FILE = "/home/zhangwm/trec/datas/ebola_rank.json"
NYT_GOOGLE_RANK_FILE = "/home/zhangwm/trec/datas/nytimes_rank.json"
EBOLA_NYT_GOOGLE_KEY_RANK_FILE = "/home/zhangwm/trec/datas/ebola_nytimes_key_rank.json"

NOT_ON_TOPIC = 'not_on_topic'
