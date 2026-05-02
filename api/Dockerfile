FROM node:20-alpine
RUN apk add --no-cache qemu-system-x86_64 qemu-img bash
WORKDIR /app
COPY package.json .
RUN npm install
COPY server.js .
EXPOSE 3000
CMD ["node", "server.js"]
