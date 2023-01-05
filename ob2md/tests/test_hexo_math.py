from unittest import TestCase

from ob2md.src.HexoConverter import HexoConverter, insert_new_line_for_math, \
    get_wiki_link_abs_file, post_process_anchor


class TestConverterMath(TestCase):
    def setUp(self) -> None:
        self.home = "/Users/sunwu/SW-KnowledgeBase"
        self.target = "/Users/sunwu/SW-Research/hexo-websit"
        self.c = HexoConverter(home=self.home, target=self.target)

    def test_math_converter(self):
        assert "\n$$math$$\n" == insert_new_line_for_math("$$math$$")
        assert '`$$math$$`' == insert_new_line_for_math("`$$math$$`")

    def test_link_convert(self):
        assert self.c._convert_wiki_anchor("a.md", "$[[aa]]$") == '$[[aa]]$'
        assert self.c._convert_wiki_anchor("a.md", "[[aa]]$") == '[[aa]]$'
        assert self.c._convert_wiki_anchor("a.md", "![[aa]]") == '![[aa]]'
