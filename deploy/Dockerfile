FROM python:3.12-slim

WORKDIR /app

# システム依存のインストール（必要最小限）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 依存パッケージを先にインストール（Docker キャッシュ活用）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 非 root ユーザーで実行（セキュリティ）
RUN useradd -m botuser
USER botuser

# Bot を起動
CMD ["python", "main.py"]
