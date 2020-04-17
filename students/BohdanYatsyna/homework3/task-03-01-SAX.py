import xml.sax
from tqdm import tqdm
import re

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = {}
        self.is_synonym = False
        self.re_synonym = re.compile('{{Synonyme}}')
        self.re_synonym_end = re.compile('\{\{.{1,}\}\}')
        self.re_words = re.compile('(?<=\[\[)\w{1,}(?=\]\])')
        self.re_garbadge = re.compile('MediaWiki:')

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

        if self._current_tag == 'text':
            if self.re_synonym.match(content):
                self.is_synonym = True
            elif self.is_synonym:
                if self.re_synonym_end.match(content):
                    self.is_synonym = False
                    return
                synonyms = self.re_words.findall(content)
                if len(synonyms): self._pages.update({self._values['title']: synonyms})

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            self.is_synonym = False


# Object for handling xml
handler = WikiXmlHandler()
# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

# Iteratively process file
data_path = "/Users/bogdan/Downloads/dewiktionary-20200301-pages-articles-multistream.xml"

num_lines = sum(1 for line in open(data_path, 'r'))
with open(data_path) as file:
    for line in tqdm(file, total=num_lines):
        parser.feed(line)

with open('task-03-SAX.txt', 'w') as f:
    for key, value in handler._pages.items():
        print('{}: {}'.format(key, value), file=f)
