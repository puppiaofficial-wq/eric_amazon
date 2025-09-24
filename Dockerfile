FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements_web.txt .
RUN pip install --no-cache-dir -r requirements_web.txt

# Playwright 브라우저 설치
RUN playwright install chromium
RUN playwright install-deps chromium

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8501

# 헬스체크 추가
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Streamlit 실행
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
