from unittest import TestCase

from ob2md.src.HexoConverter import HexoConverter


class TestConverterYaml(TestCase):
    def setUp(self) -> None:
        self.home = "/Users/sunwu/SW-KnowledgeBase"
        self.target = "/Users/sunwu/SW-Research/hexo-websit"
        self.c = HexoConverter(home=self.home, target=self.target)

    def test_yaml01(self):
        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_markdown_yaml_formatter("""---
title: Tensor 实验
share: false
tags: 
  - private
linter-yaml-title-alias: Tensor 实验
date modified: 2022-11-10 10:57:37 
date created: 2022-11-09 20:12:55 
aliases:
  - Tensor 实验
---""")
        print(tag)
        assert tag.get('share') is False

    def test_yaml02(self):
        c = HexoConverter(home=self.home, target=self.target)
        tag = c._get_markdown_yaml_formatter("""---
        title: Tensor 实验
        tags: public
        share: true
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
        share: true
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
        share: false
        linter-yaml-title-alias: Tensor 实验
        date modified: 2022-11-10 10:57:37 
        date created: 2022-11-09 20:12:55 
        aliases:
          - Tensor 实验
        ---""")
        print(tag)
        assert c._is_share_formatter(tag) is False

    def test_yaml_share(self):
        tag = self.c._get_markdown_yaml_formatter("""---
title: (2022)贵州大学商业数据分析课程看板
share: true
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
