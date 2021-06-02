
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


def find_keywords(df, top_n=100):
    logging.info('Finding keywords')
    nlp = spacy.blank('id')
    brief_cleaning = [re.sub("[^A-Za-z']+", ' ', str(title)).lower()
                      for title in df.title.values]
    text = [cleaning_title(doc) for doc in tqdm(
        nlp.pipe(brief_cleaning, batch_size=5000, n_process=-1))]

    titles = [title.split() for title in text if title is not None]
    words = np.array([word for title in tqdm(titles)
                     for word in title], dtype=object)
    counter = Counter(words)
    return counter.most_common(top_n)
