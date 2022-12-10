# Configure for the obsidian and hexo
obsidian_home := /Users/sunwu/SW-KnowledgeBase
hexo_home := /Users/sunwu/SW-Research/hexo-websit
host := 114.55.41.175

h:
	@echo "make d:\t\t generate html and upload to $(host)"
	@echo "make run:\t start view on local "
	@echo "make prepare:\t prepare nginx environment to $(host)"

run: clean convert
	hexo server --watch
# upload to github
d: build
	mv ./public/Index.html ./public/index.html
	rsync  --delete -avz  /Users/sunwu/SW-Research/hexo-websit/public/* root@$(host):/usr/blog/hexo/

prepare:
	ssh root@$(host) "nginx -t"
	rsync  -avz  ./cert/ root@$(host):/etc/nginx/cert/
	rsync  -avz  ./bin/ root@$(host):/etc/nginx/scripts/
	ssh root@$(host) "bash /etc/nginx/scripts/config_nginx.sh"
	ssh root@$(host) "nginx -s reload"

debug:
	hexo clean
	hexo server --debug


install:
	yarn remove hexo-rendered-marked
	yarn add hexo-rendered-pandoc

clean:
	hexo clean
	rm -rf source/_posts
	rm -rf source/images

convert:
	mkdir -p ./source/imgs
	cp ./images/dogs.jpeg ./source/imgs
	bash bin/init_categories_and_tags.sh
	python HexoConverter.py $(obsidian_home) $(hexo_home)


build: clean convert
	hexo generate --debug

commit:
	git add .
	git commit -m "update config"
	git push origin main


