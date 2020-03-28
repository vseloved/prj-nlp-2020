import re
import xml.sax
danish_wiktionary_filename = 'dawiktionary-20200301-pages-articles-multistream.xml'
brackets_pattern = re.compile(r'\[\[(.*?)\]\]')
non_sym_token_pattern = re.compile(r'\{\{\-(.*?)\-\}\}')
language_token_pattern = re.compile(r'\{\{\=(.*?)\=\}\}')


class DanishHandler(xml.sax.ContentHandler):
    def __init__(self):
        super().__init__()
        self.words_and_synonyms = {}
        self.current_key = ""
        self.current_synonyms = []
        self.inTitleTag = False
        self.inTextTag = False
        self.inDanishSection = False
        self.foundSynonymKey = False

    def startDocument(self):
        print('---started processing danish dictionary ---')

    def endDocument(self):
        print('---ended processing danish dictionary ---')

    def startElement(self, tag, attrs):
        if tag == 'title':
            self.inTitleTag = True
        elif tag == 'text':
            self.inTextTag = True

    def endElement(self, tag):
        self.inTitleTag = False
        self.inTextTag = False
        self.foundSynonymKey = False
        if self.current_synonyms:
            self.words_and_synonyms[self.current_key] = self.current_synonyms
            self.current_synonyms = []

    def characters(self, data):
        if self.inTitleTag:
            self.current_key = data
        elif self.inTextTag:
            language_section_data = language_token_pattern.findall(data)
            if language_section_data:
                # Some pages contain section for different languages, not only danish
                if language_section_data[0] == 'da':
                    self.inDanishSection = True
                else:
                    self.inDanishSection = False

            if self.inDanishSection:
                # There are multiple types of synonym tag
                if ('Synonym' in data and '====' in data) or data == '{{-syn-}}':
                    self.foundSynonymKey = True
                elif non_sym_token_pattern.findall(data):
                    self.foundSynonymKey = False
                # Line can contain words and their meanings, but sunonyms themselves
                # are enclosed in double square brackets
                if self.foundSynonymKey and brackets_pattern.findall(data):
                    # I think this is usecase of walrus operator, but I don't have needed version yet
                    data_trimmed = brackets_pattern.findall(data)[0]
                    self.current_synonyms.append(data_trimmed)


if __name__ == "__main__":
    parser = xml.sax.make_parser()
    handler = DanishHandler()
    parser.setContentHandler(handler)
    parser.parse(danish_wiktionary_filename)
    with open('synonyms.txt', 'w') as f:
        for word, synonyms in handler.words_and_synonyms.items():
            print(f'{word} -- {synonyms}', file=f)
