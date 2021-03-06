import pandas as pd
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher

import document
#import utils

config = ConfigClass()

# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None

    def gen_search_objects(self, config=config):
        """

        :param config:
        :return:
        """

        reader = ReadFile(config.corpusPath,
                           config.benchmarkPath
        )
        dfs = reader.read_all(1)
        parser = Parse()
        parser.parse_corpus(dfs)
        index = Indexer(config)
        index.initialize_indexer(parser.documents,
                                 parser.words_capital_representation,
                                 parser.words_dual_representation
        )
        self._indexer = index

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        df['is_benchmark'] = False

        # iterate over every document in the file
        for row in df.itertuples():
            # parse the document
            doc = self._parser.parse_doc(row)
            # index the document data
            self._indexer.add_new_doc(doc)

        # find words with capital status
        self._parser.words_dual_representation = set([word for word in self._parser.seen_capital if word.lower() in self._parser.capitals_counter.keys()])
        self._parser.words_capital_representation = self._parser.seen_capital-self._parser.words_dual_representation

        # upper for words which appeared with capital letter only
        for capital in self._parser.words_capital_representation:
            if capital.upper() not in self._indexer.dictionary.keys():
                self._indexer.dictionary[capital.upper()] = self._indexer.dictionary.pop(capital)
            else:
                self._indexer.dictionary[capital.upper()].union(self._indexer.dictionary.pop(capital))

        # lower for words which appeared with both capital and lower case letter
        for capital in self._parser.words_dual_representation:
            self._indexer.dictionary[capital.lower()].union(self._indexer.dictionary.pop(capital))

        print('Finished parsing and indexing.')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and 
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k:int=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.search(query,k)
