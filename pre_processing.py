import json
from collections import Counter


STOPWORDS = set(json.load(open("./resources/stop_words.json", "r"))["english"])

class TextProcessor:

    def __init__(self):
        self.text = "This is sample text."
    
    def __init__(self, text_path):
        with open(text_path) as file:
            self.text = file.read()

    def chop_gutenberg_metadata(self):
        if "*** START OF THIS PROJECT GUTENBERG EBOOK" in self.text:
            self.text = self.text.split("*** START OF THIS PROJECT GUTENBERG EBOOK")[1]
        if "*** END OF THIS PROJECT GUTENBERG EBOOK" in self.text:
            self.text = self.text.split("*** END OF THIS PROJECT GUTENBERG EBOOK")[0]

    def clean_up_text(self):
        self.text = self.text.replace("\n", " ")
        self.text = self.text.translate(
            {ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_'\"+\u2018\u2019\u201c\u201d"})
    
    def create_unigrams(self):
        self.unigrams = self.text.split()
        self.unigrams = [w if w.istitle() else w.lower() for w in self.unigrams if w.lower() not in STOPWORDS and len(w)>1]

    def merge_words(self, w1, w2, raw_frequencies):
        if raw_frequencies[w1] >= raw_frequencies[w2]:
            self.frequencies[w1] = raw_frequencies[w1] + raw_frequencies[w2]
        else:
            self.frequencies[w2] = raw_frequencies[w1] + raw_frequencies[w2]

    def compute_frequencies(self):
        raw_frequencies = dict(Counter(self.unigrams))
        self.frequencies = {}
        for w in raw_frequencies:
            if w.islower():
                if w.title() in raw_frequencies:
                    self.merge_words(w.title(), w, raw_frequencies)
                elif w+'s' in raw_frequencies:
                   self.merge_words(w, w+'s', raw_frequencies)
                else:
                    self.frequencies[w] = raw_frequencies[w]                    
            
        return self.frequencies

    def create_bigrams(self):
        self.bigrams = [f"{b[0]}_{b[1]}" for b in zip(text.split()[:-1], text.split()[1:])]
