import re
import time
import pickle
import pandas as pd
<<<<<<< HEAD
from typing import NamedTuple
=======
>>>>>>> a24168a94adb123d968668ebf39fb2dc64ebddd4
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict

class Document(NamedTuple):
    tweet_id: str
    is_benchmark: bool
    tweet_tokens: list

class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.documents = []
        #self.dictionary = defaultdict(set)
        #self.tweets_words_locations = defaultdict(lambda: (str, Counter()))
        self.dictionary = defaultdict(set)
        self.tweets_words_locations = dict()
        self.capitals_counter = Counter()
        self.words_dual_representation = []
        self.words_capital_representation = []
        self.seen_capital = set()

    def parse_sentence(self, text, do_stem: bool):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        """
        text_tokens = self.number_tokenizer(text)  # parse percent
        if "percent" in text_tokens or "percentage" in text_tokens:
            text_tokens = self.percentage_tokenizer(text_tokens)  # parse numbers

        ans = ""
        string = ""
        for w in text_tokens.split():
            ans = self.remove_single_chars(w)
            if "http" in w or "https" in w or "www" in w:
                ans = self.url_tokenizer(ans)
            elif "-" in ans or "/" in ans or "&" in ans:
                ans = self.hyphen_fixer(ans)
            elif "#" in ans or "_" in ans:  # parse hashtags
                ans = self.hash_tag_tokenizer(ans)


            string = string + " " + ans

        text_tokens = word_tokenize(string)  # tokenization

        # if stemming is necessary
        if do_stem:
            text_tokens = self.stemmer(text_tokens)

        text_tokens_without_stopwords = []#[w for w in text_tokens if w.lower() not in self.stop_words]
        for w in text_tokens:
            if w not in self.stop_words:
                text_tokens_without_stopwords.append(w)
                if w[0].isupper():
                    self.seen_capital.add(w)

        self.capitals_counter.update(text_tokens_without_stopwords)
        print(text_tokens_without_stopwords)
        return text_tokens_without_stopwords

    def parse_doc(self, doc_as_named_tuple: tuple, do_stem: bool = False):
        """
        This function get tweet data than send the tweet text to parsing and saves the tokens in two data struct.
        the data struct are the dictionary (term: {tweets_ids}), and the tweets indexer (tweet_id: {term:occ})
        """
        # split the data attributes
        tweet_id = doc_as_named_tuple.tweet_id
        full_text = doc_as_named_tuple.full_text
        is_benchmark = doc_as_named_tuple.is_benchmark

        # parse the tweet
        tokenized_text = self.parse_sentence(full_text, do_stem)

        document = Document(
            tweet_id = tweet_id,
            is_benchmark = is_benchmark,
            tweet_tokens = tokenized_text
        )

        self.documents.append(document)

        # # add words to dict
        # for term in tokenized_text:
        #         self.dictionary[term].add(tweet_id)
        #         self.tweets_words_locations[tweet_id][1].update(term)
        #
        # self.tweets_words_locations[tweet_id][0] = 'benchmark' if is_benchmark else 'not_benchmark'

    def parse_doc(self, doc_as_named_tuple, do_stem: bool = False):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_named_tuple.tweet_id
        full_text = doc_as_named_tuple.full_text
        tokenized_text = self.parse_sentence(full_text, do_stem)

        # the following dict will hold the words locations for a specific tweet
        tweet_words_locations = defaultdict(list)

        # add words to dict
        for location, term in enumerate(tokenized_text):
                self.dictionary[term].add(tweet_id)
                tweet_words_locations[term].append(location)

        # keep tweet words locations
        self.tweets_words_locations[tweet_id] = tweet_words_locations



    def parse_batch_of_docs(self, df: pd.DataFrame):
        """
        :param df:
        :return:
        """
        # parse each tweet and insert result to a document
        for row in df.itertuples():
            self.parse_doc(row)


    def parse_corpus(self, dfs: list):
        """
        :param df:
        :return:
        """
        while dfs:
            df = dfs.pop()
            print(f"batch size to parse: {df.shape[0]} {time.ctime()}")
            self.parse_batch_of_docs(df)
            print(f'finish parse batch {time.ctime()}')

        # fetch words with capital letter
        print('tokens seen with capital', len(self.seen_capital))
        print('total number of tokens seen', len(self.capitals_counter))
        self.words_dual_representation = set([word for word in self.seen_capital if word.lower() in self.capitals_counter.keys()])
        self.words_capital_representation = self.seen_capital-self.words_dual_representation

        # save words counter as pickle
        with open('words_counter.pickle', 'wb') as handle:
            pickle.dump(self.capitals_counter, handle, protocol=pickle.HIGHEST_PROTOCOL)
        del self.capitals_counter
        print('capital councapitals_counterter as been deleted')

        # change words to all capital
        for capital in self.words_capital_representation:
            self.dictionary[capital.upper()] = self.dictionary.pop(capital)

        # change words to all lower
        for capital in self.words_dual_representation:
            self.dictionary[capital.lower()].union(self.dictionary.pop(capital))


    def hash_tag_tokenizer(self, word: str) -> str:
        string = word
        word = word[1:]
        if "_" in word:
            split_by_underscore = " ".join(word.split("_"))
            string = string + " " + split_by_underscore
            return string
        else:
            split_by_caps = " ".join([a for a in re.split('([A-Z][a-z]+)', word) if a])
            string = string + " " + split_by_caps
            return string

        return word


    def url_tokenizer(self, w: str) -> str:
        string = ""
        url = []
        # if len(w) < 2:
        #     continue
        url = (re.split(r"\W+", w))
        url_to_string = ' '.join(url)
        string = url_to_string

        return string


    def stemmer(self, tokens: str) -> str:
        ps = PorterStemmer()
        string = ""
        for word in tokens.split():
            string = string + ps.stem(word) + " "

        return string


    def percentage_tokenizer(self, tokens: str) -> str:
        string = ""
        ans = False
        for w in tokens.split():
            if ans:
                if w == "percent" or w == "percentage":
                    string = string + "%" + " "
                    ans = False
                    continue
                else:
                    string = string + " "
            try:
                if float(w):
                    string = string + w
                    ans = True
                    continue
            except ValueError:
                string = string + w + " "

        return string


    def number_tokenizer(self, tokens: str) -> str:
        string = ""
        kmb = ""
        number = False
        for w in tokens.split():
            if w == "RT":
                continue
            if number:
                if w == "Thousand":
                    kmb = kmb + "K"
                    if kmb == "KK":
                        string = string[:-1] + "M"
                        kmb = ""
                        continue
                    elif kmb == "MK" or kmb == "KM":
                        string = string[:-1] + "B"
                        kmb = ""
                        continue
                    else:
                        string = string + "K"
                        continue
                elif w == "Million":
                    kmb = kmb + "M"
                    if kmb == "MK" or kmb == "KM":
                        string = string[:-1] + "B"
                        kmb = ""
                        continue
                    else:
                        string = string + "M"
                        continue
                elif w == "Billion":
                    string = string + "B"
                    continue
                else:
                    string = string + " "
                    number = False
            kmb = ""
            try:
                if float(w):
                    num = float(w)
                    if num < 1000:
                        number = True
                        string = string + w
                        continue
                    elif num < 1000000:
                        num = num / 1000
                        num = round(num, 3)
                        num = str(num)
                        if num.endswith(".0"):
                            num = num.replace(".0", "")
                        string = string + num + "K"
                        kmb = kmb + "K"
                        number = True
                        continue
                    elif num < 1000000000.00:
                        num = num / 1000000
                        num = round(num, 3)
                        num = str(num)
                        if num.endswith(".0"):
                            num = num.replace(".0", "")
                        string = string + num + "M"
                        kmb = kmb + "M"
                        number = True
                        continue
                    elif num >= 1000000000:
                        num = num / 1000000000.000
                        num = round(num, 3)
                        num = str(num)
                        if num.endswith(".0"):
                            num = num.replace(".0", "")
                        string = string + num + "B"
                        number = True
                        continue
            except:
                string = string + w + " "

        return string


    def remove_single_chars(self, w: str) -> str:
        string = ""
        w = re.sub(r'[^a-zA-Z0-9\s&@#/._-]', '', w)
        if "." in w:
            try:
                if float(w):
                    []
            except:
                w = w.replace(".", "")
        if len(w) > 1 or w.isdigit():
            string = w

        return string


    def hyphen_fixer(self, w: str) -> str:
        string = ""
        if "-" in w:
            # dual_string = w
            string = " ".join(w.split("-")) + " "
        elif "/" in w:
            # dual_string = w
            string = " ".join(w.split("/")) + " "
        elif "&" in w:
            # dual_string = w
            string = " ".join(w.split("&")) + " "
        else:
            string = w
        return string
