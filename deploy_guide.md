# Amazon Review Scraper 웹 배포 가이드

## 방법 1: Streamlit Cloud (무료, 권장)

### 1. GitHub 저장소 준비
```bash
# 프로젝트를 GitHub에 업로드
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/amazon-review-scraper.git
git push -u origin main
```

### 2. Streamlit Cloud 배포
1. https://streamlit.io/cloud 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `your-repo/amazon-review-scraper`
5. Main file path: `streamlit_app.py`
6. "Deploy!" 클릭

### 3. 자동 배포 완료
- URL: `https://your-app-name.streamlit.app`
- 코드 변경 시 자동 재배포
- 무료로 사용 가능

## 방법 2: Heroku (유료)

### 1. 추가 파일 생성

#### Procfile
```
web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

#### runtime.txt
```
python-3.9.18
```

### 2. Heroku 배포
```bash
# Heroku CLI 설치 후
heroku create your-app-name
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## 방법 3: 자체 서버 (VPS/클라우드)

### 1. 서버 설정
```bash
# Ubuntu/Debian 서버에서
sudo apt update
sudo apt install python3 python3-pip nginx

# 프로젝트 업로드
git clone https://github.com/yourusername/amazon-review-scraper.git
cd amazon-review-scraper

# 의존성 설치
pip3 install -r requirements_web.txt
playwright install chromium

# 방화벽 설정
sudo ufw allow 8501
```

### 2. Streamlit 실행
```bash
# 백그라운드 실행
nohup streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 &
```

### 3. Nginx 프록시 설정 (선택사항)
```nginx
# /etc/nginx/sites-available/amazon-scraper
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 방법 4: Docker 컨테이너

### 1. Dockerfile 생성
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements_web.txt .
RUN pip install -r requirements_web.txt

# Playwright 브라우저 설치
RUN playwright install chromium
RUN playwright install-deps chromium

# 애플리케이션 코드 복사
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Docker 실행
```bash
# 이미지 빌드
docker build -t amazon-scraper .

# 컨테이너 실행
docker run -p 8501:8501 amazon-scraper
```

## 방법 5: FTP 서버 직접 업로드 (제한적)

### 1. 서버 요구사항
- Python 3.7+ 지원
- pip 패키지 설치 권한
- 포트 8501 접근 가능

### 2. 업로드할 파일들
```
amazon-review-scraper/
├── streamlit_app.py
├── amazon_review_scraper.py
├── requirements_web.txt
└── README.md
```

### 3. 서버에서 실행
```bash
# 의존성 설치
pip install -r requirements_web.txt
playwright install chromium

# 애플리케이션 실행
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

## 주의사항

### 1. 브라우저 자동화 제한
- 일부 호스팅 서비스는 브라우저 자동화를 제한할 수 있음
- Heroku, Railway 등에서는 추가 설정 필요

### 2. 메모리 사용량
- Playwright + Chromium은 메모리를 많이 사용
- 최소 1GB RAM 권장

### 3. 보안
- 로그인 정보를 환경변수로 관리
- HTTPS 사용 권장

### 4. 법적 고려사항
- Amazon 이용약관 준수
- 과도한 요청 방지

## 권장 배포 방법

1. **개발/테스트**: Streamlit Cloud (무료)
2. **소규모 운영**: 자체 VPS
3. **대규모 운영**: AWS/GCP + Docker

Streamlit Cloud가 가장 간단하고 무료로 시작할 수 있는 방법입니다!
