from unittest import TestCase

from HexoConverter import HexoConverter, insert_new_line_for_math, \
    get_wiki_link_abs_file


class TestConverter(TestCase):
    def setUp(self) -> None:
        self.home = "/Users/sunwu/SW-KnowledgeBase"
        self.target = "/Users/sunwu/SW-Research/hexo-websit"
        self.c = HexoConverter(home=self.home, target=self.target)

    def test_convert(self):
        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_markdown_yaml_formatter("""---
title: Tensor 实验
tags: 
  - private
linter-yaml-title-alias: Tensor 实验
date modified: 2022-11-10 10:57:37 
date created: 2022-11-09 20:12:55 
aliases:
  - Tensor 实验
---""")
        print(tag)
        assert "private" in tag.get('tags')

    def test_yaml2(self):
        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_markdown_yaml_formatter("""---
        title: Tensor 实验
        tags: public
        linter-yaml-title-alias: Tensor 实验
        date modified: 2022-11-10 10:57:37 
        date created: 2022-11-09 20:12:55 
        aliases:
          - Tensor 实验
        ---""")
        print(tag)
        assert c._is_share_formatter(tag) is True

        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_markdown_yaml_formatter("""---
        title: Tensor 实验
        tags: 
          - public
        linter-yaml-title-alias: Tensor 实验
        date modified: 2022-11-10 10:57:37 
        date created: 2022-11-09 20:12:55 
        aliases:
          - Tensor 实验
        ---""")
        print(tag)
        assert c._is_share_formatter(tag) is True

        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_markdown_yaml_formatter("""---
        title: Tensor 实验
        tags: 
          - s2
        linter-yaml-title-alias: Tensor 实验
        date modified: 2022-11-10 10:57:37 
        date created: 2022-11-09 20:12:55 
        aliases:
          - Tensor 实验
        ---""")
        print(tag)
        assert c._is_share_formatter(tag) is False

    def test_share(self):
        tag = self.c._get_markdown_yaml_formatter("""---
title: (2022)贵州大学商业数据分析课程看板
tags:
- 贵州大学商业数据分析
- public
date modified: 2022-11-22 13:22:29 
date created: 2022-11-14 15:13:57 
aliases:
  - (2022)贵州大学商业数据分析课程看板
           ---""")
        print(tag)
        assert self.c._is_share_formatter(tag) is True

    def test_markdown(self):
        c = HexoConverter(home=self.home, target=self.target, callbacks=[insert_new_line_for_math])
        c.parse_markdown()

    def test_wikilink_convert(self):
        # All linke like ![[]]
        c = HexoConverter(home=self.home, target=self.target)
        target = self.c._convert_wiki_images("![[b.pdf]]")
        assert target == "<embed src='/images/0.pdf' width='100%' height='750' type='application/pdf'>"

        target = self.c._convert_wiki_images(" ![[static/attachment/second_result.pdf]]")
        assert target == " <embed src='/images/1.pdf' width='100%' height='750' type='application/pdf'>"

        assert self.c._convert_wiki_images("![[b.png|300]]") == '![b.png](/images/2.png)'
        assert self.c._convert_wiki_images("![[b.png]]") == '![b.png](/images/3.png)'
        assert self.c._convert_wiki_images("![[a]]") == '![[a]]'

    def test_math_converter(self):
        assert "\n$$math$$\n" == insert_new_line_for_math("$$math$$")
        assert '`$$math$$`' == insert_new_line_for_math("`$$math$$`")

    def test_link_convert(self):
        # contain space in fine name
        assert self.c._convert_wiki_links("a.md", "兼容 [[Docs/2022-11-25实验结果|上次实验结果]]") \
               == "兼容 <a href='{% post_path 2022-11-25实验结果 %}'>2022-11-25实验结果</a>"
        assert self.c._convert_wiki_links("a.md", "兼容 [[Docs/2022-11-25实验结果#上次实验结果]]") \
               == "兼容 <a href='{% post_path 2022-11-25实验结果 %}'>2022-11-25实验结果</a>"

        # all link like  [[]]
        assert self.c._convert_wiki_links("a.md", "兼容 [[Docs/2022-11-25 实验结果|上次实验结果]]") \
               == "兼容 <a href='{% post_path 2022-11-25 实验结果 %}'>2022-11-25 实验结果</a>"
        assert self.c._convert_wiki_links("a.md", "兼容 [[Docs/2022-11-25 实验结果#上次实验结果]]") \
               == "兼容 <a href='{% post_path 2022-11-25 实验结果 %}'>2022-11-25 实验结果</a>"

        assert self.c._convert_wiki_links("a.md", "$[[aa]]$") == '$[[aa]]$'
        assert self.c._convert_wiki_links("a.md", "[[aa]]$") == '[[aa]]$'
        assert self.c._convert_wiki_links("a.md", "![[aa]]") == '![[aa]]'
        assert self.c._convert_wiki_links("a.md", "[[aa]]") == "<a href='{% post_path aa %}'>aa</a>"

    def test_compatibility(self):
        # todo:  兼容 [[Docs/2022-11-25 实验结果|上次实验结果]]
        # todo:  兼容 ![[static/attachment/Pasted image 20221201110235.png|400]]
        pass

    def test_link_file(self):
        assert get_wiki_link_abs_file("aaaa.pdf#111") == "aaaa.pdf"
        assert get_wiki_link_abs_file("abc/aaaa.pdf#111") == "abc/aaaa.pdf"
        assert get_wiki_link_abs_file("abc/aaaa.pdf|111") == "abc/aaaa.pdf"
