import pandas as pd
from functools import reduce
from search_engine_3 import SearchEngine

queries = {
    1: "Dr. Anthony Fauci wrote in a 2005 paper published in Virology Journal that hydroxychloroquine was effective in treating SARS",
    2: "The seasonal flu kills more people every year in the U.S. than COVID-19 has to date",
    4: "The coronavirus pandemic is a cover for a plan to implant trackable microchips and that the Microsoft co-founder Bill Gates is behind it",
    7: "Herd immunity has been reached",
    8: "Children are almost immune from this disease"
}


def get_engine_results(queries: dict, benchmark_data: pd.DataFrame, search_engine: SearchEngine):
    """
    This function return the search results for queries deliveried in the dict
    :return:
    """
    benchmark_data.tweet = benchmark_data.tweet.astype(object)
    benchmark_data.tweet = benchmark_data.tweet.apply(str)
    benchmark_dict_of_dfs = {query: data for query, data in benchmark_data.groupby('query')}

    num_of_relevant = {query: df.y_true.sum() for query, df in benchmark_dict_of_dfs.items() if query in queries.keys()}

    engine_results = []
    for query_ind, query in queries.items():
        n_relevant, ranked_doc_ids = search_engine.search(query)
        temp_query_true = benchmark_dict_of_dfs[query_ind]
        temp_query_results_df = pd.DataFrame([(tweet_id, 1) for tweet_id in ranked_doc_ids],
                                                 columns=['tweet', 'pred'])

        temp_query_true = temp_query_true.merge(temp_query_results_df, on='tweet', how='inner')
        engine_results.append(temp_query_true)

    return pd.concat(engine_results, axis=0), num_of_relevant


# precision(df, True, 1) == 0.5
# precision(df, False, None) == 0.5
def precision(df, single=False, query_number=None):
    """
        This function will calculate the precision of a given query or of the entire DataFrame
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param single: Boolean: True/False that tell if the function will run on a single query or the entire df
        :param query_number: Integer/None that tell on what query_number to evaluate precision or None for the entire DataFrame
        :return: Double - The precision
    """
    if single:
        df2 = df[df['query'] == query_number]
        return df2['y_true'].mean()
    else:
        return df.groupby('query')['y_true'].mean().mean()


def recall_single(df, num_of_relevant, query_number):
    """
        This function will calculate the recall of a specific query or of the entire DataFrame
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param num_of_relevant: Integer: number of relevant tweets
        :param query_number: Integer/None that tell on what query_number to evaluate precision or None for the entire DataFrame
        :return: Double - The recall
    """
    df2 = df[df['query'] == query_number]
    return df2['y_true'].sum() / num_of_relevant


# recall(df, {1:2}, True) == 0.5
# recall(df, {1:2, 2:3, 3:1}, False) == 0.388
def recall(df, num_of_relevant):
    """
        This function will calculate the recall of a specific query or of the entire DataFrame
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param num_of_relevant: Dictionary: number of relevant tweets for each query number. keys are the query number and values are the number of relevant.
        :return: Double - The recall
    """
    rec = 0
    for query_number in num_of_relevant.keys():
        relevant = num_of_relevant.get(query_number)
        rec += recall_single(df, relevant, query_number)
    return rec / len(num_of_relevant)


# precision_at_n(df, 1, 2) == 0.5
# precision_at_n(df, 3, 1) == 0
def precision_at_n(df, query_number=1, n=5):
    """
        This function will calculate the precision of the first n files in a given query.
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :param query_number: Integer that tell on what query_number to evaluate precision
        :param n: Total document to splice from the df
        :return: Double: The precision of those n documents
    """
    return precision(df[df['query'] == query_number][:n], True, query_number)


# map(df) == 2/3
def map(df):
    """
        This function will calculate the mean precision of all the df.
        :param df: DataFrame: Contains tweet ids, their scores, ranks and relevance
        :return: Double: the average precision of the df
    """
    acc = 0
    split_df = [pd.DataFrame(y).reset_index() for x, y in df.groupby('query', as_index=True)]
    indices = [sdf.index[sdf['y_true'] == 1].tolist() for sdf in split_df]
    query_ids = df['query'].unique().tolist()
    for i, indexes in enumerate(indices):
        pres = [precision_at_n(split_df[i], query_ids[i], index + 1) for index in indexes]
        acc += reduce(lambda a, b: a + b, pres) / len(indexes) if len(pres) > 0 else 0

    return acc / len(split_df)


# from metrics import *
# a=pd.read_csv('C:/Users/orimo/Downloads/benchmark_lbls_train.csv')
# b = SearchEngine()
# b.load_index('idx_bench.pkl')
# df, num_of_relevant = get_engine_results(queries, a, b)


# from metrics import *
# a= pd.read_csv('C:/Users/Jonathan Grinshpan/Desktop/benchmark_lbls_train.csv')
# b = SearchEngine()
# b.load_index('idx_bench.pkl')
# df, num_of_relevant = get_engine_results(queries, a, b)