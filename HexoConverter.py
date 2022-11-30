import os
import pprint
import re
import shutil
import sys

import yaml
from yaml import Loader

from util_log import get_logger

log = get_logger()

"""
-  Only convert for specified tags, default containing tag: public
-  Remove all space ' '. 
- 支持 pdf.jpeg 
"""


def insert_new_line_for_math(content):
    """
    Insert \n before $$ and after

    assert "\n$$math$$\n" == insert_new_line_for_math("$$math$$")
    assert '`$$math$$`' == insert_new_line_for_math("`$$math$$`")

    Parameters
    ----------
    content :

    Returns
    -------

    """
    links = re.findall("(`?)(\$\$.*?\$\$)", content, re.S)
    for prex, link in links:
        if prex:
            continue
        content = content.replace(link, f"\n{link}\n")
    return content


def convert_wiki_markdown_to_markdown_link(content):
    """
    #  convert [[xx]] to link, which not start with ! and end with $
    Parameters
    ----------
    content :

    Returns
    -------

    """
    links = re.findall("(?<!!)\[\[(.*?)\]\](?!\$)", content)
    for source_link in links:
        link_remove_jinhao: str = source_link.split("#")[0]
        # source static file
        link_remove_jinhao_and_space = link_remove_jinhao.split('/')[-1].replace(" ", "")
        wiki_link_reg = f"[[{source_link}]]"

        _ext = os.path.splitext(link_remove_jinhao_and_space)[-1]
        if _ext == "":
            target_line = f"[{link_remove_jinhao_and_space}]({link_remove_jinhao_and_space}.html)"
        else:
            target_line = f"[{link_remove_jinhao_and_space}]({link_remove_jinhao_and_space})"
        content = content.replace(wiki_link_reg, target_line)
    return content


def convert_obsidian_toc_to_hexo_toc(content, hexo_toc_tag="@[toc]"):
    """

    """
    tocs = re.findall("(```toc.*?```)", content, re.S)
    for toc in tocs:
        # content = content.replace(toc, f"## Table of Contents \n{hexo_toc_tag}\n\n---\n\n")
        # content = content.replace(toc, f"## Table of Contents \n\n @[toc] \n\n ---\n")
        content = content.replace(toc, f"\n# ✨Table of contents✨ \n\n @[toc] \n\n ---\n")
    return content


# https://www.markdownguide.org/basic-syntax/

