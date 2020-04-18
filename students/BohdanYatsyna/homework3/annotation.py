import re

annotationType = {
    'Vt': {'Description': 'Verb tense',
           'Example': "Medical technology during that time [is → was] not advanced enough to cure him."},
    'Vm': {'Description': 'Verb modal',
           'Example': "Although the problem [would → may] not be serious, people [would → might] still be afraid."},
    'V0': {'Description': 'Missing verb',
           'Example': "However, there are also a great number of people [who → who are] against this technology."},
    'Vform': {'Description': 'Verb form',
              'Example': "A study in 2010 [shown → showed] that patients recover faster when sur- rounded by family members."},
    'SVA': {'Description': 'Subject-verb agreement',
            'Example': "The benefits of disclosing genetic risk information [outweighs → out- weigh] the costs."},
    'ArtOrDet': {'Description': 'Article or determiner',
                 'Example': "It is obvious to see that [internet → the internet] saves people time and also connects people globally."},
    'Nn': {'Description': 'Noun number',
           'Example': "A carrier may consider not having any [child → children] after getting married."},
    'Npos': {'Description': 'Noun possessive',
             'Example': "Someone should tell the [carriers → carrier’s] relatives about the genetic problem."},
    'Pform': {'Description': 'Pronoun form',
              'Example': "A couple should run a few tests to see if [their → they] have any genetic diseases beforehand."},
    'Pref': {'Description': 'Pronoun reference',
             'Example': "It is everyone’s duty to ensure that [he or she → they] undergo regular health checks."},
    'Prep': {'Description': 'Preposition',
             'Example': "This essay will [discuss about → discuss] whether a carrier should tell his relatives or not."},
    'Wci': {'Description': 'Wrong collocation/idiom',
            'Example': "Early examination is [healthy → advisable] and will cast away unwanted doubts."},
    'Wa': {'Description': 'Acronyms',
           'Example': "After [WOWII → World War II], the population of China decreased rapidly."},
    'Wform': {'Description': 'Word form',
              'Example': "The sense of [guilty → guilt] can be more than expected."},
    'Wtone': {'Description': 'Tone (formal/informal)',
              'Example': "[It’s → It is] our family and relatives that bring us up."},
    'Srun': {'Description': 'Run-on sentences, comma splices',
             'Example': "The issue is highly [debatable, a → debatable. A] genetic risk could come from either side of the family."},
    'Smod': {'Description': 'Dangling modifiers',
             'Example': "[Undeniable, → It is undeniable that] it becomes addictive when we spend more time socializing virtually."},
    'Spar': {'Description': 'Parallelism',
             'Example': "We must pay attention to this information and [assisting → assist] those who are at risk."},
    'Sfrag': {'Description': 'Sentence fragment',
              'Example': "However, from the ethical point of view."},
    'Ssub': {'Description': 'Subordinate clause',
             'Example': "This is an issue [needs → that needs] to be addressed."},
    'WOinc': {'Description': 'Incorrect word order',
              'Example': "[Someone having what kind of disease → What kind of disease someone has] is a matter of their own privacy."},
    'WOadv': {'Description': 'Incorrect adjective/ adverb order',
              'Example': "In conclusion, [personally I → I personally] feel that it is important to tell one’s family members."},
    'Trans': {'Description': 'Linking words/phrases',
              'Example': "It is sometimes hard to find [out → out if] one has this disease."},
    'Mec': {'Description': 'Spelling, punctuation,capitalization, etc.',
            'Example': "This knowledge [maybe relavant → may be relevant] to them."},
    'Rloc−': {'Description': 'Redundancy',
              'Example': "It is up to the [patient’s own choice → patient] to disclose information."},
    'Cit': {'Description': 'Citation',
            'Example': "Poor citation practice."},
    'Others': {'Description': 'Other errors',
               'Example': "An error that does not fit into any other category but can still be corrected."},
    'Um': {'Description': 'Unclear meaning',
           'Example': "Genetic disease has a close relationship with the born gene. (i.e., no cor- rection possible without further clarification.)"},
}


class Annotation:
    re_annotation_didgits = re.compile('(?!=\|{1,})\d+')
    re_annotation_values = re.compile('\|([^|]*)(?!$)')

    def __init__(self, annot_str):
        didgits = self.re_annotation_didgits.findall(annot_str)
        values = self.re_annotation_values.findall(annot_str)

        self.startPos = int(didgits[0])
        self.endPos = int(didgits[1])
        self.annotatorNumber = int(didgits[2])
        self.type = values[2]
        self.correction = values[5]

    def __eq__(self, other):
        return self.startPos == other.startPos and self.endPos == other.endPos and self.type == other.type and self.correction == other.correction

    def __repr__(self):
        return {'annotatorNumber': self.annotatorNumber, 'startPos': self.startPos, 'endPos': self.endPos,
                'type': self.type, 'correction': self.correction}

    def __str__(self):
        return 'Annotation(annotatorNumber=' + str(self.annotatorNumber) + ', startPos=' + str(
            self.startPos) + ', endPos=' + str(
            self.endPos) + ', type=' + self.type + ', correction=' + self.correction + ')'


class AnnotatedSentence:
    def __init__(self, str):
        self.sentence = str
        self.sentenceNumber = -1
        self.annotations = []
