FROM python

WORKDIR /app/text-extractor

COPY requirements.txt ./requirements.txt
RUN pip install -f ./requirements.txt

COPY . .

RUN python src/main.py