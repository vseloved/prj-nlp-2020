import re
import xml.sax.handler
import xml.sax
import pandas as pd

syns = []
awailable_poss = {
    'Pronomen', 'Subjunktion', 'Preposition', 'Adjektiv', 'Verb', 'Källor', 'Affix', 'Substamtiv', 'Konjunktion', 
    'Adverb', 'Substantiv', 'Interjektion', 'Artikel', 'Förkortning', 'Räkneord', 'Verb.'
}

def safe_list_get (l):
  try:
    return "[" + str(l[0]) + "]"
  except IndexError:
    return " "

class Handler(xml.sax.handler.ContentHandler):    
    def __init__(self):        
        self.in_text = False
        self.has_pos = False
        self.pos = ""
        self.swedish = False
        self.have_translation = False
        self.word = ""
        self.synonyms = []
        self.translations = []
        self.re_word = re.compile(r"'''(.+)'''")
        self.re_pos = re.compile(r"^={3}([^=]+)={3}$")
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
            elif self.swedish and self.re_pos.match(line):
                self.has_pos = True
                self.pos = self.re_pos.search(line).group(1).strip()
            elif self.has_pos and line=="====Översättningar====":
                self.have_translation = True
            elif self.have_translation and self.re_translation_string.match(line):
                self.translations = self.re_translation.findall(line)
            elif self.has_pos and self.re_word.match(line):
                self.word = self.re_word.search(line).group(1)
            elif self.has_pos and self.re_synonym_string.match(line):
                self.synonyms = self.re_synonym_matching.findall(line)
                    
    def endElement(self, name):    
        def insert(w, t, s):
            key = "%s %s" % (w, safe_list_get(t))
            syns.append((key.strip(), s))
        if name == "text":
            if self.has_pos and self.pos in awailable_poss and len(self.synonyms):
                w = re.sub(r"\s+", " ", self.word.replace("[", " ").replace("]", " ")).strip()
                if len(w.split())==1:
                    insert(w, self.translations, self.synonyms)
                else:
                    for e in self.synonyms:
                        if len(e.split())==1:
                            self.synonyms.remove(e)
                            self.synonyms.append(w)
                            insert(e, self.translations, self.synonyms)


            self.word = ""
            self.synonyms = []
            self.translations = []
            self.in_text = False


import pathlib
curr_path = pathlib.Path(__file__).parent.absolute()
path = curr_path / 'svwiktionary-latest-pages-articles-multistream.xml'
syns_path = curr_path / 'syns.pkl'

P = xml.sax.make_parser() 
P.setContentHandler(Handler())
P.parse(path.as_posix())


df = pd.DataFrame(syns, columns = ["word", "syn"])
df.to_pickle(syns_path)