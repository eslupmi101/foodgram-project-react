FROM node:13.12.0-alpine as build

WORKDIR /app

COPY package.json package.json

COPY package-lock.json package-lock.json

RUN npm install

COPY . .

RUN npm run build

RUN mkdir /frontend_static/

RUN cp -r /app/build/. /frontend_static/.

CMD ["npm", "start"]
