"""
칼라미디어 B2B 매출 분석 대시보드
Streamlit 기반 웹 애플리케이션
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 유틸리티 함수 임포트
from utils.data_loader import (
    load_excel_file, 
    merge_sales_data, 
    enrich_sales_with_client_info,
    clean_and_prepare_data,
    get_data_summary
)
from utils.analysis import (
    analyze_sales_by_period,
    analyze_sales_by_client,
    analyze_sales_by_product,
    calculate_growth_rate,
    predict_future_sales,
    get_top_growing_clients
)
from utils.charts import (
    create_line_chart,
    create_bar_chart,
    create_pie_chart,
    create_growth_chart,
    create_prediction_chart,
    create_pareto_chart
)
from utils.brand_analysis import (
    load_brand_list,
    add_brand_column,
    analyze_sales_by_brand,
    analyze_brand_trend,
    get_brand_product_detail,
    compare_brand_growth,
    get_brand_statistics
)

# 페이지 설정
st.set_page_config(
    page_title="칼라미디어 매출 분석",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #262730;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F0F2F6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #E8F4F8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B35;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def check_password():
    """
    간단한 비밀번호 인증
    """
    def password_entered():
        """비밀번호 확인"""
        # Secrets에서 비밀번호 가져오기 (없으면 기본값)
        try:
            correct_password = str(st.secrets["passwords"]["admin_password"])
        except:
            correct_password = "칼라미디어2024"  # 기본 비밀번호
        
        # 입력한 비밀번호 가져오기
        entered_password = st.session_state.get("password", "")
        
        if entered_password == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # 이미 인증되었으면 통과
    if st.session_state.get("password_correct", False):
        return True

    # 로그인 화면
    st.markdown('<div class="main-header">🔐 칼라미디어 매출 분석 시스템</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "비밀번호를 입력하세요",
            type="password",
            on_change=password_entered,
            key="password",
            placeholder="비밀번호 입력"
        )
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ 비밀번호가 틀렸습니다.")
        
        st.info("💡 기본 비밀번호: 칼라미디어2024")
    
    return False


def main():
    """메인 애플리케이션"""
    
    # 사이드바
    with st.sidebar:
        st.markdown("# 🏛️ 칼라미디어")
        st.markdown("### 📊 매출 분석 대시보드")
        st.markdown("---")
        
        # 메뉴 선택
        menu = st.radio(
            "메뉴 선택",
            [
                "📁 데이터 업로드",
                "🏷️ 브랜드 업로드",
                "📈 매출 분석",
                "🎯 거래처 분석",
                "📦 제품 분석",
                "🏷️ 브랜드 분석",
                "🔮 매출 예측",
                "💬 AI 질의응답"
            ],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### ℹ️ 정보")
        st.markdown(f"**접속 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if 'merged_sales_df' in st.session_state:
            st.success(f"✅ 데이터 로드 완료")
            st.info(f"📊 총 {len(st.session_state['merged_sales_df']):,}건")
    
    # 헤더
    st.markdown('<div class="main-header">📊 칼라미디어 B2B 매출 분석 대시보드</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 메뉴별 페이지
    if menu == "📁 데이터 업로드":
        page_data_upload()
    elif menu == "🏷️ 브랜드 업로드":
        page_brand_upload()
    elif menu == "📈 매출 분석":
        page_sales_analysis()
    elif menu == "🎯 거래처 분석":
        page_client_analysis()
    elif menu == "📦 제품 분석":
        page_product_analysis()
    elif menu == "🏷️ 브랜드 분석":
        page_brand_analysis()
    elif menu == "🔮 매출 예측":
        page_prediction()
    elif menu == "💬 AI 질의응답":
        page_ai_query()


def page_data_upload():
    """데이터 업로드 페이지"""
    st.markdown('<div class="sub-header">📁 데이터 업로드</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>📌 데이터 업로드 안내</strong><br>
    1. <strong>거래처 리스트</strong> 파일을 먼저 업로드하세요 (Excel 또는 CSV, 선택사항)<br>
    2. <strong>매출 데이터</strong> 파일을 업로드하세요 (Excel 또는 CSV, 여러 파일 가능)<br>
    3. 브랜드 분석을 원하시면 <strong>'🏷️ 브랜드 업로드'</strong> 메뉴에서 브랜드리스트를 업로드하세요<br>
    4. 데이터가 자동으로 병합되고 분석 준비가 완료됩니다
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 거래처 리스트")
        client_file = st.file_uploader(
            "거래처 정보 파일 업로드 (Excel 또는 CSV)",
            type=['xlsx', 'xls', 'csv'],
            key="client_uploader",
            help="거래처 상세 정보가 담긴 Excel 또는 CSV 파일"
        )
        
        if client_file:
            with st.spinner("거래처 데이터 로딩 중..."):
                # 파일 형식에 따라 로드
                if client_file.name.endswith('.csv'):
                    client_df = pd.read_csv(client_file, encoding='utf-8-sig')
                else:
                    client_df = load_excel_file(client_file)
                
                if client_df is not None:
                    st.session_state['client_df'] = client_df
                    st.success(f"✅ 거래처 {len(client_df):,}개 로드 완료")
                    
                    with st.expander("📊 거래처 데이터 미리보기"):
                        st.dataframe(client_df.head(10), use_container_width=True)
    
    with col2:
        st.markdown("#### 💰 매출 데이터")
        sales_files = st.file_uploader(
            "매출 데이터 파일 업로드 (Excel 또는 CSV, 여러 파일 선택 가능)",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=True,
            key="sales_uploader",
            help="기간별로 분리된 매출 데이터 파일들 (Excel 또는 CSV)"
        )
        
        if sales_files:
            with st.spinner("매출 데이터 로딩 및 병합 중..."):
                merged_df = merge_sales_data(sales_files)
                
                if merged_df is not None:
                    # 데이터 정리
                    merged_df = clean_and_prepare_data(merged_df)
                    
                    # 거래처 정보 병합
                    if 'client_df' in st.session_state:
                        merged_df = enrich_sales_with_client_info(
                            merged_df, 
                            st.session_state['client_df']
                        )
                    
                    st.session_state['merged_sales_df'] = merged_df
                    
                    # 요약 정보
                    summary = get_data_summary(merged_df)
                    
                    st.success(f"✅ 매출 데이터 {summary['total_rows']:,}건 로드 완료")
                    
                    # 요약 메트릭
                    metric_cols = st.columns(3)
                    with metric_cols[0]:
                        st.metric("총 레코드 수", f"{summary['total_rows']:,}건")
                    with metric_cols[1]:
                        if summary['total_amount']:
                            st.metric("총 매출액", f"{summary['total_amount']:,.0f}원")
                    with metric_cols[2]:
                        if summary['unique_clients']:
                            st.metric("거래처 수", f"{summary['unique_clients']:,}개")
                    
                    # 감지된 주요 컴럼 표시
                    col_names_preview = ', '.join(list(merged_df.columns[:8]))
                    if len(merged_df.columns) > 8:
                        col_names_preview += ', ...'
                    
                    st.info(f"""
