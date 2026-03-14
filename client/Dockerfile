FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

FROM node:18-alpine

WORKDIR /app

# Install simple http server for serving static files
RUN npm install -g serve

# Copy built application from builder
COPY --from=builder /app/dist .

EXPOSE 3000

CMD ["serve", "-s", ".", "-l", "3000"]
