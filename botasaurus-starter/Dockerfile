# Base image chuẩn cho FastAPI
FROM python:3.10-slim

# Không buffer stdout/stderr => log sẽ hiển thị tức thì
ENV PYTHONUNBUFFERED=1
# Cài các thư viện hệ thống cần thiết + Chromium
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    curl \
    unzip \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libxss1 \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Đặt biến môi trường để Chrome có thể chạy không headless
ENV CHROME_BIN="/usr/bin/chromium"
# Cài pip requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ project vào container
COPY . .

# Mở port (nếu cần)
EXPOSE 8000

# Khởi chạy FastAPI app với uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