✅ **데이터 구조 확인**  
📊 총 컴럼 수: **{len(merged_df.columns)}개**  
💰 금액 컴럼: **{summary.get('amount_col_used', '발견되지 않음')}**  
📋 실제 컴럼명: {col_names_preview}
                    """)
                    
                    # 데이터 미리보기
                    with st.expander("📊 매출 데이터 미리보기"):
                        st.dataframe(merged_df.head(20), use_container_width=True)
                    
                    # 컬럼 정보
                    with st.expander("📋 컬럼 정보"):
                        col_info = pd.DataFrame({
                            '컬럼명': merged_df.columns,
                            '데이터 타입': merged_df.dtypes.values,
                            '결측치': merged_df.isnull().sum().values
                        })
                        st.dataframe(col_info, use_container_width=True)


def page_sales_analysis():
    """매출 분석 페이지"""
    st.markdown('<div class="sub-header">📈 매출 분석</div>', unsafe_allow_html=True)
    
    if 'merged_sales_df' not in st.session_state:
        st.warning("⚠️ 먼저 데이터를 업로드해주세요.")
        return
    
    df = st.session_state['merged_sales_df']
    
    # 날짜 및 금액 컬럼 자동 감지
    date_col = None
    for col in ['일자', '날짜', '전표일자', '판매일자', '거래일자']:
        if col in df.columns:
            date_col = col
            break
    
    amount_col = None
    for col in ['합계금액', '공급가액', '금액', '매출금액', '판매금액', '공급가', '판매가', '단가', '금액(공급가액)']:
        if col in df.columns:
            amount_col = col
            break
    
    if not date_col or not amount_col:
        st.error("❌ 날짜 또는 금액 컬럼을 찾을 수 없습니다.")
        return
    
    # 분석 옵션
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "분석 기간 단위",
            options=['D', 'W', 'M', 'Q', 'Y'],
            format_func=lambda x: {'D': '일별', 'W': '주별', 'M': '월별', 'Q': '분기별', 'Y': '연도별'}[x],
            index=2
        )
    
    # 기간별 매출 분석
    period_sales = analyze_sales_by_period(df, date_col, amount_col, period)
    
    if period_sales is not None:
        # 메트릭
        total_sales = period_sales['매출액'].sum()
        avg_sales = period_sales['매출액'].mean()
        total_transactions = period_sales['거래건수'].sum()
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("총 매출액", f"{total_sales:,.0f}원")
        with metric_cols[1]:
            st.metric("평균 매출액", f"{avg_sales:,.0f}원")
        with metric_cols[2]:
            st.metric("총 거래건수", f"{total_transactions:,}건")
        with metric_cols[3]:
            st.metric("평균 거래액", f"{df[amount_col].mean():,.0f}원")
        
        st.markdown("---")
        
        # 매출 추이 차트
        st.markdown("#### 📊 매출 추이")
        period_labels = {'D': '일별', 'W': '주별', 'M': '월별', 'Q': '분기별', 'Y': '연도별'}
        fig = create_line_chart(
            period_sales,
            date_col,
            '매출액',
            f"기간별 매출 추이 ({period_labels[period]})",
            "매출액 (원)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 거래건수 차트
        st.markdown("#### 📦 거래건수 추이")
        fig2 = create_line_chart(
            period_sales,
            date_col,
            '거래건수',
            "기간별 거래건수 추이",
            "거래건수"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # 성장률 분석
        growth_df = calculate_growth_rate(df, date_col, amount_col, period)
        if growth_df is not None and '성장률(%)' in growth_df.columns:
            st.markdown("#### 📈 성장률 분석")
            fig3 = create_growth_chart(
                growth_df,
                date_col,
                amount_col,
                '성장률(%)',
                "매출액 및 성장률"
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # 상세 데이터 테이블
        with st.expander("📋 상세 데이터 보기"):
            st.dataframe(period_sales, use_container_width=True)


def page_client_analysis():
    """거래처 분석 페이지"""
    st.markdown('<div class="sub-header">🎯 거래처 분석</div>', unsafe_allow_html=True)
    
    if 'merged_sales_df' not in st.session_state:
        st.warning("⚠️ 먼저 데이터를 업로드해주세요.")
        return
    
    df = st.session_state['merged_sales_df']
    
    # 거래처 컬럼 찾기
    client_col = None
    for col in ['거래처명', '판매처명', '거래처', '고객명']:
        if col in df.columns:
            client_col = col
            break
    
    amount_col = None
    for col in ['합계금액', '공급가액', '금액', '매출금액', '판매금액', '공급가', '판매가', '단가', '금액(공급가액)']:
        if col in df.columns:
            amount_col = col
            break
    
    if not client_col or not amount_col:
        st.error("❌ 거래처 또는 금액 컬럼을 찾을 수 없습니다.")
        return
    
    # 분석 옵션
    top_n = st.slider("상위 거래처 수", 5, 50, 20)
    
    # 거래처별 분석
    client_sales = analyze_sales_by_client(df, client_col, amount_col, top_n)
    
    if client_sales is not None:
        # 주요 메트릭
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("총 거래처 수", f"{df[client_col].nunique():,}개")
        with metric_cols[1]:
            st.metric("상위 거래처 매출", f"{client_sales['총매출액'].sum():,.0f}원")
        with metric_cols[2]:
            st.metric("상위 거래처 비중", f"{client_sales['매출비중(%)'].sum():.1f}%")
        with metric_cols[3]:
            top_client = client_sales.iloc[0]
            st.metric("1위 거래처", top_client[client_col])
        
        st.markdown("---")
        
        # 파레토 차트
        st.markdown("#### 📊 거래처별 매출 (파레토 차트)")
        fig1 = create_pareto_chart(
            client_sales.head(top_n),
            client_col,
            '총매출액',
            '누적비중(%)',
            "거래처별 매출 및 누적 비중"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 상위 거래처 파이 차트
            st.markdown("#### 🥧 상위 거래처 매출 비중")
            fig2 = create_pie_chart(
                client_sales.head(10),
                client_col,
                '총매출액',
                "상위 10개 거래처 매출 분포"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # 거래처별 평균 거래액
            st.markdown("#### 💰 평균 거래액 상위 거래처")
            top_avg = client_sales.nlargest(10, '평균거래액')
            fig3 = create_bar_chart(
                top_avg,
                client_col,
                '평균거래액',
                "평균 거래액 Top 10",
                'h'
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # 고성장 거래처 분석
        date_col = None
        for col in ['일자', '날짜', '전표일자', '판매일자', '거래일자']:
            if col in df.columns:
                date_col = col
                break
        
        if date_col:
            st.markdown("#### 🚀 고성장 거래처")
            growing_clients = get_top_growing_clients(df, date_col, client_col, amount_col, 10)
            if growing_clients is not None and len(growing_clients) > 0:
                st.dataframe(
                    growing_clients.style.format({
                        '최근6개월매출': '{:,.0f}',
                        '이전6개월매출': '{:,.0f}',
                        '성장률(%)': '{:.2f}%'
                    }),
                    use_container_width=True
                )
        
        # 상세 데이터 테이블
        with st.expander("📋 거래처별 상세 데이터"):
            st.dataframe(
                client_sales.style.format({
                    '총매출액': '{:,.0f}',
                    '평균거래액': '{:,.0f}',
                    '최대거래액': '{:,.0f}',
                    '최소거래액': '{:,.0f}',
                    '매출비중(%)': '{:.2f}%',
                    '누적비중(%)': '{:.2f}%'
                }),
                use_container_width=True
            )


def page_product_analysis():
    """제품 분석 페이지"""
    st.markdown('<div class="sub-header">📦 제품 분석</div>', unsafe_allow_html=True)
    
    if 'merged_sales_df' not in st.session_state:
        st.warning("⚠️ 먼저 데이터를 업로드해주세요.")
        return
    
    df = st.session_state['merged_sales_df']
    
    # 제품 컬럼 찾기
    product_col = None
    for col in ['품명 및 규격', '품목명', '제품명', '상품명', '품명', '품목', '제품', '상품', '아이템', '물품', 'Product', 'Item']:
        if col in df.columns:
            product_col = col
            break
    
    if not product_col:
        st.error("❌ 제품 컬럼을 찾을 수 없습니다.")
        st.warning("📌 **찾고 있는 컬럼명**: 품명 및 규격, 품목명, 제품명, 상품명, 품명, 품목, 제품, 상품, 아이템, 물품, Product, Item")
        st.info("📋 **실제 컬럼**: " + ", ".join(df.columns.tolist()))
        st.info("""
