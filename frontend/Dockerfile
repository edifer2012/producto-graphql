FROM nginxinc/nginx-unprivileged:1.28-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY dist /usr/share/nginx/html
# Sin entrypoint de autoconfiguración: el filesystem de runtime es de solo lectura.
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
EXPOSE 8080
