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

upload_cert:
	rsync  -avz  /Users/sunwu/SW-Research/hexo-websit/cert/ root@114.55.41.175:/etc/nginx/cert/
	# nginx
	# cat > /etc/nginx/nginx.conf <<"EOF"
      	#user  nginx;
      	#worker_processes  1;
      	#pid        /var/run/nginx.pid;
      	#events {
      	#    worker_connections  1024;
      	#}
      	#http{
      	#	server {
      	#	    listen 443 ssl;
      	#	    auth_basic off;
      	#	    server_name 114.55.41.175;
      	#	    root /usr/blog/hexo/;
      	#	    ssl_certificate /etc/nginx/cert/lessonplan.pem;
      	#	    ssl_certificate_key /etc/nginx/cert/lessonplan.key;
      	#	}
      	#	server {
      	#	    listen 80;
      	#	    auth_basic off;
      	#	    server_name 114.55.41.175;
      	#	    #将请求转成https
      	#	    rewrite ^(.*)$ https://$host$1 permanent;
      	#	}
      	#}
      	#EOF
      	#nginx -t
      	#nginx -s reload


# upload to github
d: build
	mv ./public/Index.html ./public/index.html
	rsync  -avz  /Users/sunwu/SW-Research/hexo-websit/public/* root@114.55.41.175:/usr/blog/hexo/


publish:
	hexo g
	hexo d

