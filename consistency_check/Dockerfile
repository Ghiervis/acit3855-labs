FROM python:3
LABEL maintainer="your-email@bcit.ca"

RUN mkdir /app
WORKDIR /app
RUN pip3 install setuptools

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN mkdir -p /app/data && chown -R nobody:nogroup /app
USER nobody

EXPOSE 8200
CMD ["python", "app.py"]
