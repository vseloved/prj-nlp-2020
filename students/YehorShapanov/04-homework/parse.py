import pandas as pd 
import numpy as np
import json 
import wikipedia

import re
import spacy 

nlp = spacy.load("en_core_web_md")

MS = 'Michael Schumacher'

wikipedia.set_lang("en")
wiki_michael_article = wikipedia.page("Michael_Schumacher")

#Parse Michael main article
sections = wiki_michael_article.content.split('\n')
re_team_year = re.compile(r"^===\s(\w+)\s\(([\d\W]+)\)\s===$")

team_years = []
for line in [l for l in sections if re_team_year.match(l)!=None]: 
    team_years.append(re_team_year.search(line).groups(0))

template = "{}_Formula_One_World_Championship"
re_schumi = re.compile(r'Schumacher')
re_ralf = re.compile(r'Ralf')
def check_if_schumi_in_named_ents(s):
    """ 
    return MS entity
    """
    for t in s.ents:
        if re_schumi.search(t.text):
            if re_ralf.search(t.text)==None:
                return t
    return None

def is_person(tag):
    if tag==None:
        return False
    return tag.ent_type_=="PERSON"

def dependency_dfs(start):
    stack = [start]
    while stack:
        tag = stack.pop()
        if not is_person(tag):
            stack.extend([t for t in tag.children if t.dep_ in ["prep", "pobj"]])
        else:
            return tag
    return None

def find_token_with_dep(root, dep):
    tmp=[token for token in root.children if token.dep_ in dep]
    if len(tmp):
        return tmp[0]
    return None

def sentence_about_winning(s):
    """
        return True if can extract from sentence that Michael won
    """
    if check_if_schumi_in_named_ents(s)==None:
        return False

    verbs = [token for token in s if token.pos_ == 'VERB']
    win = [token for token in verbs if token.lemma_=="win"]
    if len(win):
        root = win[0]
        agent=find_token_with_dep(root, "agent")
        nominal_subject=find_token_with_dep(root, ["nsubjpass", "nsubj"])
        prep=None
        dobj=None
        if not agent:
            prep=find_token_with_dep(root, "prep")
            dobj=find_token_with_dep(root, "dobj")
        pobj=None
        if agent:
            pobj=find_token_with_dep(agent, "pobj")
        elif prep:
            pobj_from_prep=find_token_with_dep(prep, "pobj")
            if pobj_from_prep:
                agent=find_token_with_dep(pobj_from_prep, "agent")
            if agent:
                pobj=find_token_with_dep(agent, "pobj")
            else:
                # Last resort
                pobj=dependency_dfs(root)
        is_schumacher=False 
        if not pobj:
            if root.tag_=='VBD' and nominal_subject and nominal_subject.text=="Schumacher":
                #try to find direct object
                dobj=find_token_with_dep(root, "dobj")
                if dobj and dobj.text=='position': #usualy people don't say `won first position`
                    return False
                return True
            return False
        if pobj.text=="Schumacher":
            is_schumacher=True
        if not is_schumacher and pobj.text=="Michael":
            print("Add processing")
        if nominal_subject and nominal_subject.text=="race" and is_schumacher:
            return True
        if dobj and dobj.text=="race":
            if is_person(nominal_subject):
                name = get_full_name(nominal_subject)
                if name==MS:
                    return True
     
    take = [token for token in verbs if token.lemma_=="take"]
    if len(take):
        #(smb)->take->(smth)
        root = take[0]
        nsubj=find_token_with_dep(root, "nsubj")
        if is_person(nsubj):
            is_schumacher=False 
            if nsubj.text=="Schumacher":
                is_schumacher=True
            if not is_schumacher and nsubj.text=="Michael":
                print("Add processing")
            if not is_schumacher:
                return False
            d=find_token_with_dep(root, "dobj")
            if d and d.text in ["win", "victory"]:
                return True

    schumi_ent=check_if_schumi_in_named_ents(s)
    #statistical experiment
    if 'victory' in [v.lemma_ for v in schumi_ent.root.ancestors]:
        return True          
    
    return False

def get_full_name(token):
    if token.dep_=='compound':
        head = token.head
        if is_person(head):
            return token.text + " " + head.text
        else:
            return token.text
    else:
        return " ".join([t.text for t in token.children if t.dep_=='compound']) + " " + token.text

def check_name(t):
    name=get_full_name(t)
    if name==MS:
        return (False, None)
    else:
        return (True, name)

