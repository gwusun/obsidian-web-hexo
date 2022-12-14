import os
import pprint
import re
import shutil
import sys
import numpy as np
import yaml
from yaml import Loader
import hashlib
from util_log import get_logger

log = get_logger()

"""
- Only convert the .md  specified tags=public
- Randomly generated the image filename by UUID
- 目标文件名中的"空格" 全部被替换为 "-" 
- 


ref:
https://butterfly.js.org


##  excalidraw
COCA源码分析 2022-12-23 14.56.42.excalidraw.png
COCA源码分析 2023-01-05 09.37.53.excalidraw.md
COCA源码分析 2023-01-05 09.37.53.excalidraw.png
COCA源码分析 2023-01-04 09.18.29.excalidraw.md
COCA源码分析 2023-01-04 09.18.29.excalidraw.png
COCA源码分析 2022-12-23 14.56.42.excalidraw.md
"""


def get_str_hash(string):
    """
    Get the hash code of string

    Parameters
    ----------
    string : str
        The input str

    Returns
    -------
    str
        The hash code of the string

    """
    if not isinstance(string, str):
        raise ValueError(f"get_str_hash excepts str, but recept {type(string)}")
    return hashlib.sha1(string.encode("utf8")).hexdigest()


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
    try:
        links = re.findall("(`?)(\$\$.*?\$\$)", content, re.S)
        for prex, link in links:
            if prex:
                continue
            content = content.replace(link, f"\n{link}\n")
        return content
    except Exception as e:
        raise e


def get_wiki_link_abs_file(wiki_link):
    if wiki_link.find("#") > -1:
        # compact  with 'Docs/2022-11-25 实验结果#上次实验结果'
        return wiki_link.split("#")[0]
    elif wiki_link.find("|") > -1:
        return wiki_link.split("|")[0]
    else:
        return wiki_link


def get_wiki_link_file_name(wiki_link: str):
    base_name = get_wiki_link_abs_file(wiki_link).split("/")[-1]
    if wiki_link.find("#") > -1:
        # compact  with 'Docs/2022-11-25 实验结果#上次实验结果'
        return convert_space_to_dash(base_name.split("#")[0])
    elif wiki_link.find("|") > -1:
        return convert_space_to_dash(base_name.split("|")[0])
    else:
        return convert_space_to_dash(base_name)


def get_wiki_link_file_alias(cur_link: str):
    return cur_link.split("|")[-1]


def convert_obsidian_toc_to_hexo_toc(content, hexo_toc_tag="@[toc]"):
    """

    """
    tocs = re.findall("(```toc.*?```)", content, re.S)
    for toc in tocs:
        # content = content.replace(toc, f"## Table of Contents \n{hexo_toc_tag}\n\n---\n\n")
        # content = content.replace(toc, f"## Table of Contents \n\n @[toc] \n\n ---\n")
        # content = content.replace(toc, f"\n# ✨Table of contents✨ \n\n @[toc] \n\n ---\n")
        # content = content.replace(toc, f"\n✨Table of contents✨ \n @[toc] \n")
        content = content.replace(toc, f"")
    return content


# https://www.markdownguide.org/basic-syntax/

# /Users/sunwu/SW-Research/typecho/usr/637c79e786d72.db
def post_process_anchor(source_link):
    """
    Get the anchor text from the source link.

    Examples
    --------

    .. code-block:: python

        assert post_process_anchor("#上次实验结果") == "#上次实验结果"
        self.assertEqual(post_process_anchor("#上次 实验结果"), "#上次-实验结果")
        self.assertEqual(post_process_anchor("#上次 实验 结果"), "#上次-实验-结果")
        self.assertEqual(post_process_anchor("#上次　实验结果"), "#上次-实验结果")


    Parameters
    ----------
    source_link :

    Returns
    -------

    """
    _anchor = re.search("(#.*)", source_link)
    if _anchor is None:
        return ""
    else:
        _anchor_text = _anchor.group(0)
        return convert_space_to_dash(_anchor_text)


def convert_space_to_dash(text):
    """
    Converts a space to -

    Parameters
    ----------
    text :

    Returns
    -------

    """
    return re.sub("\\s", '-', text)


