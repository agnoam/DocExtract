FROM python

WORKDIR /app/text-extractor

COPY . .

RUN python src/main.py