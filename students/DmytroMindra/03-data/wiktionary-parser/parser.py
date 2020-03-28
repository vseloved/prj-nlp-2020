import xml.sax
import os
import re

file_path = os.getcwd() + '/../data/plwiktionary-20200301-pages-articles-multistream.xml'

# Templates for extracting data from <text> tag
synonym_section_template = ".*{{synonimy}}(.*?){{antonimy}}.*"
synonym_template = "[[]]"

output_file_name ='output.txt'
output_file = open(output_file_name, "w")


class WiktionaryHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.title = None
        self.text = "empty"
        self.CurrentData = ""
        self.counter = 0

    # Call when an element starts
    def startElement(self, tag, attributes):
        self.CurrentData = tag

        if tag == "text":
            self.CurrentData = "text"
            self.text = ""

        if tag == "title":
            self.CurrentData = "title"
            self.title = ""

    # Call when a portion of characters arrives
    def characters(self, content):
        if self.CurrentData == "title":
            self.title += content

        if self.CurrentData == "text":
            self.text += content

    # Call when an elements ends
    def endElement(self, tag):

        if tag == "text":
            self.counter +=1

            # it takes a bit to process the data.
            # these lines make waiting a bit more fun
            if self.counter%1000 == 0:
                print("{} entities processed".format(self.counter))

            # Here we extract and log synonyms to file
            match = re.match(synonym_section_template, self.text, flags=re.DOTALL)
            synonyms = []
            if match is not None:
                if len(match.groups()[0]) > 5:
                    synonyms_string = match.groups()[0]
                    synonyms = re.findall(r'\[\[(.*?)\]\]', synonyms_string, flags=re.DOTALL)
                    synonyms = synonyms

            if self.title is not None and self.title.strip()!= "":
                synonym_string = ""
                if synonyms is not None:
                    synonym_string = ', '.join(synonyms)
                output_string = self.title.strip()+': '+synonym_string+'\n'
                output_file.write(output_string)

            self.CurrentData = ""


if (__name__ == "__main__"):

    # create an XMLReader
    parser = xml.sax.make_parser()

    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = WiktionaryHandler()
    parser.setContentHandler(Handler)

    file = open(file_path)
    parser.parse(file)

    print ("done")
    output_file.close()