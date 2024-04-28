FROM node:20
WORKDIR /app/

COPY ./sherlock-web/frontend/package.json ./sherlock-web/frontend/package-lock.json ./
RUN npm i

COPY ./sherlock-web/frontend/tsconfig.json ./tsconfig.json
COPY ./sherlock-web/frontend/next-env.d.ts ./next-env.d.ts
COPY ./sherlock-web/frontend/next.config.mjs ./src/next.config.mjs 

COPY ./sherlock-web/frontend/app/ ./app/
COPY ./sherlock-web/frontend/public/ ./public/

COPY ./sherlock/resources/data.json ./data.json

RUN npm run build

CMD npm run start