def sentence_about_second(s):
    """
        If can extract who took second place in race - return (True, First Last)
        else return (False, None)
    """
    if not "second" in [t.lemma_ for t in s]:
        return (False, None)
    root = [token for token in s if token.head == token][0]
    if root.lemma_ in ["finish", "be"]:
        agent=find_token_with_dep(root, "agent")
        nominal_subject=find_token_with_dep(root, ["nsubjpass", "nsubj"])
        if nominal_subject:
            #try searching for second in root's children 
            for t in [x for x in root.children if x.text=="second"]:
                if t.dep_=='acomp' or t.dep_=='advmod':
                    if is_person(nominal_subject):
                        return (True, get_full_name(nominal_subject))
        if agent:
            pobj=find_token_with_dep(agent, "pobj")
        else:
            pobj=find_token_with_dep(root, "pobj")
        advmod=find_token_with_dep(root, "advmod")
        if not advmod:
            l = root.nbor(-1)
            r = root.nbor(1)
            if l.pos_=="ADV":
                advmod=l
            elif r.pos_=="ADV":
                advmod=r
        if not advmod:
            return (False, None)
        if advmod.text=="second":
            if is_person(nominal_subject):
                l = nominal_subject.nbor(-1)
                if is_person(l):
                    #Was second-fastest etc.
                    name=l.text + " " + nominal_subject.text
                    if name==MS:
                        return (False, None)
                    else:
                        return (True, name)
                r = nominal_subject.nbor(1)
                if is_person(r):
                    name=nominal_subject.text + " " + r.text
                    if name==MS:
                        return (False, None)
                    else:
                        return (True, name)
                return (False, None)
            else:
                c = [t for t in nominal_subject.subtree if t.dep_=='appos']
                if len(c):
                    if len(c)>1:
                        print('check')
                    mod=c[0]
                    if is_person(mod):
                        return (True, get_full_name(mod))
    #verb is not finish 
    #just find second directly 
    token = [t for t in s if t.lemma_=="second"]
    for t in token: 
        if t.pos_=='ADJ':
            y = t.head
            if is_person(y):
                return (True, get_full_name(y))
            if y.pos_=='NOUN':
                if y.text in ['place', 'position']:
                    #It's proper `second` find subj
                    x = 1
                    while y.i-x>0 and y.i+x<len(s):
                        n1 = y.nbor(-x)
                        n2 = y.nbor(x)
                        if is_person(n1):
                            return check_name(n1)
                        if is_person(n2):
                            return check_name(n2)
                        x+=1
                    while y.i-x>0:
                        n1 = y.nbor(-x)
                        if is_person(n1):
                            return check_name(n1)
                        x+=1
                    while y.i+x<len(s):
                        n2 = y.nbor(x)
                        if is_person(n2):
                            return check_name(n2)
                        x+=1

    return (False, None)

def process_race(race):
    lines = race.split('\n')
    win=False
    for line in lines:
        second=False
        name=None
        for t1 in re.split('(\.|!|\?)', line):
            if len(t1)<8:
                continue
            s=nlp(t1)
            if not win:
                win = sentence_about_winning(s)
            if not second:
                second, name = sentence_about_second(s)
            if win and second:
                return (win, name)
        
    return (win, None)

re_year_race = re.compile(r"^===\sRace\s\d+:\s[\w\s]+===$")
def process_year(year):
    """
        returns number of wins
    """
    y = template.format(year)
    season_of_article=wikipedia.page(y, auto_suggest=False, redirect=False)
    sections = []
    curr_section=""
    start_processing = False

    re_t="^{}\s(.+)Grand Prix$".format(year)
    re_gran_prix_link = re.compile(re_t)
    links = [l for l in season_of_article.links if re_gran_prix_link.match(l)]
    for line in season_of_article.content.split('\n'):
        if line[:3]=="===":
            start_processing = False
        if re_year_race.match(line):
            if len(curr_section)!=0:
                sections.append(curr_section)
                curr_section=""
            start_processing=True
        if start_processing:
            curr_section += line
    sections.append(curr_section)
    
    wins=[]
    #This check shows if all of race descriptions have distinct wikipedia article 
    #if distinct article - we process that if not
    #we process section about this race from whole year description 
    if len(sections)<=len(links):
        print("{} links:".format(len(links)))
        for race_link in links:
            page_link=race_link.replace(" ", "_")
            race_article=wikipedia.page(page_link, auto_suggest=False, redirect=False)
            #If Michael wins this race - return who took second place
            #if unable to detect who took 2nd - return Unknown 
            #else return None
            #print("Processing race: {}".format(race_link))
            was_win, second = process_race(race_article.content)
            if was_win:
                gp = re_gran_prix_link.search(race_link).group(1)
                uri = 'http://dbpedia.org/resource/'+page_link
                wins.append([uri, gp+"Grand Prix", year, second])
    else:
        for s in sections:
            process_race(s)

    return wins


