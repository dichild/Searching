__author__ = 'userme865'
import urllib

import p01.stemmer.api as nlp
import nltk

porter=nltk.PorterStemmer()
from bs4 import BeautifulSoup


def del_tag(tag, text):
    num = len(text.find_all(tag))
    for n in range(num):
        cmd = 'text' + '.' + tag + '.' + 'decompose()'
        exec (cmd)


def dedupe(items): #Removing Duplicates from a Sequence while Maintaining Order
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


def despec(complist, delist): #Delete the specific words
    for i in delist:
        try:
            complist.remove(i)
        except:
            continue

def pasrsing(raw):
    markup = BeautifulSoup(raw)
    del_tag('script', markup)
    del_tag('pre', markup)
    del_tag('style', markup)
    words = []
    for text in markup.stripped_strings:
        for uword in text.split():
            words.append(uword)
    text = ' '.join(words)

    locale = nlp.guessLocale(text)
    # text = text.translate(None,',-:()|;\'./')
    # text = list(dedupe(text.split(' ')))
    stopwords = nlp.getStopWords(locale)
    # despec(text,stopwords)  # Here there are examples 'and','or'
    text = nlp.removeNumbers(text)
    token = nlp.doTokenize(text, stopwords)
    # Lemmatization  = nltk.WordNetLemmatizer()
    # lem = [Lemmatization.lemmatize(t) for t in token]
    # print lem
    stem = [porter.stem(t) for t in token]
    return stem


