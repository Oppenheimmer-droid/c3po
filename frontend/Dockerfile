FROM node:18-alpine

WORKDIR /usr/src/app

# Install all dependencies (including devDependencies) for build
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
COPY . .

# Build
RUN npm run build

# Optionally remove devDependencies to reduce image size
RUN npm prune --production || true

ENV PORT=3000
EXPOSE 3000

CMD ["npm", "run", "start"]
