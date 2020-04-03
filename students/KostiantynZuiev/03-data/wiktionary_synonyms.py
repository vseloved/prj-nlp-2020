import re
import xml.sax
import langid

class MyHandler(xml.sax.ContentHandler):

    def __init__(self, output):
        xml.sax.ContentHandler.__init__( self)
        self.current_node = ''
        self.current_word = ''
        self.current_text = ''
        # self.synonyms_map = {}
        self.output = output

    def startElement(self, name, attrs):
        self.current_node = name

    def is_pure_word(self, word):
        if ":" in word:

            return False
        if "|" in word:

            return False
        if " " in word:

            return False
        if langid.classify(word)[0] != 'de':

            return False

        return True

    def get_pure_synonyms(self, synonyms):
        
        return list(filter(self.is_pure_word, synonyms))

    def characters(self, content):
        if self.current_node == "title":
            if self.is_pure_word(content):
                self.current_word = content
        if self.current_node == "text":
            self.current_text += content


    def endElement(self, name):
        if self.current_node == "text" and self.current_word:
            r = re.search(r'{{Synonyme}}(?P<synonyms>[^{]+){{', self.current_text)
            if r:
                synonyms_string = r.groupdict().get('synonyms')
                synonyms = re.findall(r'(?:\[\[)([^\[\]]+)(?:\]\])', synonyms_string)
                if synonyms:
                    pure_synonyms = self.get_pure_synonyms(synonyms)
                    if pure_synonyms:
                    # self.synonyms_map[self.current_word] = synonyms
                        self.output.write(f'{self.current_word}: {pure_synonyms}\n')
                        self.current_word = ''

                    # print(self.synonyms_map)
        
        self.current_text = ''
        self.current_node = ''


filename = "dewiktionary-20200301-pages-articles-multistream.xml"
with open('synonyms.txt','w') as f:
    handler = MyHandler(f)
    xml.sax.parse(filename, handler)
    # for word,synonyms in handler.synonyms_map.items():
    #     f.write(f'{word}: {synonyms}')
