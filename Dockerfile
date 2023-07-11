FROM node:16.20 AS parcel
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY bundles-src/ ./bundles-src/
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

FROM python:3.10
WORKDIR /app
COPY --from=parcel /app/bundles/ ./bundles/
RUN apt update  \
    && apt install -y libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
RUN mkdir -p frontend/  \
    && cp -R bundles/* frontend/  \
    && cp -R staticfiles/* frontend/
