from unittest import TestCase
from students.BohdanYatsyna.homework6.preprocess1 import generate_sent_string
from students.BohdanYatsyna.homework6.preprocess1 import generate_sent_params
from students.BohdanYatsyna.homework6.preprocess1 import generate_dataset_string

class Test(TestCase):
    def test_generate_sent_params(self):
        sent_num = 4
        lowercases, misses = generate_sent_params(sent_num, debug=True)
        self.assertTrue(misses[-1] == False, "не викинутий символ .!?")
        self.assertTrue(lowercases[0] == False, "Перше слово першого речення чмусь ти ловеркейсиш")
        for i in range(sent_num):
            if lowercases[i] == True:
                self.assertTrue(misses[i-1] == True)

    def test_generate_dataset_string(self):
        sents = [ \
            "Imagine the feeling of being able to offer your opportunity and products to millions of people in North America and other parts of the world from your own home-based niche.", \
            "I am contacting you about a need I have and I believe you are well able to help me.",
            "You will not be able to send or receive new mail until you upgrade your email.", \
            "After few months of this ugly situation and experience a friend of mine that had similar fraud experience years back, advised me on how he was able to get", \
            "Please let me know of you would be able to do this.", \
            "They leave Pleasant Run, generally, ready and able to contribute to society.", \
            "Please if you would be able to use these funds for the Lord's work kindly reply to me.", \
            "Your processor should be able to tell you this information.", \
            "For this event, when you purchase a corporate picnic table, you will be able to bring 16 people.", \
            "What has your support of our campers meant to them and what have they been able to accomplish because you care?", \
            "Since then, she and I have grown very close and I have been able to experience lots of new things.", \
            "We go to movies, dinner, concerts, and other stuff like that, but I have also been able to participate in charity events and fundraiser type things.", \
            "We must be able to reach all youth and families interested in values-based programs.",
            "I would appreciate it very much if you were able to assist/guide me.", \
            "and they might be able to fix it.", \
            "As he turned away from the beach, he saw the last flame of the fire, what used to be so huge he was afraid they wouldn\u2019t be able to put it out, go away forever.", \
            "As he turned away from the beach, he saw the last flame of the fire, what used to be so huge he was afraid they wouldn\u2019t be able to put it out, go away forever.", \
            "Please don\u2019t make me feel any guiltier about not being able to be with you.", \
            "People knew what I could do, yet they thought I wasn\u2019t able to do little things, like walking down a hallway.", \
            "People tried to convince me to go through with all of the things doctors kept trying to fix by telling me &quot;I can't imagine not being able to see.", \
            "Walking would appear as running, when traveling in the mirror realm, that is, if anyone in the real world was able to see them.", \
            "Melody asked &quot;The ability to be able to go into that mirror realm...",
            "Suddenly the lights dim and he is able to fully open his eyes."]

        test_buffer_1 = sents[:3] ## len 3

        generated_features = generate_dataset_string(test_buffer_1, debug=True)
        for tok,lab in zip(generated_features["tokens"],generated_features["labels"]):
            print("{:<5}{}".format (lab,tok))

        self.assertTrue(True)
