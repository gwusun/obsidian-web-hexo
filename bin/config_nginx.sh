cat > /etc/nginx/nginx_password <<"EOF"
lihui:$apr1$.vH3abai$Jz8S1odfB2pSShLbTRZVJ0
EOF

cat > /etc/nginx/nginx.conf <<"EOF"
user  nginx;
worker_processes  1;
pid   /var/run/nginx.pid;
events {
    worker_connections  1024;
}
http{
     include mime.types;
     server {
          listen 443 ssl;
          auth_basic "Input your password";
	        auth_basic_user_file /etc/nginx/nginx_password;
          server_name www.gwusun.top;
          root /usr/blog/hexo/;
          ssl_certificate /etc/nginx/cert/8884530_www.gwusun.top.pem;
          ssl_certificate_key /etc/nginx/cert/8884530_www.gwusun.top.key;
      }
}
EOF
nginx
nginx -s reload