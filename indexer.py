import pickle
from collections import Counter, defaultdict

# DO NOT MODIFY CLASS NAME
class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.dictionary = defaultdict(set)
        self.indexer = defaultdict(lambda: [str, Counter()])
        self.config = config

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document, is_benchmark: bool = False):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        # Go over each term in the doc
        for term in document.tweet_tokens:
            try:
                self.dictionary[term].add(document.tweet_id)
                self.indexer[document.tweet_id][1].update(term)
            except:
                print('problem with the following key {}'.format(term))

        self.indexer[document.tweet_id][0] = 'benchmark' if is_benchmark else 'not_benchmark'


    def initialize_indexer(self, documents: list, words_capital_representation: dict, words_dual_representation: dict):
        """
        :param documents:
        :return:
        """
        for document in documents:
            # add words to dictionary
            for term in document.tweet_tokens:
                    self.dictionary[term].add(document.tweet_id)
                    #CHANGE
                    self.indexer[document.tweet_id][1].update({term: 1})

            self.indexer[document.tweet_id][0] = 'benchmark' if document.is_benchmark else 'not_benchmark'

        # upper for words which appeared with capital letter only
        for capital in words_capital_representation:
            self.dictionary[capital.upper()] = self.dictionary.pop(capital)

        # lower for words which appeared with both capital and lower case letter
        for capital in words_dual_representation:
            self.dictionary[capital.lower()].union(self.dictionary.pop(capital))

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        with open('filename', 'rb') as f:
            indexer = pickle.load(fn)
            self.indexer = indexer

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        with open(fn, 'wb') as f:
            pickle.dump(self.indexer, f)

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.dictionary

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []

    def save_index_benchmark(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        benchmark_indexer = {key: value for key, value in self.indexer.items() if value[0] == 'benchmark'}
        with open('idx_bench.pickle', 'wb') as f:
            pickle.dump(benchmark_indexer, f)