"""
브랜드 분석 페이지 (app.py에 추가할 함수)
"""
import streamlit as st
import pandas as pd
from utils.brand_analysis import (
    load_brand_list,
    add_brand_column,
    analyze_sales_by_brand,
    analyze_brand_trend,
    get_brand_product_detail,
    compare_brand_growth,
    get_brand_statistics
)
from utils.charts import (
    create_bar_chart,
    create_pie_chart,
    create_line_chart,
    create_pareto_chart
)


def page_brand_upload():
    """브랜드 리스트 업로드 페이지"""
    st.markdown('<div class="sub-header">🏷️ 브랜드 리스트 업로드</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>📌 브랜드 리스트 업로드 안내</strong><br>
    1. 취급 브랜드 목록이 담긴 CSV 파일을 업로드하세요<br>
    2. 매출 데이터의 제품명에서 자동으로 브랜드를 식별합니다<br>
    3. 브랜드별 매출 분석이 가능해집니다
    </div>
    """, unsafe_allow_html=True)
    
    brand_file = st.file_uploader(
        "브랜드 리스트 파일 업로드 (CSV)",
        type=['csv'],
        key="brand_uploader",
        help="첫 번째 컬럼에 브랜드명이 있어야 합니다"
    )
    
    if brand_file:
        with st.spinner("브랜드 리스트 로딩 중..."):
            try:
                brand_df = pd.read_csv(brand_file, encoding='utf-8-sig')
                st.session_state['brand_df'] = brand_df
                
                # 브랜드 리스트 추출
                brand_list = load_brand_list(brand_df)
                st.session_state['brand_list'] = brand_list
                
                st.success(f"✅ 브랜드 {len(brand_list)}개 로드 완료")
                
                # 브랜드 목록 표시
                st.markdown("#### 📋 등록된 브랜드")
                
                # 3열로 표시
                cols = st.columns(3)
                for idx, brand in enumerate(brand_list):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.markdown(f"✓ **{brand}**")
                
                # 매출 데이터가 있으면 브랜드 컬럼 추가
                if 'merged_sales_df' in st.session_state:
                    with st.spinner("매출 데이터에 브랜드 정보 추가 중..."):
                        sales_df = st.session_state['merged_sales_df'].copy()
                        
                        # 제품 컬럼 찾기
                        product_col = None
                        for col in ['품목명', '제품명', '상품명', '품명']:
                            if col in sales_df.columns:
                                product_col = col
                                break
                        
                        if product_col:
                            sales_df = add_brand_column(sales_df, brand_list, product_col)
                            st.session_state['merged_sales_df'] = sales_df
                            
                            # 브랜드 통계
                            brand_stats = get_brand_statistics(sales_df, '브랜드')
                            
                            st.markdown("---")
                            st.markdown("#### 📊 브랜드 매칭 결과")
                            
                            metric_cols = st.columns(4)
                            with metric_cols[0]:
                                st.metric("식별된 브랜드", f"{brand_stats.get('총_브랜드_수', 0)}개")
                            with metric_cols[1]:
                                st.metric("등록 브랜드", f"{len(brand_list)}개")
                            with metric_cols[2]:
                                st.metric("미분류(기타)", f"{brand_stats.get('브랜드별_거래건수', {}).get('기타', 0):,}건")
                            with metric_cols[3]:
                                most_brand = brand_stats.get('가장_많은_브랜드')
                                st.metric("최다 브랜드", most_brand if most_brand else "N/A")
                            
                            st.success("✅ 매출 데이터에 브랜드 정보가 추가되었습니다!")
                        else:
                            st.warning("⚠️ 제품명 컬럼을 찾을 수 없어 브랜드 매칭을 건너뜁니다.")
                
            except Exception as e:
                st.error(f"❌ 브랜드 리스트 로드 실패: {e}")


def page_brand_analysis():
    """브랜드별 매출 분석 페이지"""
    st.markdown('<div class="sub-header">🏷️ 브랜드별 매출 분석</div>', unsafe_allow_html=True)
    
    # 브랜드 리스트 확인
    if 'brand_list' not in st.session_state or 'merged_sales_df' not in st.session_state:
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
    for col in ['공급가액', '금액', '합계금액', '매출금액']:
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
        for col in ['날짜', '일자', '전표일자', '판매일자', '거래일자']:
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
                import plotly.express as px
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
                
                st.dataframe(
                    growth_df_display.style.format({
                        '최근6개월': '{:,.0f}',
                        '이전6개월': '{:,.0f}',
                        '성장액': '{:,.0f}',
                        '성장률(%)': '{:.2f}%'
                    }).background_gradient(subset=['성장률(%)'], cmap='RdYlGn'),
                    use_container_width=True
                )
        
        # 상세 데이터 테이블
        st.markdown("#### 📋 브랜드별 상세 데이터")
        st.dataframe(
            brand_sales.style.format({
                '총매출액': '{:,.0f}',
                '평균단가': '{:,.0f}',
                '최대금액': '{:,.0f}',
                '최소금액': '{:,.0f}',
                '매출비중(%)': '{:.2f}%',
                '누적비중(%)': '{:.2f}%'
            }),
            use_container_width=True
        )
        
        # 특정 브랜드 상세 분석
        st.markdown("---")
        st.markdown("#### 🔍 특정 브랜드 상세 분석")
        
        selected_brand = st.selectbox(
            "분석할 브랜드 선택",
            options=brand_sales['브랜드'].tolist()
        )
        
        if selected_brand:
            product_col = None
            for col in ['품목명', '제품명', '상품명', '품명']:
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
                    st.dataframe(
                        brand_products.style.format({
                            '총매출액': '{:,.0f}',
                            '평균단가': '{:,.0f}',
                            '브랜드내비중(%)': '{:.2f}%'
                        }),
                        use_container_width=True
                    )
