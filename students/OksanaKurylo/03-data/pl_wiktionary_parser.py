#!/usr/bin/env python
# coding: utf-8

import xml.sax
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta

output_file_name ='pl_synonyms.txt'
output_file = open(output_file_name, "w+")

def find_synonyms(text, title):
    lines = [line for line in text.splitlines() if line.strip()]
    is_polish, has_synonyms = False, False 
    syns = defaultdict(list)
    for line in lines:
        if "({{język polski}}) ==" in line:
            is_polish = True
            end_ind = line.find(' ({{język polski}}) ==')
        if "{{synonimy}}" in line:
            has_synonyms = True
        if is_polish and has_synonyms and line.startswith(':'):
            synonyms = re.findall(r'\[\[(.*?)\]\]', line)
            if len(synonyms) != 0:
                syns[title].append(synonyms)
        elif line.startswith("{{antonimy}}"):
            break
        
    if syns:
        return syns
    else:
        return None

class PLWikiHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.current_tag = ""
        self.page = ""
        self.title = ""
        self.text = ""
        
    def startElement(self, tag, attributes):
        self.current_tag = tag
        if tag == "title":
            self.title = ""
            self.current_tag = "title"
        if tag == "text":
            self.text = ""
            self.current_tag = "text"
    
    def endElement(self, tag):
        if tag == "text":
            if self.title != "" and "Wikisłownik:" not in self.title:
                syns = find_synonyms(self.text, self.title)
                if syns != None:
                    for k, v in syns.items():
                        output_file.write('{}: {}\n'.format(k, v))
        self.current_tag = ""
        

    def characters(self, content):
        if self.current_tag == "title":
            self.title += content
        if self.current_tag == "text":
            self.text += content
            
if ( __name__ == "__main__"):
    t1 = time.time()
    # create an XMLReader
    parser = xml.sax.make_parser()
    
    # turn off namespaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = PLWikiHandler()
    parser.setContentHandler(Handler)

    parser.parse("plwiktionary-20200401-pages-articles-multistream.xml")
    output_file.close()
    print("See results in {}".format(output_file_name))
    t2 = time.time()
    end_time = t2 - t1
    print("Time: ", str(timedelta(seconds=end_time)))
