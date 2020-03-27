import re
import xml.sax.handler
import xml.sax
import pandas as pd

syns = []

class Handler(xml.sax.handler.ContentHandler):    
    def __init__(self):        
        self.in_text = False
        self.is_noun = False
        self.swedish = False
        self.have_translation = False
        self.word = ""
        self.synonyms = []
        self.translations = []
        self.re_word = re.compile(r"'''(.+)'''")
        self.re_synonym_string = re.compile(r"^#:{{synonymer")
        self.re_synonym_matching = re.compile(r"\[\[([a-zA-ZåäöÄÖÅ ]+)\]\]")
        self.re_translation_string = re.compile(r"^\*engelska")
        self.re_translation = re.compile(r"en\|([a-zA-Z -]+)")

    def startElement(self, name, attrs):        
        if name == "text": #  xml:space="preserve"
            self.in_text = True    
            
    def characters(self, line):
        if self.in_text and line != "\n":
            if line=="==Svenska==":
                self.swedish=True
            elif self.swedish and line=="===Substantiv===":
                self.is_noun = True
            elif self.is_noun and line=="====Översättningar====":
                self.have_translation = True
            elif self.have_translation and self.re_translation_string.match(line):
                self.translations = self.re_translation.findall(line)
            elif self.is_noun and self.re_word.match(line):
                self.word = self.re_word.search(line).group(1)
            elif self.is_noun and self.re_synonym_string.match(line):
                self.synonyms = self.re_synonym_matching.findall(line)
                    
                

    def endElement(self, name):        
        if name == "text":
            if self.is_noun and len(self.translations) and len(self.synonyms):
                w = re.sub(r"\s+", " ", self.word.replace("[", " ").replace("]", " ")).strip()
                syns.append((w+str(self.translations), self.synonyms))
            self.word = ""
            self.synonyms = []
            self.translations = []
            self.in_text = False


P = xml.sax.make_parser() 
P.setContentHandler(Handler())
P.parse("svwiktionary-latest-pages-articles.xml")


df = pd.DataFrame(syns, columns = ["word", "syn"])
df.to_pickle("./syns.pkl")