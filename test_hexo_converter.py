from unittest import TestCase

from HexoConverter import HexoConverter, insert_new_line_for_math, convert_wiki_markdown_to_markdown_link


class TestConverter(TestCase):
    def setUp(self) -> None:
        self.home = "/Users/sunwu/Documents/SW-KnowledgeBase-Backup"
        self.target = "/Users/sunwu/SW-Research/hexo-websit"
        self.c = HexoConverter(home=self.home, target=self.target)

    def test_convert(self):
        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_md_formatter("""---
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
        tag = c._get_md_formatter("""---
        title: Tensor 实验
        tags: public
        linter-yaml-title-alias: Tensor 实验
        date modified: 2022-11-10 10:57:37 
        date created: 2022-11-09 20:12:55 
        aliases:
          - Tensor 实验
        ---""")
        print(tag)
        assert c._is_shared_md(tag) is True

        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_md_formatter("""---
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
        assert c._is_shared_md(tag) is True

        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_md_formatter("""---
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
        assert c._is_shared_md(tag) is False

    def test_share(self):
        tag = self.c._get_md_formatter("""---
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
        assert self.c._is_shared_md(tag) is True

    def test_markdown(self):
        c = HexoConverter(home=self.home, target=self.target, callbacks=[insert_new_line_for_math])
        c.parse_markdown()

    def test_wikilink_convert(self):
        assert self.c._convert_wiki_images("![[b.pdf]]") == '![b.pdf](/images/b.pdf)'
        assert self.c._convert_wiki_images("![[b.png|300]]") == '![b.png](/images/b.png)'
        assert self.c._convert_wiki_images("![[b.png]]") == '![b.png](/images/b.png)'
        assert self.c._convert_wiki_images("![[a]]") == '![[a]]'

    def test_math_converter(self):
        assert "\n$$math$$\n" == insert_new_line_for_math("$$math$$")
        assert '`$$math$$`' == insert_new_line_for_math("`$$math$$`")

    def test_link_convert(self):
        assert convert_wiki_markdown_to_markdown_link("$[[aa]]$") == '$[[aa]]$'
        assert convert_wiki_markdown_to_markdown_link("[[aa]]$") == '[[aa]]$'
        assert convert_wiki_markdown_to_markdown_link("![[aa]]") == '![[aa]]'
        assert convert_wiki_markdown_to_markdown_link("[[aa]]") == '[aa](aa.html)'
        assert convert_wiki_markdown_to_markdown_link("[[aa.pdf]]") == '[aa.pdf](aa.pdf)'
