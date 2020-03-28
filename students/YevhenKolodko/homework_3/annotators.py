from dataclasses import dataclass
import numpy as np

path = '/home/yevhen/prj/data/nucle_test_set.m2'
annot_types = {
    'ALL': 'All error types',
    'Vt': 'Verb tense',
    'Vm': 'Verb modal',
    'V0': 'Missing verb',
    'Vform': 'Verb form',
    'SVA': 'Subject-verb-agreement',
    'ArtOrDet': 'Article or Determiner',
    'Nn': 'Noun number',
    'Npos': 'Noun possesive',
    'Pform': 'Pronoun form',
    'Pref': 'Pronoun reference',
    'Prep': 'Preposition',
    'Wci': 'Wrong collocation/idiom',
    'Wa': 'Acronyms',
    'Wform': 'Word form',
    'Wtone': 'Tone',
    'Srun': 'Runons, comma splice',
    'Smod': 'Dangling modifier',
    'Spar': 'Parallelism',
    'Sfrag': 'Fragment',
    'Ssub': 'Subordinate clause',
    'WOinc': 'Incorrect sentence form',
    'WOadv': 'Adverb/adjective position',
    'Trans': 'Link word/phrases',
    'Mec': 'Punctuation, capitalization, spelling, typos',
    'Rloc-': 'Local redundancy',
    'Cit': 'Citation',
    'Others': 'Other errors',
    'Um': 'Unclear meaning (cannot be corrected)',
}


@dataclass
class Annotation:
    """
    This class not only carries all parameters of annontation string, but also
    provides methods __eq__ and __hash__ on desired fields (it ignores annotation_type and annotator_id)
    With method __hash__ we'll be able to put all annotations to set() and calculate unions and intersections
    """
    sentence_id: int
    from_token: str
    to_token: str
    annot_type: str
    suggested_change: str
    annotator_id: int

    def __eq__(self, other):
        if isinstance(other, Annotation):
            return (
                self.sentence_id == other.sentence_id
                and self.from_token == other.from_token
                and self.to_token == other.to_token
                and self.suggested_change == other.suggested_change
            )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((
            self.sentence_id,
            self.from_token,
            self.to_token,
            self.suggested_change
        ))


def read_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()
        return lines


def extract_suitable_sentence_line_nums(lines):
    """This function helps to ignore in advance sentences with not enough annotations (0 or 1).
    This function will not filter out cases, when only one annotator made 2 or more notes, but they are rare"""
    first_symbols = [l[0] for l in lines]
    suitable_indices = set()
    num_annotations_dict = {}
    sentence_index = None
    annot_counter = 0
    for i, token in enumerate(first_symbols):
        if token == 'S':
            sentence_index = i
            annot_counter = 0
        elif token == 'A':
            annot_counter += 1
        elif token == '\n' and annot_counter > 1:
            suitable_indices.update([sentence_index])
            num_annotations_dict[sentence_index] = annot_counter
    return suitable_indices, num_annotations_dict


def parse_annotation_line(line, sentence_id):
    line_elements = line[2:].rstrip().split('|||')
    from_token, to_token = line_elements[0].split(' ')
    annotation = Annotation(
        sentence_id=sentence_id,
        from_token=from_token,
        to_token=to_token,
        annot_type=line_elements[1],
        suggested_change=line_elements[2],
        annotator_id=int(line_elements[-1]),
    )
    return annotation


def generate_annotations(lines, suitable_indices, num_annotations):
    all_annotations_by_id = {
        0:[],
        1:[],
        2:[],
        3:[],
        4:[],
    }
    sentence_counter = -1
    for index, line in enumerate(lines):
        if index in suitable_indices:
            sentence_counter += 1
            for annot_number in range(1, num_annotations[index] + 1):
                annotation = parse_annotation_line(lines[index + annot_number], sentence_counter)
                all_annotations_by_id[annotation.annotator_id].append(annotation)
    return all_annotations_by_id


def jaccard_coef(set_A, set_B):
    union_len = len(set_A.union(set_B))
    if union_len == 0:
        return np.nan
    else:
        return len(set_A.intersection(set_B)) / union_len


def make_set_of_annotations_by_type(list_of_annotations, annotation_type):
    return set([
        annotation
        for annotation in list_of_annotations
        if annotation.annot_type == annotation_type
    ])


def compare_two_annotators(first_annotations, second_annotations, annotation_type=None):
    if annotation_type == 'ALL':
        first_set = set(first_annotations)
        second_set = set(second_annotations)
    else:
        first_set = make_set_of_annotations_by_type(first_annotations, annotation_type)
        second_set = make_set_of_annotations_by_type(second_annotations, annotation_type)
    return jaccard_coef(first_set, second_set)

if __name__=='__main__':
    result_output = open('annotators_output.txt', 'w')
    lines = read_file(path)
    suitable_indices, num_annotations = extract_suitable_sentence_line_nums(lines)
    all_annotations_by_id = generate_annotations(lines, suitable_indices, num_annotations)

    for annot_type, annot_category in annot_types.items():
        for first_annontator_id in range(5):
            for second_annotator_id in range(first_annontator_id+1, 5):
                metrics = []
                metric = compare_two_annotators(
                    first_annotations=all_annotations_by_id[first_annontator_id],
                    second_annotations=all_annotations_by_id[second_annotator_id],
                    annotation_type=annot_type,
                )
                metrics.append(metric)
                if annot_type == 'ALL':
                    print (
                        f'Jaccard coef for {first_annontator_id} and {second_annotator_id} is {metric:0.3f}',
                        file=result_output)
        print(f'For error category "{annot_category}" mean Jaccard coef is {np.mean(metrics)}', file=result_output)
    result_output.close()


