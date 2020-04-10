import requests
import json
import re
from collections import defaultdict

def make_request(url, query, cb_fn):
    print('url: ', url)
    r = requests.get(url, params = {'format': 'json', 'query': query})
    print('status: ', r.status_code)
    data = r.json()
    return list(map(cb_fn, data['results']['bindings']))

wikidata_url = 'https://query.wikidata.org/sparql'
dbpedia_url = 'http://dbpedia.org/sparql'


query1 = '''
SELECT DISTINCT ?physicist ?physicistLabel ?birthDate
                ?birthPlaceLabel ?causeOfDeathLabel
WHERE
{
  ?physicist wdt:P106 wd:Q169470;
             wdt:P1344 wd:Q127050;
             wdt:P569 ?birthDate;
             wdt:P19 ?birthPlace.
             
  OPTIONAL { ?physicist wdt:P509 ?causeOfDeath. }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
'''

query2 = '''
SELECT ?physicist ?physicistLabel
       (GROUP_CONCAT(DISTINCT ?awardLabel; separator=" | ") as ?awards)
WHERE 
{
  ?physicist wdt:P106 wd:Q169470;
             wdt:P1344 wd:Q127050;
             wdt:P166 ?award.

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
    ?physicist rdfs:label ?physicistLabel .
    ?award rdfs:label ?awardLabel .
  }
}
GROUP BY ?physicist $physicistLabel
ORDER BY $physicistLabel
'''

query3 = '''
SELECT ?physicist ?physicistLabel
       (GROUP_CONCAT(DISTINCT ?eduPlaceLabel; separator=" | ") as ?eduPlaces)
WHERE 
{
  ?physicist wdt:P106 wd:Q169470;
             wdt:P1344 wd:Q127050;
             wdt:P166 ?eduPlace.

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".
    ?physicist rdfs:label ?physicistLabel .
    ?award rdfs:label ?eduPlaceLabel .
  }
}
GROUP BY ?physicist $physicistLabel
'''

query4 = '''
SELECT DISTINCT ?person ?o
WHERE {
  ?person dct:subject ?o ;
          rdf:type dbo:Scientist;
          dct:subject dbc:Manhattan_Project_people .

  FILTER regex(?o, "cancer")
}
'''

query1_cb = lambda x: {
    'name': x['physicistLabel']['value'],
    'brithdate': x['birthDate']['value'],
    'birth_place': x['birthPlaceLabel']['value'],
    'cause_of_death': x.get('causeOfDeathLabel', {}).get('value', None),
    'mhp_involvement': True
}
query2_cb = lambda x: { 'name': x['physicistLabel']['value'], 'awards': x['awards']['value'] }
query3_cb = lambda x: { 'name': x['physicistLabel']['value'], 'eduPlaces': x['eduPlaces']['value'] }
query4_cb = lambda x: { 'name': re.sub('_', ' ', x['person']['value'].split('/')[-1]), 'has_caner': True }


queries = [
    (wikidata_url, query1, query1_cb),
    (wikidata_url, query2, query2_cb),
    (wikidata_url, query3, query3_cb),
    (dbpedia_url, query4, query4_cb),
]

data = defaultdict(dict)

for url, q, cb in queries:
    physicists = make_request(url, q, cb)
    
    for p in physicists:
        data[p['name']].update(p)

with open('physicists.json', 'w') as out:
    json.dump(list(data.values()), out)
