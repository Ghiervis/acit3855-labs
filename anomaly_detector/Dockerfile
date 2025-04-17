FROM python:3

RUN mkdir /app
WORKDIR /app
RUN pip3 install setuptools

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
RUN mkdir -p data && chown -R nobody:nogroup /app
USER nobody

EXPOSE 8210
CMD ["python", "app.py"]
