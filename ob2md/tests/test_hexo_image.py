from unittest import TestCase

from ob2md.src.HexoConverter import HexoConverter


class TestImg(TestCase):
    def setUp(self) -> None:
        self.home = "/Users/sunwu/SW-KnowledgeBase"
        self.target = "/Users/sunwu/SW-Research/hexo-websit"
        self.c = HexoConverter(home=self.home, target=self.target)

    def test_wikilink_convert(self):
        # All linke like ![[]]
        c = HexoConverter(home=self.home, target=self.target)
        assert self.c._convert_wiki_images(
            "![[b.png|300]], ![[a.jpeg]] \n ![[cc.jpg]] \n![[cc.gif]]") == """![b.png](/images/84120802dfb025b465d51f522f235d9cf34e7dec.png), ![a.jpeg](/images/c77fcd8c158b032d89d725726140833a1b6219ee.jpeg) 
 ![cc.jpg](/images/b22b344e46e13c45cd63d815f0be19b2f979856e.jpg) 
![cc.gif](/images/0a342ad487a4f7f6593596dfe1ff85e4e4eddacb.gif)"""
        assert self.c._convert_wiki_images(
            "![[b.png]]") == '![b.png](/images/84120802dfb025b465d51f522f235d9cf34e7dec.png)'
        assert self.c._convert_wiki_images("![[a]]") == '![[a]]'
