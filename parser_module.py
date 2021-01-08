import re
import time
import pickle
import pandas as pd
from typing import NamedTuple
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from document import Document
from nltk.tokenize import word_tokenize
from collections import Counter, defaultdict

class Parse:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.documents = []
        self.capitals_counter = Counter()
        self.words_dual_representation = []
        self.words_capital_representation = []
        self.seen_capital = set()

    def parse_sentence(self, text, do_stem: bool = False):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        """
        text_tokens = self.number_tokenizer(text)
        if "percent" in text_tokens or "percentage" in text_tokens:
            text_tokens = self.percentage_tokenizer(text_tokens)  # parse numbers

        ans = ""
        string = ""
        for w in text_tokens.split():
            ans = self.remove_single_chars(w)
            if "http" in w or "www" in w:
                ans = self.url_tokenizer(ans)
            elif "-" in ans or "/" in ans or "&" in ans:
                ans = self.hyphen_fixer(ans)
            elif "#" in ans or "_" in ans:
                ans = self.hash_tag_tokenizer(ans)

            string = string + " " + ans

        text_tokens = word_tokenize(string)

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

        #added this return statement
        return document



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

        self.words_dual_representation = set([word for word in self.seen_capital if word.lower() in self.capitals_counter.keys()])
        self.words_capital_representation = self.seen_capital-self.words_dual_representation



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
        if w.endswith('s') or w.endswith('S'):
            w = w[:-1]
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
