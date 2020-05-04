import nltk
import json


from sklearn.metrics import classification_report


false_tags = ["TO","IN","WDT","WP","DT","WP$","WRB", "LS", "CC", "PRP"]

with open('run-on-test.json','r') as f:
    test_sentences = json.load(f)


results = []
for sentence in test_sentences:
    results_to_compare = []
    for i, (token, expected_result) in enumerate(sentence):
        result = False
        token_pos = nltk.pos_tag([token])[0][1]
        if token_pos in false_tags and token != "I":
            if token[0].isupper() and i != 0:
                results_to_compare[-1][1] = True
        results_to_compare.append([token, result])
    results.append(results_to_compare)


test_labels = [item[1] for sentence in test_sentences for item in sentence]
classified_labels = [item[1] for result in results for item in result]

print(classification_report(test_labels, classified_labels))

