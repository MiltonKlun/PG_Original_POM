# nginx stable-alpine resolved and verified 2026-09-12.
FROM nginx@sha256:dc5069ad14f19660b141b21236140b91656bf89bbc3e2417c70ae650cd66104c
WORKDIR /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html app.js style.css catalog.json __health ./
COPY productos/ ./productos/
COPY contacto/ ./contacto/
COPY account/ ./account/
COPY search/ ./search/
