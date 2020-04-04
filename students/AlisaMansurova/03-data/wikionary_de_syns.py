import xml.sax
import re
import os

absDir = os.path.dirname(os.path.abspath(__file__))
data_file_name = '../../../../../dewiktionary-20200301-pages-meta-current.xml'
data_file = os.path.join(absDir, data_file_name)
res_file = os.path.join(absDir, 'wiktionary_de_syns.txt')


def parse_syns(text):
    syns = re.findall('(?<=\\[\\[)[\\w]+(?=\\]\\])', text)
    return syns


def append_result(res):
    with open(res_file, 'a') as f:
        f.write(res)


class SynsHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.CurrentData = ''
        self.word = ''
        self.text = ''
        self.res = ''
        self.syn_section = False

    def startElement(self, tag, attributes):
        self.CurrentData = tag

    def endElement(self, tag):
        if self.CurrentData == 'text' and self.text:
            syns = parse_syns(self.text)
            if syns:
                res = f'{self.word}: {syns}\n'
                if len(self.res) < 1000:
                    self.res += res
                else:
                    append_result(self.res)
                    self.res = ''

        self.CurrentData = ''
        self.text = ''

    def characters(self, content):
        if self.CurrentData == 'title':
            self.word = content
        elif self.CurrentData == 'text':
            if content.startswith('{{Synonyme}}'):
                self.syn_section = True
            if content.startswith('{{') and 'Synonyme' not in content:
                self.syn_section = False
            if self.syn_section and 'Synonyme' not in content \
                    and content.strip():
                self.text += content


if (__name__ == '__main__'):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = SynsHandler()
    parser.setContentHandler(Handler)

    parser.parse(data_file)
