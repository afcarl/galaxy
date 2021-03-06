"""
Vectorize
==============

Handles vectorizing of documents.
"""

import os, pickle
import string

from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

from . import conf, pipe

class Tokenizer():
    """
    Custom tokenizer for vectorization.
    Uses Lemmatization.
    """
    def __init__(self):
        self.lemmr = WordNetLemmatizer()
    def __call__(self, doc):
        return tokenize(doc, lemmr=self.lemmr)


PIPELINE = None

def train(docs):
    """
    Trains and serializes (pickles) a vectorizing pipeline
    based on training data.

    `min_df` is set to filter out extremely rare words,
    since we don't want those to dominate the distance metric.

    `max_df` is set to filter out extremely common words,
    since they don't convey much information.
    """
    pipeline = Pipeline([
        ('vectorizer', CountVectorizer(input='content', stop_words='english', lowercase=True, tokenizer=Tokenizer(), min_df=0.015, max_df=0.9)),
        ('tfidf', TfidfTransformer(norm=None, use_idf=True, smooth_idf=True)),
        ('feature_reducer', TruncatedSVD(n_components=100)),
        ('normalizer', Normalizer(copy=False))
    ])

    print('Training on {0} docs...'.format(len(docs)))
    pipeline.fit(docs)

    pipe.save_pipeline(pipeline, 'bow')
    print('Training complete.')

def tokenize(doc, **kwargs):
    """
    Tokenizes a document, using a lemmatizer.

    Args:
        | doc (str)                 -- the text document to process.

    Returns:
        | list                      -- the list of tokens.
    """

    tokens = []
    lemmr = kwargs.get('lemmr', WordNetLemmatizer())
    stops = set(list(string.punctuation) + stopwords.words('english'))

    # Tokenize
    for sentence in sent_tokenize(doc):
        for token in word_tokenize(sentence):

            # Ignore punctuation and stopwords
            if token in stops:
                continue

            # Lemmatize
            lemma = lemmr.lemmatize(token.lower())
            tokens.append(lemma)
    return tokens

def vectorize(docs):
    """
    Vectorizes a list of documents using
    a trained vectorizing pipeline.

    Args:
        | docs (list)       -- the documents to vectorize.
        | docs (str)        -- a single document to vectorize.

    Returns:
        | scipy sparse matrix (CSR/Compressed Sparse Row format)
    """
    global PIPELINE
    if not PIPELINE:
        PIPELINE = pipe.load_pipeline('bow')

    if type(docs) is str:
        # Extract and return the vector for the single document.
        return PIPELINE.transform([docs])[0]
    else:
        return PIPELINE.transform(docs)
