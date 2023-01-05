from unittest import TestCase

from ob2md.src.HexoConverter import HexoConverter


class TestConverterExcalidraw(TestCase):
    def setUp(self) -> None:
        self.home = "/Users/sunwu/SW-KnowledgeBase"
        self.target = "/Users/sunwu/SW-Research/hexo-websit"
        self.c = HexoConverter(home=self.home, target=self.target)

    def test_wikilink_convert(self):
        # All linke like ![[]]
        c = HexoConverter(home=self.home, target=self.target)
        pdf_ = "![[Excalidraw/COCA源码分析 2023-01-05 09.37.53.excalidraw]]"
        assert self.c._convert_wiki_excalidraw(
            pdf_) == '![Excalidraw/COCA源码分析 2023-01-05 09.37.53.excalidraw](/images/ff9b6413ac39b2772ebd08fce73ccb7fb34fb335.png)'
