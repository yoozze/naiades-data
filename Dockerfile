# Build stage
# ===========

FROM node:14.18.1-alpine3.14 AS build-stage

ARG ROOT

WORKDIR /app

# Install build dependencies
# RUN apk add --no-cache gettext
# RUN apk add --no-cache perl

COPY $ROOT/package*.json ./
RUN npm install

# Copy project files from host
COPY $ROOT .

# Build service
RUN npm run build


# Production stage
# ================

FROM node:14.18.1-alpine3.14

ENV NODE_ENV=production

WORKDIR /app

# Copy from build stage
COPY --from=build-stage /app/build /app
COPY --from=build-stage /app/package*.json /app/

# Install production dependencies
RUN npm install --production

# Run service
EXPOSE 8080
ENTRYPOINT ["node", "index.js"]
