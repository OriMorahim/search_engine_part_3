# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math
from collections import Counter
from typing import Dict, Tuple, Set
class Ranker:
    def __init__(self):
        pass

    # @staticmethod
    # def rank_relevant_docs(relevant_docs, k=None):
    #     """
    #     This function provides rank for each relevant document and sorts them by their scores.
    #     The current score considers solely the number of terms shared by the tweet (full_text) and query.
    #     :param k: number of most relevant docs to return, default to everything.
    #     :param relevant_docs: dictionary of documents that contains at least one term from the query.
    #     :return: sorted list of documents by score
    #     """
    #     ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
    #     if k is not None:
    #         ranked_results = ranked_results[:k]
    #     return [d[0] for d in ranked_results]

    @staticmethod
    def rank_relevant_docs(docs: list,terms_doc_freq: Dict[str,int],query_as_list: list, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """

        results = {}
        N = len(indexer) * 2
        q = len(relevant_tweets)
        for location, doc in indexer:
            sim = 0
            cosin_sim = 0
            denominator = 0
            max_count = max(doc, key=lambda item: item[1])[1]
            for term in doc:
                word = term[0].lower()
                tf = term[1]
                df_ = terms_doc_freq[word]
                tf = tf / max_count
                idf = math.log(N / df_, 2)
                if word in relevant_tweets:
                    sim = sim + tf * idf
                denominator = denominator + math.pow(tf * idf, 2)
            if denominator == 0:
                cosin_sim = 0
            else:
                cosin_sim = sim / (math.sqrt(q * denominator))
            results[location] = cosin_sim
        results = sorted(results.items(), key=lambda x: x[1], reverse=True)

        return results

# from reader import ReadFile
# reader = ReadFile('C:/Users/Jonathan Grinshpan/Documents/information_Retrieval/Data/Data','C:/Users/Jonathan Grinshpan/Desktop/benchmark_data_train.snappy.parquet')
# dfs = reader.read_all()
# from parser_module import Parse
# parser = Parse()
# docs = parser.parse_corpus(dfs)
# from indexer import Indexer
# index = Indexer('')
# indx = Indexer.initialize_indexer(index,parser.documents,parser.words_capital_representation,parser.words_dual_representation)
#from searcher import Searcher
#search = Searcher(parser,index.dictionary)
#a = search.search('year')
#from ranker import Ranker
#rank = Ranker()
#dict = {"a": 1, "b" :2, "c" :0}
#a = rank.rank_relevant_docs(index,['1280940944263544834', '1280921542243659776'],dict)
