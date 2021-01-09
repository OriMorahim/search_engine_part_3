# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math
from collections import Counter
from typing import Dict, Tuple, Set
class Ranker:
    def _init_(self):
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
    def rank_relevant_docs(docs: list, terms_doc_freq: Dict[str,int], query_as_list: list, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """

        results = {}
        N = len(docs) * 2
        q = len(query_as_list)
        for location, doc in docs:
            try:
                #print(len(doc))
                sim = 0
                cosin_sim = 0
                denominator = 0
                max_word = max(doc)
                max_count = doc[max_word]

                for term in doc:
                    #word_lower = term.lower()
                    #word_upper = term.upper()
                    tf = doc[term]
                    if (term.lower() in query_as_list) | (term.upper() in query_as_list) in query_as_list: #or word_upper in query_as_list:
                        df_ = terms_doc_freq[term]
                    else:
                        df_ = 1
                    tf = tf / max_count
                    idf = math.log(N / df_, 2)
                    if term in query_as_list:# or word_upper in query_as_list:
                        sim = sim + tf * idf
                    denominator = denominator + math.pow(tf * idf, 2)
                if denominator == 0:
                    cosin_sim = 0
                else:
                    cosin_sim = sim / (math.sqrt(denominator*q))
                results[location] = cosin_sim
            except:
                continue
        results = sorted(results.keys(), key=lambda x: x[1], reverse=True)

        return results