import itertools
processed_years = set()
def process_season(s):
    a = [int("".join(list(g))) for a, g in itertools.groupby(s, key=str.isdigit) if a]
    r=int(a[0])
    wins=[]
    if len(a)==2: 
        end=int(a[1])
        for i in range(r, end):
            if i in processed_years:
                print("===Year skipped===")
                continue
            print("===Processing year({}/{}): {}===".format(i-r+1, end-r+1, i))
            wins.extend(process_year(i))
            processed_years.add(i)
    else:
        if r in processed_years:
            return []
        print("===Processing year(1/1): {}===".format(r))
        wins=process_year(r)
        processed_years.add(r)

    return wins

# Test
# assert(True==sentence_about_winning(nlp("The race, contested over 62 laps, was the fourth race of the 2002 Formula One season and was won by Michael Schumacher driving a Ferrari.")))
# assert(True==sentence_about_winning(nlp("Michael Schumacher won ahead of Jean Alesi in the Benetton and Giancarlo Fisichella in the Jordan.")))
# assert(False==sentence_about_winning(nlp("The race is remembered for an incident involving the two title contenders Damon Hill and Michael Schumacher which forced both to retire and resulted in Schumacher winning the World Drivers' Championship.")))
# assert(True==sentence_about_winning(nlp("The 72-lap race was won by Michael Schumacher for the Ferrari team, from a second position start.")))
# assert(True==sentence_about_winning(nlp("Michael Schumacher won ahead of Jean Alesi in the Benetton and Giancarlo Fisichella in the Jordan.")))
# assert(True==sentence_about_winning(nlp("This race, Michael Schumacher's first Ferrari victory, is generally regarded as one of his finest.")))
# assert(True==sentence_about_winning(nlp("The 44-lap race was won by Michael Schumacher, driving a Benetton-Renault.")))
# assert(False==sentence_about_winning(nlp("The 69-lap race was won by Williams driver Ralf Schumacher after starting from the second position")))
# assert(True==sentence_about_winning(nlp("Michael Schumacher took his only win of the season, the second win of his career, while second place was enough for Alain Prost to clinch the championship, after Ayrton Senna's engine failed")))
# assert((True, "Alain Prost")==sentence_about_second(nlp("Michael Schumacher took his only win of the season, the second win of his career, while second place was enough for Alain Prost to clinch the championship, after Ayrton Senna's engine failed")))
# assert(True==sentence_about_winning(nlp("The 71-lap race was won by Michael Schumacher, driving a Benetton-Ford, after starting from second position.")))
# assert((True, "Damon Hill")==sentence_about_second(nlp("Senna's teammate Damon Hill finished second, with Jean Alesi third in a Ferrari")))
# assert(True==sentence_about_winning(nlp("The 69-lap race was won from pole position by Michael Schumacher, driving a Benetton-Ford, with Damon Hill second in a Williams-Renault and Jean Alesi third in a Ferrari")))
# assert((True, "Damon Hill")==sentence_about_second(nlp("The 69-lap race was won from pole position by Michael Schumacher, driving a Benetton-Ford, with Damon Hill second in a Williams-Renault and Jean Alesi third in a Ferrari")))
# assert((True, 'Gerhard Berger')==sentence_about_second(nlp("Gerhard Berger was second in the other Ferrari, with Rubens Barrichello third in a Jordan-Hart, his and the Jordan team's first podium finish. ")))
# assert(True==sentence_about_winning(nlp("Michael Schumacher, driving for Benetton, won the race despite contact with Damon Hill (who dropped to the back of the field and battled back to finish sixth).")))
# assert((True, 'Nicola Larini')==sentence_about_second(nlp("Nicola Larini, driving for Ferrari, scored the first points of his career when he achieved a podium finish in second position. ")))
# assert((False, None)==sentence_about_second(nlp("The 83-lap race was won by Michael Schumacher, driving a Benetton-Ford, after he started from second position")))

# print("# Test1")
# res = process_year(1992)
# print(len(res), 1)

# print("# Test2")
# res = process_year(1993)
# print(len(res), 1)

# print("# Test3")
# res = process_year(1994)
# print(len(res), 8)

# print("# Test4")
# res = process_year(1995)
# print(len(res), 9) # Spanish gp - no clear way on how to improve

# print("# Test5")
# res = process_year(1996)
# print(len(res), 3)

# print("# Test6")
# res = process_year(1997)
# print(len(res), 5)

# print("# Test7")
# res = process_year(1998)
# print(len(res), 6)

# print("# Test8")
# res = process_year(1999)
# print(len(res), 2)

# print("# Test9")
# res = process_year(2000)
# print(len(res), 9)

# print("# Test10")
# res = process_year(2001)
# print(len(res), 9)

# print("# Test11")
# res = process_year(2002)
# print(len(res), 11)

#Process season articles by season 
wins = []
for team, season in team_years[1:]:
    wins.extend(process_season(season))

with open('processed_data.json', 'w') as f:
    json.dump(wins, f)
