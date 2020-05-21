from unittest import TestCase
from students.BohdanYatsyna.homework3.annotation import Annotation
from students.BohdanYatsyna.homework3.annotation import annotationType


class TestAnnotation(TestCase):
    def test_correct_parsing(self):
        test_string = "A 5 6|||Wci|||establishing|||REQUIRED|||-NONE-|||0"
        ann = Annotation(test_string)
        self.assertTrue(ann.annotatorNumber == 0, "Annotator number incorrect!!")
        self.assertTrue(ann.startPos == 5, "Start position is incorrect!!")
        self.assertTrue(ann.endPos == 6, "End position is incorrect!!!")
        self.assertTrue(ann.type == 'Wci', "Type is incorrect!!!")
        self.assertTrue(ann.correction == 'establishing', "Type is incorrect!!!")


    def test_eq_function(self):
        annStr1 = "A 3 4|||Mec|||diagnosed|||REQUIRED|||-NONE-|||0"
        annStr2 = "A 3 4|||Mec|||diagnosed|||REQUIRED|||-NONE-|||2"
        annStr3 = "A 3 4|||Mec|||diag|||REQUIRED|||-NONE-|||2"

        self.assertTrue(Annotation(annStr1) == Annotation(annStr2))
        self.assertFalse(Annotation(annStr1) == Annotation(annStr3))
