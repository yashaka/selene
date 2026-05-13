FROM node:20-alpine AS assets

ARG TINYMCE_VERSION=8.0.2
WORKDIR /opt/tinymce
RUN npm --silent --no-fund --no-audit install tinymce@${TINYMCE_VERSION}

FROM nginxinc/nginx-unprivileged:1.29-alpine

COPY --from=assets /opt/tinymce/node_modules/tinymce /usr/share/nginx/html/tinymce
COPY site /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8000
