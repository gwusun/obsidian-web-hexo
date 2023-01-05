from unittest import TestCase

from ob2md.src.HexoConverter import HexoConverter, insert_new_line_for_math, \
    get_wiki_link_abs_file, post_process_anchor


class TestConverterWiki(TestCase):
    def setUp(self) -> None:
        self.home = "/Users/sunwu/SW-KnowledgeBase"
        self.target = "/Users/sunwu/SW-Research/hexo-websit"
        self.c = HexoConverter(home=self.home, target=self.target)

    def test_markdown_anchor(self):
        text = "兼容 [[Docs/2022-11-25实验结果#上次实验结果]] 兼容 ![[Docs/2022-11-25实验结果#上次实验结果]] [[#上传]]"
        assert self.c._convert_wiki_anchor("a.md", text) \
               == "兼容 <a href='{% post_path 2022-11-25实验结果 %}#上次实验结果'>2022-11-25实验结果#上次实验结果</a> 兼容 !<a href='{% post_path 2022-11-25实验结果 %}#上次实验结果'>2022-11-25实验结果#上次实验结果</a> <a href='#上传'>#上传</a>"

        assert get_wiki_link_abs_file("aaaa.pdf#111") == "aaaa.pdf"
        assert get_wiki_link_abs_file("abc/aaaa.pdf#111") == "abc/aaaa.pdf"
        assert get_wiki_link_abs_file("abc/aaaa.pdf|111") == "abc/aaaa.pdf"

    def test_pure_link(self):
        test = "[[aa]] 兼容 [[Docs/2022-11-25实验结果|上次实验结果]]"
        assert self.c._convert_wiki_link("a.md",
                                         test) == "<a href='{% post_path aa %}'>aa</a> 兼容 <a href='{% post_path 2022-11-25实验结果 %}'>2022-11-25实验结果</a>"

    def test_anchor_post_process(self):
        assert post_process_anchor("#上次实验结果") == "#上次实验结果"
        self.assertEqual(post_process_anchor("#上次 实验结果"), "#上次-实验结果")
        self.assertEqual(post_process_anchor("#上次 实验 结果"), "#上次-实验-结果")
        self.assertEqual(post_process_anchor("#上次　实验结果"), "#上次-实验结果")
