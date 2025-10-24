"""
브랜드별 매출 분석 함수
"""
import pandas as pd
import re
from typing import List, Dict, Tuple


def extract_brand_from_product(product_name: str, brand_mapping: Dict[str, List[str]]) -> str:
    """
    제품명에서 브랜드명 추출 (유사표기 모두 지원)
    '품명 및 규격' 컬럼 형식: [브랜드명][제품명][제품규격 및 옵션정보]
    
    Args:
        product_name: 제품명 (형식: [브랜드명][제품명][규격])
        brand_mapping: {대표브랜드명: [모든_가능한_표기들]}
    
    Returns:
        str: 추출된 브랜드명 (없으면 '기타')
    """
    if pd.isna(product_name):
        return '기타'
    
    product_name = str(product_name).strip()
    product_name_upper = product_name.upper()
    
    # 1단계: 첫 번째 [브랜드명] 부분 추출 시도
    bracket_match = re.match(r'^\[([^\]]+)\]', product_name)
    if bracket_match:
        first_bracket = bracket_match.group(1).strip()
        first_bracket_upper = first_bracket.upper()
        
        # 모든 브랜드의 모든 표기와 비교
        for main_brand, variants in brand_mapping.items():
            for variant in variants:
                if variant.upper() == first_bracket_upper:
                    return main_brand
    
    # 2단계: 모든 브랜드의 모든 표기로 매칭 (긴 표기부터 우선)
    # 모든 표기를 길이 순으로 정렬
    all_variants_with_brand = []
    for main_brand, variants in brand_mapping.items():
        for variant in variants:
            all_variants_with_brand.append((variant, main_brand))
    
    # 길이 순으로 정렬 (긴 것부터)
    all_variants_with_brand.sort(key=lambda x: len(x[0]), reverse=True)
    
    for variant, main_brand in all_variants_with_brand:
        variant_upper = variant.upper()
        
        # 대소문자 구분 없이 포함 여부 확인
        if variant_upper in product_name_upper:
            return main_brand
        
        # 단어 경계 매칭 (공백이나 특수문자 앞뒤)
        try:
            pattern = rf'\b{re.escape(variant)}\b'
            if re.search(pattern, product_name, re.IGNORECASE):
                return main_brand
        except:
            pass  # 정규식 오류 무시
    
    return '기타'


