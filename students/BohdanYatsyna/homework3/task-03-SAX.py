import xml.sax
import subprocess
from tqdm import tqdm
import re


class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""

    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []
        self.is_synonym = False
        self.re_synonym = re.compile('^{{Synonyme}}')
        self.re_words = re.compile('(?!\d)\w+')
        self.re_garbadge = re.compile('MediaWiki:')



    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag == 'title':
            if not self.re_garbadge.match(content):
                self._buffer.append(content)
        if self._current_tag == 'text':
            if self.re_synonym.match(content):
                self.is_synonym = True
            elif self.is_synonym:
                self.synonyms = self.re_words.findall(line)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)

        if name == 'text':
            self._pages.append((self._values['title'], self.synonyms))


# Object for handling xml
handler = WikiXmlHandler()
# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)
# Iteratively process file

with open("/Users/bogdan/Downloads/dewiktionary-20200301-pages-articles-multistream.xml") as file:
    for line in tqdm(file):

        parser.feed(line)

        # Stop when 3 articles have been found
        if len(handler._pages) > 1000:
            print(handler._pages)
            break

    # parser.par
