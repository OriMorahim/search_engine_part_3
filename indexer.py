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
                self.indexer[document.tweet_id][1].update({term: 1})
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
        # read the search engnine objects
        with open(fn, 'rb') as f:
            search_object = pickle.load(f)
        self.dictionary = search_object['dictionary']
        temp_indexer = search_object['indexer']

        # change indexer format
        adjusted_indexer = defaultdict(lambda: [str, Counter])
        for key, value in temp_indexer.items():
            adjusted_indexer[key] = value

        self.indexer = adjusted_indexer


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        index_dict = dict(self.indexer)
        search_object = {'dictionary': self.dictionary, 'indexer': index_dict}
        with open(fn, 'wb') as f:
            pickle.dump(search_object, f)


    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.dictionary


    # # feel free to change the signature and/or implementation of this function
    # # or drop altogether.
    # def get_term_posting_list(self, term):
    #     """
    #     Return the posting list from the index for a term.
    #     """
    #     return self.postingDict[term] if self._is_term_exist(term) else []


    def save_index_benchmark(self, fn:str = 'idx_bench.pickle'):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        benchmark_indexer = {key: value for key, value in self.indexer.items() if value[0] == 'benchmark'}
        search_object = {'dictionary': self.dictionary, 'indexer': benchmark_indexer}
        with open(fn, 'wb') as f:
            pickle.dump(search_object, f)

    def gen_svd_objects(self, n_tokens: int = 500, n_ids: int = 15000):
        """

        :return:
        """
        dictionary = self.dictionary
        sub_dict = list(dictionary.items())[:n_tokens]
        doc_dummy = pd.DataFrame(None)

        index = []
        docs_while_run = set()
        for term, docs in sub_dict:

            if doc_dummy.shape[1] <= n_ids:

                row = {doc_id: 1 for doc_id in docs}
                doc_dummy = doc_dummy.append(row, ignore_index=True)
                docs_while_run = docs_while_run.union(set(doc_dummy.columns))
                index.append(term)

            else:
                row = {doc_id: 1 for doc_id in docs if doc_id in docs_while_run}

                if len(row) > 0:
                    doc_dummy = doc_dummy.append(row, ignore_index=True)
                    index.append(term)

        doc_dummy.index = index

        doc_dummy = doc_dummy.fillna(0)
        terms_to_rm = doc_dummy.index[doc_dummy.sum(axis=1) < 5]

        return doc_dummy.drop(terms_to_rm)
