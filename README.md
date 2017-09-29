# TREC2017-DD-ICTNET SOURCE CODE 


## **Data Preparation**
- Extract Data
    - extract\_ebola.py extract\_ny.py
- Search Engine Suggestion
    - se\_suggestion.py

## **Rank algorithm blending**

We use BM25Similarity,  IBSimilarityFactory, LMJelinekMercerSimilarityFactory, DFRSimilarityFactory(basicModel G, afterEffect L, normalization H2), LMDirichlet in solr. 

## **Run Solution**
- ictnet\_div\_qe
    - submission\_xQuAD_rocchio_solution.py， change source_weight in function submission\_xQuAD\_rocchio\_tfidfw\_solution to [0, 1.0]
- ictnet\_emulti
    - submission\_xQuAD\_rocchio\_solution.py， change source\_weight in function submission\_xQuAD\_rocchio\_tfidfw\_solution to [0.1, 0.1]
- ictnet\_fom\_itr1
    - We use our algorithm from the first iteration. 
- ictnet\_params1\_s 
    - submission\_3894change\_params.py, change source\_weight in function submission\_xQuAD\_rocchio\_tfidfw\_solution to [0, 1.0], if\_use\_stop\_stop\_strategy is True, every\_expand\_words\_cnt 6
 - ictnet\_params2\_ns 
    - same with ictnet\_params1\_s, but if\_use\_stop\_stop\_strategy is False



*This repository is the submission code for TREC 2017 DD*

