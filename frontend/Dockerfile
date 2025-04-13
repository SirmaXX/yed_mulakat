FROM node:18-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install
RUN npm install datatables.net datatables.net-dt


COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app

COPY --from=build /app .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]