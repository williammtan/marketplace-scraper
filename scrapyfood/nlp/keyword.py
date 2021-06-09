
from nlp.lemmatizer import LOOKUP
from nlp.noise_words import noise_words
from signal import signal, SIGPIPE, SIG_DFL
from tqdm import tqdm
from collections import Counter
import numpy as np
import spacy
import re
import logging

signal(SIGPIPE, SIG_DFL)


def cleaning_title(doc):
    text = [token.text if token not in LOOKUP.items()
            else LOOKUP[token]
            for token in doc
            if not token.is_stop
            and token.text not in noise_words
            and len(token.text) > 2
            ]
    if len(text) > 2:
        return ' '.join(text)


def find_keywords(df, top_n=20, n_common=20, threshold=100):

    logging.info('Finding keywords')
    nlp = spacy.blank('id')
    brief_cleaning = [re.sub("[^A-Za-z']+", ' ', str(title)).lower()
                      for title in df.name.values]
    text = [cleaning_title(doc) for doc in tqdm(
        nlp.pipe(brief_cleaning, batch_size=5000, n_process=-1), total=len(brief_cleaning))]

    titles = np.array([title.split()
                      for title in text if title is not None], dtype=object)
    words = np.array([word for title in tqdm(titles)
                     for word in title], dtype=object)
    counter = Counter(words)
    keywords = counter.most_common(top_n)

    search_keywords = []

    for k, id in keywords:
        # find prods which contain the keyword and find second most common
        contains_k = titles[np.array([k in name for name in titles])]
        words = [word for name in contains_k for word in name]
        k_counter = Counter(words)
        most_common = k_counter.most_common(n_common)
        for key in most_common:
            if k != key[0] and key[1] > threshold:
                search_keywords.append(k + ' ' + key[0])

    return search_keywords
