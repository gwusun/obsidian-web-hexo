# Configure for the obsidian and hexo
obsidian_home := /Users/sunwu/SW-KnowledgeBase
hexo_home := /Users/sunwu/SW-Research/hexo-websit

install:
	yarn remove hexo-rendered-marked
	yarn add hexo-rendered-pandoc

prepare:
	brew install pandoc
clean:
	hexo clean
	rm -rf source
convert:
	python HexoConverter.py $(obsidian_home) $(hexo_home)


build: clean convert
	hexo generate

run: build
	hexo server -w
# upload to github
d: build
	mv ./public/Index.html ./public/index.html
	rsync  -avz  /Users/sunwu/SW-Research/hexo-websit/public/* root@114.55.41.175:/usr/blog/hexo/

publish:
	hexo g
	hexo d

