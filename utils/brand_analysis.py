"""
브랜드별 매출 분석 함수
"""
import pandas as pd
import re
from typing import List, Dict, Tuple


def extract_brand_from_product(product_name: str, brand_list: List[str]) -> str:
    """
    제품명에서 브랜드명 추출
    
    Args:
        product_name: 제품명
        brand_list: 브랜드 리스트
    
    Returns:
        str: 추출된 브랜드명 (없으면 '기타')
    """
    if pd.isna(product_name):
        return '기타'
    
    product_name = str(product_name).strip()
    
    # 브랜드 리스트를 길이 순으로 정렬 (긴 것부터 매칭)
    sorted_brands = sorted(brand_list, key=len, reverse=True)
    
    for brand in sorted_brands:
        # 대소문자 구분 없이 매칭
        if brand.upper() in product_name.upper():
            return brand
        
        # 공백이나 특수문자 앞뒤로 매칭
        pattern = rf'\b{re.escape(brand)}\b'
        if re.search(pattern, product_name, re.IGNORECASE):
            return brand
    
    return '기타'


def load_brand_list(brand_df: pd.DataFrame) -> List[str]:
    """
    브랜드 리스트 DataFrame에서 브랜드명 추출
    
    Args:
        brand_df: 브랜드 리스트 DataFrame
    
    Returns:
        List[str]: 브랜드명 리스트
    """
    # 첫 번째 컬럼을 브랜드명으로 간주
    if len(brand_df.columns) > 0:
        brand_col = brand_df.columns[0]
        brands = brand_df[brand_col].dropna().astype(str).str.strip().tolist()
        return [b for b in brands if b]
    return []


def add_brand_column(sales_df: pd.DataFrame, 
                     brand_list: List[str],
                     product_col: str = '품목명') -> pd.DataFrame:
    """
    매출 데이터에 브랜드 컬럼 추가
    
    Args:
        sales_df: 매출 데이터프레임
        brand_list: 브랜드 리스트
        product_col: 제품명 컬럼
    
    Returns:
        pd.DataFrame: 브랜드 컬럼이 추가된 데이터프레임
    """
    if product_col not in sales_df.columns:
        # 다른 제품 컬럼명 찾기
        for col in ['제품명', '상품명', '품명', '품목']:
            if col in sales_df.columns:
                product_col = col
                break
    
    if product_col in sales_df.columns:
        sales_df['브랜드'] = sales_df[product_col].apply(
            lambda x: extract_brand_from_product(x, brand_list)
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
                             product_col: str = '품목명',
                             amount_col: str = '공급가액',
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
