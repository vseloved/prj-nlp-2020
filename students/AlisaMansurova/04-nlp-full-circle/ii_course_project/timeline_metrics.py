import json
import os
from dateutil.parser import parse as date_parse

absDir = os.path.dirname(os.path.abspath(__file__))
validation_data_file_name = './validation_data.json'
validation_data_file = os.path.join(absDir, validation_data_file_name)
results_data_file_name = './result_data.json'
results_data_file = os.path.join(absDir, results_data_file_name)

with open(validation_data_file) as f:
    validation_data = json.load(f)
with open(results_data_file) as f:
    results_data = json.load(f)


def validate_result(expected, actual):
    invalid_order = 0
    false_positives = len(
        [x['events'] for x in actual if x['date'] not in (y['date'] for y in expected)])
    false_negatives = len(
        [x['events'] for x in expected if x['date'] not in (y['date'] for y in actual)])
    true_pos = 0

    act_len = len(actual)

    for i in range(act_len):
        res = actual[i]
        act_events = res['events']
        act_date = res['date']

        # validate correctness of date order
        if i < act_len - 1:
            curr_date = date_parse(act_date)
            next_date = date_parse(actual[i + 1]['date'])
            if curr_date > next_date:
                invalid_order += 1

        # check for false-positives, false-negatives & true-positives
        exp_data = next((x for x in expected if x['date'] == act_date), None)
        if exp_data:
            exp_events = exp_data['events']
            fp = len([x for x in act_events if x not in exp_events])
            fn = len([x for x in exp_events if x not in act_events])
            tp = len([x for x in exp_events if x in act_events])
            false_positives += fp
            false_negatives += fn
            true_pos += tp

        for act_ev in act_events:
            t = [x['date'] for x in expected if act_ev in x['events']
                 and act_date != x['date']]
            false_negatives += len(t)

    recall = round(true_pos/(true_pos + false_negatives), 2)
    precision = round(true_pos/(true_pos + false_positives), 2)
    correct_order = round((act_len - invalid_order)/act_len, 2)

    return ({'recall': recall, 'precision': precision, 'correct_order': correct_order})


res = validate_result(validation_data, results_data)
print(res)