💡 **해결 방법**:
1. CSV 파일의 헤더 행에서 제품 컬럼명을 위 목록 중 하나로 변경하세요
2. 또는 개발자에게 실제 컬럼명을 알려주세요
        """)
        return
    
    amount_col = None
    for col in ['합계금액', '공급가액', '금액', '매출금액', '판매금액', '공급가', '판매가', '단가', '금액(공급가액)']:
        if col in df.columns:
            amount_col = col
            break
    
    # 분석 옵션
    top_n = st.slider("상위 제품 수", 5, 50, 20)
    
    # 제품별 분석
    product_sales = analyze_sales_by_product(df, product_col, amount_col, top_n)
    
    if product_sales is not None:
        # 주요 메트릭
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("총 제품 수", f"{df[product_col].nunique():,}개")
        with metric_cols[1]:
            st.metric("총 매출액", f"{product_sales['총매출액'].sum():,.0f}원")
        with metric_cols[2]:
            st.metric("총 판매건수", f"{product_sales['판매건수'].sum():,}건")
        with metric_cols[3]:
            st.metric("평균 단가", f"{product_sales['평균단가'].mean():,.0f}원")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 상위 제품 매출 차트
            st.markdown("#### 📊 제품별 매출 순위")
            fig1 = create_bar_chart(
                product_sales.head(15),
                product_col,
                '총매출액',
                f"제품별 매출 Top 15",
                'h'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 제품별 매출 비중
            st.markdown("#### 🥧 제품별 매출 비중")
            fig2 = create_pie_chart(
                product_sales.head(10),
                product_col,
                '총매출액',
                "상위 10개 제품 매출 분포"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # 상세 데이터 테이블
        st.markdown("#### 📋 제품별 상세 데이터")
        # 포맷팅된 데이터프레임 표시
        styled_product = product_sales.copy()
        for col in ['총매출액', '평균단가']:
            if col in styled_product.columns:
                styled_product[col] = styled_product[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
        if '매출비중(%)' in styled_product.columns:
            styled_product['매출비중(%)'] = styled_product['매출비중(%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
        st.dataframe(styled_product, use_container_width=True)


def page_prediction():
    """매출 예측 페이지"""
    st.markdown('<div class="sub-header">🔮 매출 예측</div>', unsafe_allow_html=True)
    
    if 'merged_sales_df' not in st.session_state:
        st.warning("⚠️ 먼저 데이터를 업로드해주세요.")
        return
    
    df = st.session_state['merged_sales_df']
    
    # 날짜 및 금액 컬럼 찾기
    date_col = None
    for col in ['일자', '날짜', '전표일자', '판매일자', '거래일자']:
        if col in df.columns:
            date_col = col
            break
    
    amount_col = None
    for col in ['합계금액', '공급가액', '금액', '매출금액', '판매금액', '공급가', '판매가', '단가', '금액(공급가액)']:
        if col in df.columns:
            amount_col = col
            break
    
    if not date_col or not amount_col:
        st.error("❌ 날짜 또는 금액 컬럼을 찾을 수 없습니다.")
        return
    
    # 예측 옵션
    months_ahead = st.slider("예측 기간 (개월)", 1, 12, 6)
    
    # 매출 예측
    with st.spinner("매출 예측 중..."):
        prediction_result = predict_future_sales(df, date_col, amount_col, months_ahead)
    
    if prediction_result:
        # 주요 메트릭
        st.markdown("#### 📊 최근 매출 평균")
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric("최근 3개월 평균", f"{prediction_result['avg_3m']:,.0f}원")
        with metric_cols[1]:
            st.metric("최근 6개월 평균", f"{prediction_result['avg_6m']:,.0f}원")
        with metric_cols[2]:
            st.metric("최근 12개월 평균", f"{prediction_result['avg_12m']:,.0f}원")
        
        st.markdown("---")
        
        # 추세 정보
        trend = prediction_result['trend_slope']
        trend_text = "상승 📈" if trend > 0 else "하락 📉" if trend < 0 else "보합 ➡️"
        st.info(f"📊 **매출 추세**: {trend_text} (월평균 {abs(trend):,.0f}원)")
        
        # 예측 차트
        st.markdown("#### 🔮 매출 예측 차트")
        
        # 월별 실적 데이터
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        monthly_sales = df_copy.groupby(pd.Grouper(key=date_col, freq='M'))[amount_col].sum().reset_index()
        monthly_sales.columns = [date_col, amount_col]
        
        # 예측 차트 생성
        fig = create_prediction_chart(
            monthly_sales,
            prediction_result['predictions'],
            date_col,
            amount_col,
            f"향후 {months_ahead}개월 매출 예측"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 예측 데이터 테이블
        st.markdown("#### 📋 예측 상세 데이터")
        pred_df = pd.DataFrame(prediction_result['predictions'])
        pred_df['date'] = pd.to_datetime(pred_df['date']).dt.strftime('%Y-%m')
        pred_df.columns = ['예측월', '예측매출액']
        
        # 포맷팅된 데이터프레임 표시
        styled_pred = pred_df.copy()
        if '예측매출액' in styled_pred.columns:
            styled_pred['예측매출액'] = styled_pred['예측매출액'].apply(lambda x: f"{x:,.0f}원" if pd.notna(x) else "")
        st.dataframe(styled_pred, use_container_width=True)
        
        # 총 예측 매출
        total_predicted = sum([p['predicted_sales'] for p in prediction_result['predictions']])
        st.success(f"💰 **향후 {months_ahead}개월 예상 총 매출**: {total_predicted:,.0f}원")
    else:
        st.error("❌ 예측 데이터가 부족합니다.")


def page_ai_query():
    """AI 질의응답 페이지 (Gemini 또는 OpenAI 자동 fallback)"""
    st.markdown('<div class="sub-header">💬 AI 질의응답</div>', unsafe_allow_html=True)
    
    # API 키 확인 (Gemini 우선, OpenAI fallback)
    gemini_key = None
    openai_key = None
    
    try:
        gemini_key = st.secrets.get("GEMINI_API_KEY")
    except:
        pass
    
    try:
        openai_key = st.secrets.get("OPENAI_API_KEY")
    except:
        pass
    
    # 어떤 API도 없을 경우
    if not gemini_key and not openai_key:
        st.warning("⚠️ API 키가 설정되지 않았습니다.")
        st.markdown("""
        <div class="info-box">
        <strong>🔑 API 키 설정 방법</strong><br><br>
        <strong>Streamlit Cloud:</strong><br>
        1. 앱 대시보드 접속<br>
        2. Settings → Secrets 클릭<br>
        3. 다음 내용 입력:<br>
        <code>
        GEMINI_API_KEY = "여기에_API키_입력"<br>
        # 또는<br>
        OPENAI_API_KEY = "여기에_API키_입력"
        </code><br><br>
        <strong>API 키 발급:</strong><br>
        • Gemini: <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a><br>
        • OpenAI: <a href="https://platform.openai.com/api-keys" target="_blank">OpenAI Platform</a>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 사용할 LLM 표시
    if gemini_key:
        st.info("🌟 현재 **Google Gemini 1.5 Flash** 모델을 사용하고 있습니다.")
        llm_provider = "gemini"
    else:
        st.info("🤖 현재 **OpenAI GPT-4o-mini** 모델을 사용하고 있습니다.")
        llm_provider = "openai"
    
    if 'merged_sales_df' not in st.session_state:
        st.warning("⚠️ 먼저 데이터를 업로드해주세요.")
        return
    
    df = st.session_state['merged_sales_df']
    
    # 데이터 요약 생성
    date_cols = ['일자', '날짜', '전표일자', '판매일자', '거래일자']
    date_col = None
    for col in date_cols:
        if col in df.columns:
            date_col = col
            break
    
    date_range = "N/A"
    if date_col:
        try:
            date_range = f"{df[date_col].min()} ~ {df[date_col].max()}"
        except:
            pass
    
    summary_text = f"""
데이터 요약:
- 총 레코드 수: {len(df):,}건
- 컬럼: {', '.join(df.columns.tolist())}
- 기간: {date_range}

샘플 데이터 (상위 5개):
{df.head(5).to_string()}
"""
    
    # 질문 입력
    question = st.text_area(
        "매출 데이터에 대해 질문하세요",
        placeholder="예:\n- 판매가 있다가 최근 6개월 동안 판매가 없는 거래처 리스트를 알려줘, 그 업체의 연락처도 알려줘\n- 최근 3개월 매출 추이는?\n- 가장 많이 팔린 제품은?",
        height=100
    )
    
    if st.button("🤖 질문하기", type="primary"):
        if question:
            with st.spinner(f"{llm_provider.upper()} AI가 답변을 생성하는 중..."):
                try:
                    response_text = None
                    
                    # Gemini 사용
                    if llm_provider == "gemini":
                        try:
                            import google.generativeai as genai
                            genai.configure(api_key=gemini_key)
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            
                            prompt = f"""당신은 매출 데이터 분석 전문가입니다. 다음 매출 데이터를 분석하고 사용자의 질문에 답변해주세요.

{summary_text}

사용자 질문: {question}

답변 시 주의사항:
1. 구체적인 숫자와 통계를 포함하세요
2. 한국어로 명확하게 답변하세요
3. 데이터에서 확인할 수 없는 내용은 '데이터에서 확인할 수 없습니다'라고 명시하세요
4. 가능하면 인사이트를 제공하세요
"""
                            response = model.generate_content(prompt)
                            response_text = response.text
                        except Exception as gemini_error:
                            st.warning(f"⚠️ Gemini API 오류: {gemini_error}")
                            # OpenAI로 fallback
                            if openai_key:
                                st.info("🔄 OpenAI로 전환합니다...")
                                llm_provider = "openai"
                    
                    # OpenAI 사용
                    if llm_provider == "openai" and not response_text:
                        try:
                            from openai import OpenAI
                            client = OpenAI(api_key=openai_key)
                            
                            completion = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "system", "content": "당신은 매출 데이터 분석 전문가입니다. 한국어로 명확하고 구체적으로 답변하세요."},
                                    {"role": "user", "content": f"{summary_text}\n\n질문: {question}"}
                                ]
                            )
                            response_text = completion.choices[0].message.content
                        except Exception as openai_error:
                            st.error(f"❌ OpenAI API 오류: {openai_error}")
                    
                    # 답변 표시
                    if response_text:
                        st.markdown("### 🤖 AI 답변")
                        st.markdown(response_text)
                        st.caption(f"🏷️ 모델: {llm_provider.upper()}")
                    else:
                        st.error("❌ 답변 생성에 실패했습니다.")
                    
                except Exception as e:
                    st.error(f"❌ AI 답변 생성 중 오류 발생: {str(e)}")
                    st.info("💡 Streamlit Cloud Secrets에 올바른 API 키가 설정되어 있는지 확인해주세요.")
        else:
            st.warning("⚠️ 질문을 입력해주세요.")


