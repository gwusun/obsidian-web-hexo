from unittest import TestCase

from ob2md.src.HexoConverter import HexoConverter


class TestConverterPdf(TestCase):
    def setUp(self) -> None:
        self.home = "/Users/sunwu/SW-KnowledgeBase"
        self.target = "/Users/sunwu/SW-Research/hexo-websit"
        self.c = HexoConverter(home=self.home, target=self.target)

    def test_wikilink_convert(self):
        # All linke like ![[]]
        c = HexoConverter(home=self.home, target=self.target)
        pdf_ = "![[a.pdf|300]], ![[b.pdf]] "
        print(self.c._convert_wiki_pdf(pdf_))
        assert self.c._convert_wiki_pdf(
            pdf_) == "<embed src='/images/31ca9bd8bdb4574dbab448b2b4a3ad04ae365bda.pdf' width='100%' height='750' type='application/pdf'>, <embed src='/images/0fe9507aab79d2453ec206a070009d790d53bde6.pdf' width='100%' height='750' type='application/pdf'> "
