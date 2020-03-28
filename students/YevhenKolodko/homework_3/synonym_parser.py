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
            # print(self.current_synonyms)
            self.words_and_synonyms[self.current_key] = self.current_synonyms
            self.current_synonyms = []

    def characters(self, data):
        if self.inTitleTag:
            self.current_key = data
            if data == 'hund':
                pass
        elif self.inTextTag:
            if language_token_pattern.findall(data):
                if language_token_pattern.findall(data)[0] == 'da':
                    self.inDanishSection = True
                else:
                    self.inDanishSection = False

            if self.inDanishSection:
                if ('Synonym' in data and '====' in data) or data == '{{-syn-}}':
                    self.foundSynonymKey = True
                elif non_sym_token_pattern.findall(data):
                    self.foundSynonymKey = False

                if self.foundSynonymKey and brackets_pattern.findall(data):
                    # I think this is usecase of walrus operator, but I don't have needed version
                    data_trimmed = brackets_pattern.findall(data)[0]
                    self.current_synonyms.append(data_trimmed)


sample = """
{{-etym-}}
{{compound|politi|betjent|lang=da}}
{{-noun-|da}}
{{pn}} {{c}}
{{wikipedia}}
# En [[person]] [[ansætte|ansat]] ved [[politi]]et.
{{-decl-}}
{{da-noun|en|politibetjent|politibetjenten|politibetjente|politibetjentene}}
{{-trans-}}
{{(}}
* {{en}}: {{t|en|police officer}}, {{t|en|policeman}},{{t|en|cop}}
* {{O|eo|policisto}}
* {{fr}}: {{t|fr|policier|m}}, {{t|fr|agent|m}}, {{t|fr|agent de police}}, {{t|fr|flic|m}} (F)
* {{it}}: {{t|it|sbirro|m}}
* {{no}}: {{t|no|politimann|m}}, {{t|no|politibetjent|m}}, {{t|no|politi|m}}
* {{nl}}: {{t|nl|politieagent}}, {{t|nl|agent}}
{{-}}
* {{pl}}: {{t|pl|policjant|m}}
* {{sk}}: {{t|sk|policajt|m}}
* {{cs}}: {{t|cs|policista|m}}
* {{de}}: {{t|de|Polizist|m}}
* {{hu}}: {{t|hu|rendőr}}
{{)}}

==== Eksempel ====

&quot;''[[tyv]]en [[løb]] [[afsted]], [[da]] [[han]] så [[politibetjent]]en''&quot;.

==== Synonym ====
* [[strisser]] - (slang/gadesprog)
* [[strissersvin]] - (slang/fornærmelse)

[[Kategori:Professioner på dansk]]

[[en:politibetjent]]
[[eo:politibetjent]]
[[fr:politibetjent]]
[[hu:politibetjent]]
[[mg:politibetjent]]
[[pl:politibetjent]]
[[vi:politibetjent]]
"""

if __name__ == "__main__":
    parser = xml.sax.make_parser()
    # parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = DanishHandler()
    parser.setContentHandler(handler)
    parser.parse(danish_wiktionary_filename)
    with open('synonyms.txt', 'w') as f:
        for word, synonyms in handler.words_and_synonyms.items():
            print(f'{word} -- {synonyms}', file=f)
