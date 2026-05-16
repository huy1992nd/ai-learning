# Build Angular, serve with nginx + /api proxy to backend
FROM node:22-bookworm-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build -- --configuration production

FROM nginx:1.27-alpine

COPY nginx-docker.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/webui/browser /usr/share/nginx/html

EXPOSE 80
