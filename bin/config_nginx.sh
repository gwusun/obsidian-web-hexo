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

     # config the nginx
     # docs: http://nginx.org/en/docs/beginners_guide.html
     server {
          listen 443 ssl;
          server_name www.gwusun.top;
          root /usr/blog/hexo/;


          # config the https
          ssl_certificate /etc/nginx/cert/8884530_www.gwusun.top.pem;
          ssl_certificate_key /etc/nginx/cert/8884530_www.gwusun.top.key;

          # config 404 page.
          # If the page in the server is not found, the redirect to the 404 page.
          error_page  404 403 500 502 503 504  /404.html;
          proxy_intercept_errors on;
          server_tokens off;
          location = /404.html {
                root /usr/blog/hexo/;
          }

          # config the private directory.
          # In this directory, the user need the username and password to access.
          # username/password: lihui/lihui
          location /research/ {
               auth_basic "Input your password";
	             auth_basic_user_file /etc/nginx/nginx_password;
          }


      }
}
EOF
nginx -s stop
nginx