import streamlit as st
import asyncio
import pandas as pd
from datetime import datetime
import json
import os
from amazon_review_scraper import AmazonReviewScraper

# 페이지 설정
st.set_page_config(
    page_title="Amazon Review Scraper",
    page_icon="🛒",
    layout="wide"
)

# 세션 상태 초기화
if 'scraper' not in st.session_state:
    st.session_state.scraper = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'reviews' not in st.session_state:
    st.session_state.reviews = []

def main():
    st.title("🛒 Amazon Review Scraper")
    st.markdown("---")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 로그인 정보
        st.subheader("Amazon 로그인 정보")
        email = st.text_input("이메일", value="puppiaofficial@gmail.com")
        password = st.text_input("비밀번호", value="Xxyy0208!", type="password")
        
        # 상품 정보
        st.subheader("상품 정보")
        product_url = st.text_input(
            "상품 URL", 
            value="https://www.amazon.com/-/ko/dp/B00390BGLK",
            help="Amazon 상품 페이지 URL을 입력하세요"
        )
        max_reviews = st.number_input(
            "최대 리뷰 수", 
            min_value=10, 
            max_value=1000, 
            value=50,
            help="수집할 최대 리뷰 개수 (권장: 50-200개)"
        )
        
        # 옵션
        st.subheader("옵션")
        headless = st.checkbox("백그라운드 실행", value=True, help="브라우저 창을 숨기고 실행")
        save_csv = st.checkbox("CSV 저장", value=True)
        save_json = st.checkbox("JSON 저장", value=True)
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 리뷰 수집")
        
        # 수집 버튼
        if st.button("🚀 리뷰 수집 시작", disabled=st.session_state.is_running):
            if validate_inputs(email, password, product_url):
                st.session_state.is_running = True
                st.rerun()
        
        # 진행 상황 표시
        if st.session_state.is_running:
            with st.spinner("리뷰를 수집하는 중..."):
                try:
                    # 비동기 함수 실행
                    reviews = asyncio.run(scrape_reviews_async(
                        email, password, product_url, max_reviews, headless
                    ))
                    
                    if reviews:
                        st.session_state.reviews = reviews
                        st.success(f"✅ 총 {len(reviews)}개의 리뷰를 수집했습니다!")
                        
                        # 파일 저장
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        if save_csv:
                            csv_file = f"amazon_reviews_{timestamp}.csv"
                            df = pd.DataFrame(reviews)
                            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                            st.info(f"CSV 파일 저장: {csv_file}")
                        
                        if save_json:
                            json_file = f"amazon_reviews_{timestamp}.json"
                            with open(json_file, 'w', encoding='utf-8') as f:
                                json.dump(reviews, f, ensure_ascii=False, indent=2)
                            st.info(f"JSON 파일 저장: {json_file}")
                    
                    else:
                        st.error("❌ 리뷰를 수집할 수 없었습니다.")
                        
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
                
                finally:
                    st.session_state.is_running = False
    
    with col2:
        st.header("📈 통계")
        
        if st.session_state.reviews:
            reviews = st.session_state.reviews
            
            # 기본 통계
            st.metric("총 리뷰 수", len(reviews))
            
            # 평점 통계
            ratings = [r['rating'] for r in reviews if r['rating'] > 0]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                st.metric("평균 평점", f"{avg_rating:.2f}")
                
                # 평점 분포
                rating_dist = pd.Series(ratings).value_counts().sort_index()
                st.bar_chart(rating_dist)
            
            # 인증된 구매 비율
            verified = sum(1 for r in reviews if r['verified_purchase'])
            verified_pct = (verified / len(reviews)) * 100
            st.metric("인증된 구매", f"{verified_pct:.1f}%")
    
    # 리뷰 데이터 표시
    if st.session_state.reviews:
        st.header("📝 수집된 리뷰")
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(st.session_state.reviews)
        
        # 필터링 옵션
        col1, col2, col3 = st.columns(3)
        with col1:
            min_rating = st.selectbox("최소 평점", [0, 1, 2, 3, 4, 5], index=0)
        with col2:
            verified_only = st.checkbox("인증된 구매만")
        with col3:
            show_count = st.number_input("표시할 리뷰 수", 1, len(df), min(10, len(df)))
        
        # 필터 적용
        filtered_df = df.copy()
        if min_rating > 0:
            filtered_df = filtered_df[filtered_df['rating'] >= min_rating]
        if verified_only:
            filtered_df = filtered_df[filtered_df['verified_purchase'] == True]
        
        # 데이터 표시
        st.dataframe(
            filtered_df.head(show_count)[['reviewer_name', 'rating', 'title', 'date', 'content']],
            use_container_width=True
        )
        
        # 다운로드 버튼
        col1, col2 = st.columns(2)
        with col1:
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 CSV 다운로드",
                csv_data,
                f"amazon_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
        
        with col2:
            json_data = json.dumps(st.session_state.reviews, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 JSON 다운로드",
                json_data,
                f"amazon_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )

def validate_inputs(email, password, product_url):
    """입력값 검증"""
    if not email.strip():
        st.error("이메일을 입력해주세요.")
        return False
    if not password.strip():
        st.error("비밀번호를 입력해주세요.")
        return False
    if not product_url.strip():
        st.error("상품 URL을 입력해주세요.")
        return False
    if 'amazon.com' not in product_url:
        st.error("올바른 Amazon URL을 입력해주세요.")
        return False
    return True

async def scrape_reviews_async(email, password, product_url, max_reviews, headless):
    """비동기 리뷰 수집"""
    scraper = AmazonReviewScraper()
    
    try:
        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("브라우저 시작 중...")
        progress_bar.progress(10)
        
        await scraper.start_browser(headless=headless)
        
        status_text.text("로그인 상태 확인 중...")
        progress_bar.progress(30)
        
        if not await scraper.check_login_status():
            status_text.text("로그인이 필요합니다. 브라우저에서 수동으로 로그인해주세요.")
            # 웹 환경에서는 수동 로그인 안내만 표시
            st.warning("⚠️ 브라우저에서 Amazon에 로그인해주세요. (약 30초 후 자동으로 재확인)")
            await asyncio.sleep(30)
            
            if not await scraper.check_login_status():
                st.error("로그인이 완료되지 않았습니다.")
                return []
        
        status_text.text("리뷰 수집 중...")
        progress_bar.progress(50)
        
        reviews = await scraper.get_all_reviews(product_url, max_reviews)
        
        progress_bar.progress(100)
        status_text.text("수집 완료!")
        
        return reviews
        
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")
        return []
    
    finally:
        try:
            await scraper.close_browser()
        except:
            pass

if __name__ == "__main__":
    main()