class HexoConverter:
    md_exts = ['.md']

    def __init__(self, home, target, share_tag="share", target_md_dir="source/_posts",
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
        self._file_names = list(np.linspace(0, 999999, 999999, dtype=int))
        self._relative_all = []

        # _documents containing the yaml formatter and the content of a .md
        self._documents = {}
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
            if file.startswith("."):
                continue
            _file = os.path.join(files_directory, file)
            if os.path.isfile(_file):
                # is file, append it
                self._relative_all.append(_file.replace(self._home, "")[1:])
            else:
                # is directory,reclusive it.
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
            self._convert_one_markdown(file)

    def _is_ignore_file(self, content):
        tag = re.search("---(.*)", content).group(1)
        return

    def _is_shared_markdown_file(self, file):
        """
        Check if the content is a public

        Parameters
        ----------
        yaml_formatter :

        Returns
        -------

        """
        documents = self._extract_markdown_formatter_and_content(file)
        if documents is None:
            return False

        yaml_formatter = documents['formatter']
        try:
            return self._is_share_formatter(yaml_formatter)
        except Exception as e:
            raise e

    def _is_share_formatter(self, yaml_formatter):
        """
        Return True if the yaml formatter contain  `share: true` , otherwise false.
        The following examples return False:

        .. code-block::

            'share: flase'
            'share: `
            'share: False'
            'share: xxx `

        Parameters
        ----------
        yaml_formatter :

        Returns
        -------

        """
        if not isinstance(yaml_formatter, dict):
            return False
        share_value = yaml_formatter.get(self._share_tag)
        if share_value is None:
            return False
        if isinstance(share_value, str):
            return False

        if isinstance(share_value, bool):
            return share_value == True
        else:
            raise ValueError(f"share in the yaml formatter must be single value. received {share_value}")
            return False
        # if isinstance(share_value, list):
        # share_value = [str(tag).lower() if tag is not None else self._share_tag for tag in share_value]
        # return self._share_tag in share_value

    def _get_markdown_yaml_formatter(self, content):
        """
        Get the yaml formatter of the markdown.

        Parameters
        ----------
        content :

        Returns
        -------

        """
        yaml_for = re.match("^---(.*?)---", content, re.S)
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

    def _convert_wiki_anchor(self, file, content) -> str:
        """
        #  convert [[xx]] to link, which not start with ! and end with $
        #  [[Docs/2022-11-25 实验结果|上次实验结果]]

        #  Convert to : {% post_link a.md 点击这里查看这篇文章 %}
        Parameters
        ----------
        content :

        Returns
        -------

        """

        links = re.findall("(?<!!)(\[\[((.*?)?(#.*?)?)\]\])(?!\$)", content)
        for link in links:
            # ('[[Docs/2022-11-25实验结果#上次实验结果]]', 'Docs/2022-11-25实验结果#上次实验结果', 'Docs/2022-11-25实验结果', '#上次实验结果')
            source_link = link[2]
            link_file = self._get_file_from_wiki_link(source_link)
            source_file = self._get_file_from_wiki_link(link_file)
            if link_file is None:
                log.info(f"link_file in {source_link} is None")
                continue
            else:
                # if the file contain public tag and not convert done,  convert it.
                if self._is_shared_markdown_file(source_file) and not self._is_file_convert_done(source_file):
                    if not link_file == file:
                        # The  file is not  link itself,  recursively convert file.
                        # If link_file == file, means link itself, cant to recursive.
                        self._convert_one_markdown(link_file)

                if link[2] == '':
                    _anchor = post_process_anchor(link[1])
                    target_link = f"<a href='{_anchor}'>{_anchor}</a>"
                    content = content.replace(link[0], target_link)
                else:
                    # target: f"<a href='{{% post_path {wiki_link_file_name} %}}'>{wiki_link_file_name}</a>"
                    wiki_link_file_name = get_wiki_link_file_name(source_link)
                    if wiki_link_file_name == "" or wiki_link_file_name is None:
                        raise RuntimeError("wiki_link_file_name cant be empty. ")

                    _anchor = post_process_anchor(link[3])
                    target_link = f"<a href='{{% post_path {wiki_link_file_name} %}}{_anchor}'>{wiki_link_file_name}{_anchor}</a>"
                    content = content.replace(link[0], target_link)

        assert content is not None
        return content

    def _convert_wiki_link(self, file, content) -> str:
        """
        #  convert [[xx]] to link, which not start with ! and end with $
        #  [[Docs/2022-11-25 实验结果|上次实验结果]]

        #  Convert to : {% post_link a.md 点击这里查看这篇文章 %}
        Parameters
        ----------
        content :

        Returns
        -------

        """

        links = re.findall("(?<!!)(\[\[(([^#]*?)?)\]\])(?!\$)", content)
        for link in links:
            # ('[[aa]]', 'aa', 'aa')
            source_link = link[1]
            link_file = self._get_file_from_wiki_link(source_link)
            source_file = self._get_file_from_wiki_link(link_file)
            if link_file is None:
                log.info(f"link_file in {source_link} is None")
                continue
            else:
                # if the file contain public tag and not convert done,  convert it.
                if self._is_shared_markdown_file(source_file) and not self._is_file_convert_done(source_file):
                    if not link_file == file:
                        # The  file is not  link itself,  recursively convert file.
                        # If link_file == file, means link itself, cant to recursive.
                        self._convert_one_markdown(link_file)

                # target: f"<a href='{{% post_path {wiki_link_file_name} %}}'>{wiki_link_file_name}</a>"
                wiki_link_file_name = get_wiki_link_file_name(source_link)
                if wiki_link_file_name == "" or wiki_link_file_name is None:
                    raise RuntimeError("wiki_link_file_name cant be empty. ")
                target_link = f"<a href='{{% post_path {wiki_link_file_name} %}}'>{wiki_link_file_name}</a>"
                content = content.replace(link[0], target_link)

        assert content is not None
        return content

    def _convert_one_markdown(self, file):
        # Not markdown file, return
        if not self._is_markdown_file(file):
            return

        # Not a share file, return
        if not self._is_shared_markdown_file(file):
            return

        # Content is None, return
        content = self._get_file_content(file)
        if content is None:
            return
        content = self._convert_wiki_images(content)
        assert content is not None
        content = self._convert_wiki_pdf(content)
        assert content is not None
        content = self._convert_wiki_excalidraw(content)
        assert content is not None
        content = self._convert_wiki_link(file, content)
        assert content is not None
        content = self._convert_wiki_anchor(file, content)
        assert content is not None

        for fun in self._callbacks:
            content = fun(content)

        if content is None:
            log.warning(F"Content of  {file} is None    ")
            return
        else:
            target_file_path = self._get_target_markdown_filename_from_source_file(file)
            with open(target_file_path, "w") as f:
                log.info(f"Writing [{file}] to [{target_file_path}]")
                f.write(content)

        # Mark the file is done.
        self._set_file_convert_done(file)

    def _is_target_markdown_file_existed(self, file):
        return os.path.exists(self._get_target_markdown_filename_from_source_file(file))

    def _get_target_markdown_filename_from_source_file(self, file):
        if file is None:
            return None
        else:
            base_name = os.path.basename(file)
            base_name = convert_space_to_dash(base_name)
            target_file_path = os.path.join(self._target, self._target_md_dir, base_name)
            if not os.path.exists(os.path.dirname(target_file_path)):
                os.makedirs(os.path.dirname(target_file_path))
            return target_file_path

    def _convert_wiki_pdf(self, content):
        links = re.findall(f"(!\[\[(((.*?)(.pdf))(.*?))\]\])", content, re.IGNORECASE)
        for link in links:
            # ('![[a.pdf|300]]', 'a.pdf|300', 'a.pdf', 'a', '.pdf', '|300')
            source_link = link[2]
            origin_file_name = get_wiki_link_abs_file(source_link)
            # '/Users/sunwu/SW-KnowledgeBase/static/attachment/second_result.pdf'
            source_abs_path = os.path.join(self._home, origin_file_name)
            # '/Users/sunwu/SW-Research/hexo-websit/source/images/_static_attachment_second_result.pdf'

            # <embed src="/images/static_attachment_second_result.pdf" width="100%" height="750" type="application/pdf">
            target_relative_link = self.copy_static_file(source_abs_path)
            target_line = f"<embed src='{target_relative_link}' width='100%' height='750' type='application/pdf'>"
            content = content.replace(link[0], target_line)
        return content

    def _convert_wiki_excalidraw(self, content):
        links = re.findall(f"(!\[\[(((.*?)(.excalidraw))(.*?))\]\])", content, re.IGNORECASE)
        for link in links:
            # ('![[a.pdf|300]]', 'a.pdf|300', 'a.pdf', 'a', '.pdf', '|300')
            source_link = link[2]
            origin_file_name = get_wiki_link_abs_file(source_link)
            # '/Users/sunwu/SW-KnowledgeBase/static/attachment/second_result.pdf'
            source_abs_path = os.path.join(self._home, origin_file_name)
            source_abs_path_png = source_abs_path + ".png"
            target_relative_link = self.copy_static_file(source_abs_path_png)
            target_line = f"![{origin_file_name}]({target_relative_link})"
            content = content.replace(link[0], target_line)
        return content

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
        # Isaac(?=Asimov)
        links = re.findall(f"(!\[\[((.*?)(.png|.jpg|.svg|.jpeg|.gif)(.*?))\]\])", content, re.IGNORECASE)
        for link in links:
            # [('![[b.png|300]]', 'b.png|300', 'b', '.png', '|300'),
            # ('![[a.jpeg]]', 'a.jpeg', 'a', '.jpeg', ''),
            # ('![[cc.jpg]]', 'cc.jpg', 'cc', '.jpg', '')]
            source_link = link[1]
            origin_file_name = get_wiki_link_abs_file(source_link)
            # '/Users/sunwu/SW-KnowledgeBase/static/attachment/second_result.pdf'
            source_abs_path = os.path.join(self._home, origin_file_name)
            # '/Users/sunwu/SW-Research/hexo-websit/source/images/_static_attachment_second_result.pdf'

            # Change the link content
            target_relative_link = self.copy_static_file(source_abs_path)
            wiki_link_reg = f"![[{source_link}]]"
            target_line = f"![{origin_file_name}]({target_relative_link})"
            content = content.replace(wiki_link_reg, target_line)

        return content

    def copy_static_file(self, source_file):
        """
        拷贝文件到 hexo 静态文件列表中,
        并返回在 md 中可直接引用的文件

        Parameters
        ----------
        source_file :

        Returns
        -------
        str
            在 md 中可直接引用的文件

        """
        target = os.path.join(
            self._target,
            self._target_assets_dir,
            f"{get_str_hash(source_file)}{os.path.splitext(source_file)[-1]}"
        )
        if not os.path.exists(source_file):
            log.warning(f"{source_file} cant be found")

        if os.path.exists(source_file) and not os.path.exists(target):
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            log.info(f"Copy {source_file} to {target}")
            shutil.copyfile(source_file, target)
        if not os.path.exists(target):
            log.warning(f"Cannot copy {source_file} to {target}")
        return target.replace(self._target, "").replace(self._target_assets_dir.split('/')[0], "")[1:]

    def _generate_file_name(self, source_file):
        ext = os.path.splitext(source_file)[-1]
        return str(self._file_names.pop(0)) + ext

    def _extract_markdown_formatter_and_content(self, file):
        """
        Get the markdown content, and it associated yaml-formatter,
        Return a dict:

        .. code-block::

            {
                    'content': content,
                    'formatter': yaml_formatter
            }

        Parameters
        ----------
        file : str
            The file to parse, relative to the self._home

        Returns
        -------

        """
        res = self._documents.get(file)
        if res is not None:
            return res
        else:
            if not self._is_markdown_file(file):
                log.warning(f"{file} is not a markdown file")
                return None

            try:
                with open(os.path.join(self._home, file), 'r') as f:
                    content = f.read()
                    yaml_formatter = self._get_markdown_yaml_formatter(content)
                    equation = re.findall("\$(.+?)\$", content)
                    self._documents[file] = {
                        'content': content,
                        'formatter': yaml_formatter,
                        'equations': equation,
                        'done': False  # is convert done.
                    }
            except Exception as e:
                log.error(e)

            return self._documents.get(file)

    def _get_file_yaml_formatter(self, file):
        """
        Get the markdown yaml_formatter without the content.

        Parameters
        ----------
        file :

        Returns
        -------

        """
        return self._extract_markdown_formatter_and_content(file)['formatter']

    def _get_file_content(self, file):
        """
        Get the .md file content with the yaml_formatter.

        Parameters
        ----------
        file :

        Returns
        -------

        """
        return self._extract_markdown_formatter_and_content(file)['content']

    def _get_file_equations(self, file):
        """
        Get the .md file content with the yaml_formatter.

        Parameters
        ----------
        file :

        Returns
        -------

        """
        return self._extract_markdown_formatter_and_content(file)['content']

    def _get_file_from_wiki_link(self, wiki_link):
        """
        Get the file path form the wiki link.

        Parameters
        ----------
        wiki_link :

        Returns
        -------

        """
        filepath = wiki_link.split("#")[0].split("|")[0]
        ext = os.path.splitext(filepath)[-1]
        if ext == "":
            ret_file = filepath + ".md"
        else:
            ret_file = filepath
        return ret_file

    def _is_markdown_file(self, file):
        return os.path.splitext(file)[-1] == ".md"

    def _set_file_convert_done(self, file):
        """
        Set the file is convert done
        Parameters
        ----------
        file :

        Returns
        -------

        """
        self._documents[file]['done'] = True

    def _is_file_convert_done(self, file):
        if self._is_markdown_file(file):
            return self._documents[file]['done'] == True
        else:
            return True


if __name__ == '__main__':
    HexoConverter(home=str(sys.argv[1]).strip(),
                  target=str(sys.argv[2]).strip(),
                  callbacks=[insert_new_line_for_math,
                             convert_obsidian_toc_to_hexo_toc]
                  ).parse_markdown()
    print("=" * 32)
    print("Done")
    print("=" * 32)
