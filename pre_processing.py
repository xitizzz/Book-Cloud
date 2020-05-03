

class PreProcessing:

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
            {ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_\"+"}).lower()
    
    def create_unigrams(self):
        self.unigrams = self.text.split()

    def create_bigrams(self):
        self.bigrams = [f"{b[0]}_{b[1]}" for b in zip(text.split()[:-1], text.split()[1:])]