# /Users/sunwu/SW-Research/typecho/usr/637c79e786d72.db
class HexoConverter:
    md_exts = ['.md']

    def __init__(self, home, target, share_tag="public", target_md_dir="source/_posts",
                 target_assets_dir="source/images", statics_ext=['.png', '.gif', 'jpg', 'jpeg', '.pdf', '.excalidraw']
                 , callbacks=[]):
        """
        Parameters
        ----------
        home : str
            The obsidian vault, e.g. /Users/sunwu/SW-KnowledgeBase
        target : str
            The hexo _home, e.g., /Users/sunwu/Documents/hexo-websit
        share_tag   : str
            The share tag for md, e.g., public
        source_md_dir   : str
            The relative path of markdown directory for hexo, default source/_posts
        callbacks:list
            A list of callback function to convert markdown content.

            .. code-block::

                for fun in self._callbacks:
                content = fun(content)

        """
        self._home = home
        self._share_tag = share_tag
        self._target = target
        self._statics_ext = statics_ext
        self._callbacks = callbacks
        assert isinstance(target_assets_dir, str), "target_assets_dir must be a string"
        assert target_assets_dir.find("\\") == -1, "target_assets_dir cannot contain \\"
        assert not target_md_dir.startswith("/"), "source_md_dir cannot start with /"
        self._target_md_dir = target_md_dir

        assert not target_assets_dir.startswith("/"), "target_assets_dir cannot start with /"
        self._target_assets_dir = target_assets_dir
        # All files with absolute path

        # The file with relative path to self.home
        self._relative_all = []
        self._get_whole_files(self._home)
        print(f"Found {len(self._relative_all)} files")

    def get_all_files(self):
        self._get_whole_files(self._home)
        log.info(f"Found {len(self._relative_all)} files")
        return self._relative_all

    def _get_whole_files(self, files_directory):
        """
        Get all file in the directory to list.

        Parameters
        ----------
        files_directory : str
            The _home

        Returns
        -------

        """
        for file in os.listdir(files_directory):
            _file = os.path.join(files_directory, file)
            if os.path.isfile(_file):
                self._relative_all.append(_file.replace(self._home, "")[1:])
            else:
                self._get_whole_files(_file)

    def get_file_ext(self, file):
        return os.path.splitext(file)[-1]

    def parse_markdown(self):
        """
        1. Ignore tags: private
        Returns
        -------

        """
        for file in self._relative_all:
            _ext = self.get_file_ext(file)
            if _ext in self.md_exts:
                with open(os.path.join(self._home, file), 'r') as f:
                    content = f.read()
                    yaml_formatter = self._get_md_formatter(content)
                    if self._is_shared_md(yaml_formatter):
                        log.info(f"Get shared md: {file}")
                        self._write_md(file, content, yaml_formatter)
                    else:
                        log.debug(f"Pass for not shared md: {file}")

    def _is_ignore_file(self, content):
        tag = re.search("---(.*)", content).group(1)
        return

    def _is_shared_md(self, yaml_formatter: dict):
        """
        Check if the content is a public

        Parameters
        ----------
        yaml_formatter :

        Returns
        -------

        """
        try:
            if not isinstance(yaml_formatter, dict):
                return False
            tags = yaml_formatter.get('tags')
            if isinstance(tags, str):
                if tags.lower() == self._share_tag.lower():
                    return True
            if isinstance(tags, list):
                tags = [str(tag).lower() if tag is not None else self._share_tag for tag in tags]
                return self._share_tag in tags
            return False
        except Exception as e:
            raise e

    def _get_md_formatter(self, content):
        yaml_for = re.search("^---(.*?)---", content, re.S)
        if yaml_for is not None:
            yaml_header = yaml_for.group(1)
            try:
                return yaml.load(yaml_header, Loader=Loader)
            except Exception as e:
                log.info(f"==============YAML HEADER======================"
                         f"\n{pprint.pformat(yaml_header)}")
                raise e
        else:
            return dict()

    def _write_md(self, file, content, yaml_formatter):
        content = self._convert_wiki_images(content)
        for fun in self._callbacks:
            content = fun(content)

        if content is None:
            log.warning(F"Content of  {file} is None    ")
            return
        else:
            target_file_path = os.path.join(self._target, self._target_md_dir, os.path.basename(file)) \
                .replace(" ", "")
            if not os.path.exists(os.path.dirname(target_file_path)):
                os.makedirs(os.path.dirname(target_file_path))
            with open(target_file_path, "w") as f:
                log.info(f"Writing content to {target_file_path}")
                f.write(content)

    def _convert_wiki_images(self, content):
        """
        Convert wiki links images to markdown images

        assert self.c._convert_wiki_images("![[b.png|300]]", use_uuid=False) == '![b.png](/images/b.png)'
        assert self.c._convert_wiki_images("![[a]]", use_uuid=False) == '![[a]]'
        assert self.c._convert_wiki_images("![[b.png]]", use_uuid=False) == '![b.png](/images/b.png)'

        Parameters
        ----------
        content :

        Returns
        -------

        """
        links = re.findall("!\[\[(.*?)\]\]", content)
        for source_link in links:
            target_link = source_link.split("|")[0]
            ext = os.path.splitext(target_link)[-1]
            if ext in self._statics_ext:
                # source static file
                source = os.path.join(self._home, target_link)

                # target file
                target = os.path.join(self._target, self._target_assets_dir,
                                      target_link.replace("/", "_").replace(" ", "_"))
                if os.path.exists(source) and not os.path.exists(target):
                    if not os.path.exists(os.path.dirname(target)):
                        os.makedirs(os.path.dirname(target))
                    log.info(f"Copy {source} to {target}")
                    shutil.copyfile(source, target)

                # Change the link content
                wiki_link_reg = f"![[{source_link}]]"
                target_line = f"![{os.path.basename(target)}]({target.split('|')[0].replace(self._target, '').replace(self._target_assets_dir.split('/')[0], '')[1:]})"
                content = content.replace(wiki_link_reg, target_line)

        return content


if __name__ == '__main__':
    HexoConverter(home=str(sys.argv[1]).strip(),
                  target=str(sys.argv[2]).strip(),
                  callbacks=[insert_new_line_for_math,
                             convert_obsidian_toc_to_hexo_toc,
                             convert_wiki_markdown_to_markdown_link]
                  ).parse_markdown()
