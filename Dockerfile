FROM python:3.9-slim

WORKDIR /code

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# បង្កើត Folder សម្រាប់ Model និងផ្ដល់សិទ្ធិអាន/សរសេរ ១០០%
RUN mkdir -p /code/.u2net && chmod -R 777 /code/.u2net
ENV U2NET_HOME=/code/.u2net

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod -R 777 /code

CMD ["python", "app.py"]