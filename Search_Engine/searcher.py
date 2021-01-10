from ranker import Ranker
#import utils


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        # parse query
        query_as_list = self._parser.parse_sentence(query)

        # query_as_list = query_expantion(query_as_list)

        # if query contain tokens after parsing, find the the docs that contains the query tokens
        if len(query_as_list) > 0:
            query_as_list = [word.lower() for word in query_as_list] + [word.upper() for word in query_as_list]
            relevant_docs, terms_doc_freq = self._relevant_docs_from_posting(query_as_list)
            n_relevant = len(relevant_docs)
            docs = [(tweet_id, self._indexer.indexer[tweet_id][1]) for tweet_id in relevant_docs]
        else:
            print(f'No relevant docs were found for this query:\n{query}')
            return

        # if there are docs that contain the query tokens then rank the docs by their similarities
        if len(docs) > 0:
            ranked_doc_ids = Ranker.rank_relevant_docs(docs, terms_doc_freq, query_as_list)
            if k:
                ranked_doc_ids = ranked_doc_ids[:k]
        else:
            print(f'No relevant docs were found for this query:\n{query}')
            ranked_doc_ids = set()

        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = set()
        terms_doc_freq = dict()

        for term in query_as_list:

            if term in self._indexer.dictionary.keys():
                related_tweets = self._indexer.dictionary[term]
                terms_doc_freq[term] = len(related_tweets)
                relevant_docs = relevant_docs.union(related_tweets)

        return relevant_docs, terms_doc_freq