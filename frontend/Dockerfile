# Basic image
FROM node:20-alpine as build

# working dir
WORKDIR /app

# INSTALL packages for apps
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Nginx-Image
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
