import os
import glob
import pandas as pd

RELEVANT_COLUMS = ["tweet_id", "full_text"]

class ReadFile:
    def __init__(self, corpus_path: str, benchmark_path: str):
        self.corpus_path = corpus_path
        self.benchmark_path = benchmark_path

    def read_and_concat_all_parquet_in_dir(self):
        """
        This method used to read all the parquet files in a directory. The directory
        we fetch the files from is corpus_path
        :return:
        """
        corpus_files = glob.glob(f"{self.corpus_path}/*.parquet")

        dfs = []
        for file in corpus_files:
            temp_df = pd.read_parquet(file)
            temp_df['is_benchmark'] = False
            dfs.append(temp_df)

        return pd.concat(dfs, axis=0)


    def read_all(self, max_files=1):
        """
        This method used to read all parquet files from a directory of directories. The directory
        we fetch the files from is corpus_path
        :return:
        """
        dfs = []
        counter = 0
        for dir in os.listdir(self.corpus_path):
            files = glob.glob(f"{self.corpus_path}/{dir}/*.parquet")
            for file in files:
                temp_df = pd.read_parquet(file, columns=RELEVANT_COLUMS)
                temp_df_no_dup = temp_df.groupby('full_text')['tweet_id'].first().reset_index()
                #CHANGE
                temp_df_no_dup['is_benchmark'] = False
                dfs.append(temp_df_no_dup)
                counter += 1
                if counter >= max_files:
                    break
            if counter >= max_files:
                break

        benchmark_df = pd.read_parquet(self.benchmark_path)
        benchmark_df['is_benchmark'] = True
        dfs.append(benchmark_df)

        return dfs
# from reader import ReadFile
# reader = ReadFile('C:/Users/Jonathan Grinshpan/Documents/information_Retrieval/Data/Data','C:/Users/Jonathan Grinshpan/Desktop/benchmark_data_train.snappy.parquet')
# dfs = reader.read_all()
# from parser_module import Parse
# parser = Parse()
#docs = parser.parse_corpus(dfs)
#from indexer import Indexer
#index = Indexer('')
#indx = Indexer.initialize_indexer(index,parser.documents,parser.words_capital_representation,parser.words_dual_representation)
#from search_engine_best import SearchEngine
#searchengine = SearchEngine()
#from searcher import Searcher
#search = Searcher(parser,index)
#a = search.search('mask')
