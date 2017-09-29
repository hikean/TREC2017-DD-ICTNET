# TREC2017-DD-ICTNET SOURCE CODE 


-  *Data Preparation*


- *Rank algorithm blending*
    We use BM25Similarity,  IBSimilarityFactory, LMJelinekMercerSimilarityFactory, DFRSimilarityFactory(basicModel G, afterEffect L, normalization H2), LMDirichlet in solr. 

- *Run Solution*
  - ictnet_div_qe
submission_xQuAD_rocchio_solution.py， change source_weight in function submission_xQuAD_rocchio_tfidfw_solution to [0, 1.0]
  - ictnet_emulti
submission_xQuAD_ricchio_tc_solution.py
  - ictnet_fom_itr1
Only one aspect differient from (2), we use our algorithm from the first iteration. 





This repository is the submission code for TREC 2017 DD

