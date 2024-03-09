FROM nginx:alpine
ENV NAME=frontend

COPY ./$NAME/default.conf /etc/nginx/conf.d/
COPY ./$NAME/index.html /usr/share/nginx/html/
COPY ./$NAME/styles.css /usr/share/nginx/html/
COPY ./$NAME/script.js /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]