def page_brand_upload():
    """브랜드 리스트 업로드 페이지"""
    st.markdown('<div class="sub-header">🏷️ 브랜드 리스트 업로드</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>📌 브랜드 리스트 업로드 안내</strong><br>
    1. 취급 브랜드 목록이 담긴 CSV 파일을 업로드하세요<br>
    2. 매출 데이터의 제품명에서 자동으로 브랜드를 식별합니다<br>
    3. 브랜드별 매출 분석이 가능해집니다<br><br>
    <strong>🎯 특수 브랜드 규칙:</strong><br>
    • <strong>RenewedVision</strong> 포함 시 → <strong>프로프리젠터</strong> 브랜드로 자동 인식
    </div>
    """, unsafe_allow_html=True)
    
    brand_file = st.file_uploader(
        "브랜드 리스트 파일 업로드 (CSV 또는 Excel)",
        type=['csv', 'xlsx', 'xls'],
        key="brand_uploader",
        help="첫 번째 컬럼에 브랜드명이 있어야 합니다"
    )
    
    if brand_file:
        with st.spinner("브랜드 리스트 로딩 중..."):
            try:
                # 파일 형식에 따라 로드
                if brand_file.name.endswith('.csv'):
                    brand_df = pd.read_csv(brand_file, encoding='utf-8-sig')
                else:
                    brand_df = load_excel_file(brand_file)
                
                if brand_df is not None:
                    st.session_state['brand_df'] = brand_df
                    
                    # 브랜드 리스트 추출
                    brand_mapping = load_brand_list(brand_df)
                    st.session_state['brand_mapping'] = brand_mapping
                    
                    st.success(f"✅ 브랜드 {len(brand_mapping)}개 로드 완료")
                    
                    # 브랜드 목록 표시
                    st.markdown("#### 📋 등록된 브랜드")
                    
                    # 3열로 표시 (대표 브랜드명만)
                    cols = st.columns(3)
                    for idx, brand in enumerate(brand_mapping.keys()):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            # 유사표기 개수 표시
                            variant_count = len(brand_mapping[brand])
                            st.markdown(f"✓ **{brand}** ({variant_count})")
                    
                    # 매출 데이터가 있으면 브랜드 컬럼 추가
                    if 'merged_sales_df' in st.session_state:
                        with st.spinner("매출 데이터에 브랜드 정보 추가 중..."):
                            sales_df = st.session_state['merged_sales_df'].copy()
                            
                            # 제품 컬럼 찾기
                            product_col = None
                            for col in ['품명 및 규격', '품목명', '제품명', '상품명', '품명', '품목', '제품', '상품', '아이템', '물품', 'Product', 'Item']:
                                if col in sales_df.columns:
                                    product_col = col
                                    break
                            
                            if product_col:
                                sales_df = add_brand_column(sales_df, brand_mapping, product_col)
                                st.session_state['merged_sales_df'] = sales_df
                                
                                # 브랜드 통계
                                brand_stats = get_brand_statistics(sales_df, '브랜드')
                                
                                st.markdown("---")
                                st.markdown("#### 📊 브랜드 매칭 결과")
                                
                                metric_cols = st.columns(4)
                                with metric_cols[0]:
                                    st.metric("식별된 브랜드", f"{brand_stats.get('총_브랜드_수', 0)}개")
                                with metric_cols[1]:
                                    st.metric("등록 브랜드", f"{len(brand_mapping)}개")
                                with metric_cols[2]:
                                    st.metric("미분류(기타)", f"{brand_stats.get('브랜드별_거래건수', {}).get('기타', 0):,}건")
                                with metric_cols[3]:
                                    most_brand = brand_stats.get('가장_많은_브랜드')
                                    st.metric("최다 브랜드", most_brand if most_brand else "N/A")
                                
                                st.success("✅ 매출 데이터에 브랜드 정보가 추가되었습니다!")
                            else:
                                st.warning("⚠️ 제품명 컬럼을 찾을 수 없어 브랜드 매칭을 건너뜁니다.")
                                st.error("📌 **찾고 있는 컬럼명**: 품명 및 규격, 품목명, 제품명, 상품명, 품명, 품목, 제품, 상품, 아이템, 물품, Product, Item")
                                st.info("📋 **실제 컬럼**: " + ", ".join(sales_df.columns.tolist()))
                                st.info("""
💡 **해결 방법**:
1. 매출 데이터 CSV 파일의 헤더에서 제품 컬럼명을 위 목록 중 하나로 변경하세요
2. 또는 개발자에게 실제 컬럼명을 알려주세요
                                """)
                
            except Exception as e:
                st.error(f"❌ 브랜드 리스트 로드 실패: {e}")
                import traceback
                st.code(traceback.format_exc())


def page_brand_analysis():
    """브랜드별 매출 분석 페이지"""
    st.markdown('<div class="sub-header">🏷️ 브랜드별 매출 분석</div>', unsafe_allow_html=True)
    
    # 브랜드 리스트 확인
    if 'brand_mapping' not in st.session_state or 'merged_sales_df' not in st.session_state:
        st.warning("⚠️ 먼저 브랜드 리스트와 매출 데이터를 업로드해주세요.")
        st.info("💡 사이드바에서 '📁 데이터 업로드' → '🏷️ 브랜드 업로드' 메뉴를 이용하세요.")
        return
    
    df = st.session_state['merged_sales_df']
    
    # 브랜드 컬럼 확인
    if '브랜드' not in df.columns:
        st.error("❌ 매출 데이터에 브랜드 정보가 없습니다. 브랜드 리스트를 다시 업로드해주세요.")
        return
    
    # 금액 컬럼 찾기
    amount_col = None
    for col in ['합계금액', '공급가액', '금액', '매출금액', '판매금액', '공급가', '판매가', '단가', '금액(공급가액)']:
        if col in df.columns:
            amount_col = col
            break
    
    if not amount_col:
        st.error("❌ 금액 컬럼을 찾을 수 없습니다.")
        return
    
    # 분석 옵션
    top_n = st.slider("상위 브랜드 수", 5, 30, 15)
    
    # 브랜드별 매출 분석
    brand_sales = analyze_sales_by_brand(df, '브랜드', amount_col, top_n)
    
    if brand_sales is not None:
        # 주요 메트릭
        total_brands = df['브랜드'].nunique()
        total_sales = brand_sales['총매출액'].sum()
        top_brand = brand_sales.iloc[0]
        
        metric_cols = st.columns(4)
        with metric_cols[0]:
            st.metric("총 브랜드 수", f"{total_brands}개")
        with metric_cols[1]:
            st.metric("상위 브랜드 매출", f"{total_sales:,.0f}원")
        with metric_cols[2]:
            st.metric("1위 브랜드", top_brand['브랜드'])
        with metric_cols[3]:
            st.metric("1위 매출액", f"{top_brand['총매출액']:,.0f}원")
        
        st.markdown("---")
        
        # 파레토 차트
        st.markdown("#### 📊 브랜드별 매출 (파레토 차트)")
        fig1 = create_pareto_chart(
            brand_sales,
            '브랜드',
            '총매출액',
            '누적비중(%)',
            "브랜드별 매출 및 누적 비중"
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 브랜드별 매출 순위
            st.markdown("#### 📊 브랜드별 매출 순위")
            fig2 = create_bar_chart(
                brand_sales.head(15),
                '브랜드',
                '총매출액',
                "브랜드별 매출 Top 15",
                'h'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # 브랜드별 매출 비중
            st.markdown("#### 🥧 브랜드별 매출 비중")
            fig3 = create_pie_chart(
                brand_sales.head(10),
                '브랜드',
                '총매출액',
                "상위 10개 브랜드 매출 분포"
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # 브랜드별 시계열 추이
        date_col = None
        for col in ['일자', '날짜', '전표일자', '판매일자', '거래일자']:
            if col in df.columns:
                date_col = col
                break
        
        if date_col:
            st.markdown("#### 📈 브랜드별 매출 추이")
            
            # 상위 5개 브랜드만 표시
            top_5_brands = brand_sales.head(5)['브랜드'].tolist()
            df_top5 = df[df['브랜드'].isin(top_5_brands)]
            
            brand_trend = analyze_brand_trend(df_top5, date_col, '브랜드', amount_col, 'M')
            
            if brand_trend is not None:
                fig4 = px.line(
                    brand_trend,
                    x=date_col,
                    y='매출액',
                    color='브랜드',
                    title="상위 5개 브랜드 월별 매출 추이",
                    markers=True
                )
                fig4.update_layout(
                    xaxis_title="날짜",
                    yaxis_title="매출액 (원)",
                    hovermode='x unified'
                )
                fig4.update_yaxes(tickformat=",")
                st.plotly_chart(fig4, use_container_width=True)
            
            # 브랜드별 성장률
            st.markdown("#### 🚀 브랜드별 성장률 (최근 6개월 vs 이전 6개월)")
            growth_df = compare_brand_growth(df, date_col, '브랜드', amount_col, 6)
            
            if growth_df is not None and len(growth_df) > 0:
                # 상위 10개만 표시
                growth_df_display = growth_df.head(10)
                
                # 포맷팅된 데이터프레임 표시 (background_gradient 제거)
                styled_df = growth_df_display.copy()
                # 숫자 포맷팅
                for col in ['최근6개월', '이전6개월', '성장액']:
                    if col in styled_df.columns:
                        styled_df[col] = styled_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
                if '성장률(%)' in styled_df.columns:
                    styled_df['성장률(%)'] = styled_df['성장률(%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
                
                st.dataframe(styled_df, use_container_width=True)
        
        # 상세 데이터 테이블
        st.markdown("#### 📋 브랜드별 상세 데이터")
        # 포맷팅된 데이터프레임 표시
        styled_brand_sales = brand_sales.copy()
        for col in ['총매출액', '평균단가', '최대금액', '최소금액']:
            if col in styled_brand_sales.columns:
                styled_brand_sales[col] = styled_brand_sales[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
        for col in ['매출비중(%)', '누적비중(%)']:
            if col in styled_brand_sales.columns:
                styled_brand_sales[col] = styled_brand_sales[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
        
        st.dataframe(styled_brand_sales, use_container_width=True)
        
        # 특정 브랜드 상세 분석
        st.markdown("---")
        st.markdown("#### 🔍 특정 브랜드 상세 분석")
        
        selected_brand = st.selectbox(
            "분석할 브랜드 선택",
            options=brand_sales['브랜드'].tolist()
        )
        
        if selected_brand:
            product_col = None
            for col in ['품명 및 규격', '품목명', '제품명', '상품명', '품명', '품목', '제품', '상품', '아이템', '물품', 'Product', 'Item']:
                if col in df.columns:
                    product_col = col
                    break
            
            if product_col:
                brand_products = get_brand_product_detail(
                    df, selected_brand, '브랜드', product_col, amount_col, 10
                )
                
                if brand_products is not None and len(brand_products) > 0:
                    st.markdown(f"##### 📦 {selected_brand} 브랜드 제품별 매출 Top 10")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 제품별 매출 차트
                        fig5 = create_bar_chart(
                            brand_products,
                            product_col,
                            '총매출액',
                            f"{selected_brand} 제품별 매출",
                            'h'
                        )
                        st.plotly_chart(fig5, use_container_width=True)
                    
                    with col2:
                        # 제품별 비중
                        fig6 = create_pie_chart(
                            brand_products,
                            product_col,
                            '총매출액',
                            f"{selected_brand} 제품 구성"
                        )
                        st.plotly_chart(fig6, use_container_width=True)
                    
                    # 상세 테이블
                    # 포맷팅된 데이터프레임 표시
                    styled_brand_prod = brand_products.copy()
                    for col in ['총매출액', '평균단가']:
                        if col in styled_brand_prod.columns:
                            styled_brand_prod[col] = styled_brand_prod[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
                    if '브랜드내뺄중(%)' in styled_brand_prod.columns:
                        styled_brand_prod['브랜드내뺄중(%)'] = styled_brand_prod['브랜드내뺄중(%)'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
                    st.dataframe(styled_brand_prod, use_container_width=True)


# 앱 실행
if __name__ == "__main__":
    if check_password():
        main()
