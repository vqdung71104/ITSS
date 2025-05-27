FROM node:23.11.0 AS build
WORKDIR /app
COPY package*.json .
RUN yarn install
COPY . .
RUN yarn build

FROM nginx:latest 
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]