def load_brand_list(brand_df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    브랜드 리스트 DataFrame에서 브랜드 매핑 정보 추출
    
    파일 구조:
    - 컬럼 1: 브랜드 한글 (대표 브랜드명)
    - 컬럼 2: 브랜드 영문
    - 컬럼 3: 유사표기 (쉼표로 구분)
    
    Args:
        brand_df: 브랜드 리스트 DataFrame (3컬럼: 한글, 영문, 유사표기)
    
    Returns:
        Dict[str, List[str]]: {대표브랜드명: [모든_가능한_표기들]}
    """
    brand_mapping = {}
    
    if len(brand_df.columns) < 2:
        # 구형식 (컬럼 1개): 첫 번째 컬럼만 사용
        brand_col = brand_df.columns[0]
        for brand in brand_df[brand_col].dropna().astype(str).str.strip():
            if brand:
                brand_mapping[brand] = [brand]
        return brand_mapping
    
    # 신형식 (컬럼 3개): 한글, 영문, 유사표기
    korean_col = brand_df.columns[0]  # 브랜드 한글
    english_col = brand_df.columns[1]  # 브랜드 영문
    similar_col = brand_df.columns[2] if len(brand_df.columns) > 2 else None  # 유사표기
    
    for idx, row in brand_df.iterrows():
        korean = str(row[korean_col]).strip() if pd.notna(row[korean_col]) else ""
        english = str(row[english_col]).strip() if pd.notna(row[english_col]) else ""
        
        if not korean:
            continue
        
        # 대표 브랜드명 = 한글
        main_brand = korean
        
        # 모든 가능한 표기 수집
        all_variants = [korean]
        
        # 영문 추가
        if english:
            all_variants.append(english)
        
        # 유사표기 추가
        if similar_col and pd.notna(row[similar_col]):
            similar_text = str(row[similar_col]).strip()
            if similar_text:
                # 쉼표로 분리
                similar_items = [s.strip() for s in similar_text.split(',') if s.strip()]
                all_variants.extend(similar_items)
        
        # 중복 제거
        all_variants = list(dict.fromkeys(all_variants))  # 순서 유지하면서 중복 제거
        
        brand_mapping[main_brand] = all_variants
    
    return brand_mapping


def add_brand_column(sales_df: pd.DataFrame, 
                     brand_mapping: Dict[str, List[str]],
                     product_col: str = '품목명') -> pd.DataFrame:
    """
    매출 데이터에 브랜드 컬럼 추가 (유사표기 모두 지원)
    
    Args:
        sales_df: 매출 데이터프레임
        brand_mapping: {대표브랜드명: [모든_가능한_표기들]}
        product_col: 제품명 컬러
    
    Returns:
        pd.DataFrame: 브랜드 컬럼이 추가된 데이터프레임
    """
    if product_col not in sales_df.columns:
        # 다른 제품 컬럼명 찾기 ('품명 및 규격' 우선)
        for col in ['품명 및 규격', '품목명', '제품명', '상품명', '품명', '품목', '상품', '아이템', '물품', 'Product', 'Item']:
            if col in sales_df.columns:
                product_col = col
                break
    
    if product_col in sales_df.columns:
        sales_df['브랜드'] = sales_df[product_col].apply(
            lambda x: extract_brand_from_product(x, brand_mapping)
        )
    else:
        sales_df['브랜드'] = '기타'
    
    return sales_df


def analyze_sales_by_brand(df: pd.DataFrame,
                           brand_col: str = '브랜드',
                           amount_col: str = '공급가액',
                           top_n: int = 20) -> pd.DataFrame:
    """
    브랜드별 매출 분석
    
    Args:
        df: 매출 데이터프레임
        brand_col: 브랜드 컬럼명
        amount_col: 금액 컬럼명
        top_n: 상위 N개 브랜드
    
    Returns:
        pd.DataFrame: 브랜드별 매출 집계
    """
    if brand_col not in df.columns or amount_col not in df.columns:
        return None
    
    brand_sales = df.groupby(brand_col)[amount_col].agg([
        ('총매출액', 'sum'),
        ('판매건수', 'count'),
        ('평균단가', 'mean'),
        ('최대금액', 'max'),
        ('최소금액', 'min')
    ]).reset_index()
    
    # 매출 비중 계산
    total_sales = brand_sales['총매출액'].sum()
    brand_sales['매출비중(%)'] = (brand_sales['총매출액'] / total_sales * 100).round(2)
    
    # 누적 비중 계산
    brand_sales = brand_sales.sort_values('총매출액', ascending=False)
    brand_sales['누적비중(%)'] = brand_sales['매출비중(%)'].cumsum().round(2)
    
    return brand_sales.head(top_n)


def analyze_brand_trend(df: pd.DataFrame,
                        date_col: str = '날짜',
                        brand_col: str = '브랜드',
                        amount_col: str = '공급가액',
                        period: str = 'M') -> pd.DataFrame:
    """
    브랜드별 시계열 매출 추이 분석
    
    Args:
        df: 매출 데이터프레임
        date_col: 날짜 컬럼명
        brand_col: 브랜드 컬럼명
        amount_col: 금액 컬럼명
        period: 집계 단위 ('M': 월, 'Q': 분기, 'Y': 년)
    
    Returns:
        pd.DataFrame: 브랜드별 시계열 매출
    """
    if date_col not in df.columns or brand_col not in df.columns or amount_col not in df.columns:
        return None
    
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    
    # 기간별, 브랜드별 그룹화
    brand_trend = df_copy.groupby([
        pd.Grouper(key=date_col, freq=period),
        brand_col
    ])[amount_col].sum().reset_index()
    
    brand_trend.columns = [date_col, brand_col, '매출액']
    
    return brand_trend


def get_brand_product_detail(df: pd.DataFrame,
                             brand: str,
                             brand_col: str = '브랜드',
                             product_col: str = '품명 및 규격',
                             amount_col: str = '합계금액',
                             top_n: int = 10) -> pd.DataFrame:
    """
    특정 브랜드의 제품별 상세 분석
    
    Args:
        df: 매출 데이터프레임
        brand: 브랜드명
        brand_col: 브랜드 컬럼명
        product_col: 제품 컬럼명
        amount_col: 금액 컬럼명
        top_n: 상위 N개 제품
    
    Returns:
        pd.DataFrame: 브랜드 내 제품별 매출
    """
    if brand_col not in df.columns:
        return None
    
    # 해당 브랜드 필터링
    brand_df = df[df[brand_col] == brand].copy()
    
    if product_col not in brand_df.columns or amount_col not in brand_df.columns:
        return None
    
    # 제품별 집계
    product_sales = brand_df.groupby(product_col)[amount_col].agg([
        ('총매출액', 'sum'),
        ('판매건수', 'count'),
        ('평균단가', 'mean')
    ]).reset_index()
    
    # 브랜드 내 비중
    total_brand_sales = product_sales['총매출액'].sum()
    product_sales['브랜드내비중(%)'] = (product_sales['총매출액'] / total_brand_sales * 100).round(2)
    
    product_sales = product_sales.sort_values('총매출액', ascending=False)
    
    return product_sales.head(top_n)


def compare_brand_growth(df: pd.DataFrame,
                        date_col: str = '날짜',
                        brand_col: str = '브랜드',
                        amount_col: str = '공급가액',
                        months: int = 6) -> pd.DataFrame:
    """
    브랜드별 성장률 비교
    
    Args:
        df: 매출 데이터프레임
        date_col: 날짜 컬럼명
        brand_col: 브랜드 컬럼명
        amount_col: 금액 컬럼명
        months: 비교 기간 (개월)
    
    Returns:
        pd.DataFrame: 브랜드별 성장률
    """
    if date_col not in df.columns or brand_col not in df.columns or amount_col not in df.columns:
        return None
    
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    
    max_date = df_copy[date_col].max()
    recent_start = max_date - pd.DateOffset(months=months)
    prev_start = max_date - pd.DateOffset(months=months*2)
    prev_end = recent_start
    
    # 최근 기간 매출
    recent_sales = df_copy[df_copy[date_col] >= recent_start].groupby(brand_col)[amount_col].sum()
    
    # 이전 기간 매출
    prev_sales = df_copy[
        (df_copy[date_col] >= prev_start) & (df_copy[date_col] < prev_end)
    ].groupby(brand_col)[amount_col].sum()
    
    # 성장률 계산
    growth_df = pd.DataFrame({
        f'최근{months}개월': recent_sales,
        f'이전{months}개월': prev_sales
    })
    
    growth_df['성장액'] = growth_df[f'최근{months}개월'] - growth_df[f'이전{months}개월']
    growth_df['성장률(%)'] = (
        (growth_df[f'최근{months}개월'] - growth_df[f'이전{months}개월']) / 
        growth_df[f'이전{months}개월'] * 100
    ).round(2)
    
    growth_df = growth_df.sort_values('성장률(%)', ascending=False)
    
    return growth_df.reset_index()


def get_brand_statistics(df: pd.DataFrame,
                         brand_col: str = '브랜드') -> Dict:
    """
    브랜드 통계 정보
    
    Args:
        df: 매출 데이터프레임
        brand_col: 브랜드 컬럼명
    
    Returns:
        Dict: 브랜드 통계
    """
    if brand_col not in df.columns:
        return {}
    
    stats = {
        '총_브랜드_수': df[brand_col].nunique(),
        '기타_제외_브랜드_수': df[df[brand_col] != '기타'][brand_col].nunique(),
        '브랜드별_거래건수': df.groupby(brand_col).size().to_dict(),
        '가장_많은_브랜드': df[brand_col].value_counts().index[0] if len(df) > 0 else None
    }
    
    return stats
