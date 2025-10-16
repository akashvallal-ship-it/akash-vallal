FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl gnupg build-essential git

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

RUN npm install -g @angular/cli

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 4200

CMD ["pytest", "-v"]
