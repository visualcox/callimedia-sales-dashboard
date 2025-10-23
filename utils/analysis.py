"""
매출 데이터 분석 함수들
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


def analyze_sales_by_period(df: pd.DataFrame, 
                            date_col: str = '날짜',
                            amount_col: str = '공급가액',
                            period: str = 'M') -> pd.DataFrame:
    """
    기간별 매출 분석
    
    Args:
        df: 매출 데이터프레임
        date_col: 날짜 컬럼명
        amount_col: 금액 컬럼명
        period: 집계 단위 ('D': 일, 'W': 주, 'M': 월, 'Q': 분기, 'Y': 년)
    
    Returns:
        pd.DataFrame: 기간별 매출 집계
    """
    if date_col not in df.columns or amount_col not in df.columns:
        return None
    
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    
    # 기간별 그룹화
    period_sales = df_copy.groupby(pd.Grouper(key=date_col, freq=period))[amount_col].agg([
        ('매출액', 'sum'),
        ('거래건수', 'count'),
        ('평균거래액', 'mean')
    ]).reset_index()
    
    return period_sales


def analyze_sales_by_client(df: pd.DataFrame,
                            client_col: str = '거래처명',
                            amount_col: str = '공급가액',
                            top_n: int = 20) -> pd.DataFrame:
    """
    거래처별 매출 분석 (판매처명 = 거래처명)
    
    Args:
        df: 매출 데이터프레임
        client_col: 거래처 컬럼명
        amount_col: 금액 컬럼명
        top_n: 상위 N개 거래처
    
    Returns:
        pd.DataFrame: 거래처별 매출 집계
    """
    if client_col not in df.columns or amount_col not in df.columns:
        return None
    
    client_sales = df.groupby(client_col)[amount_col].agg([
        ('총매출액', 'sum'),
        ('거래건수', 'count'),
        ('평균거래액', 'mean'),
        ('최대거래액', 'max'),
        ('최소거래액', 'min')
    ]).reset_index()
    
    # 매출 비중 계산
    total_sales = client_sales['총매출액'].sum()
    client_sales['매출비중(%)'] = (client_sales['총매출액'] / total_sales * 100).round(2)
    
    # 누적 비중 계산
    client_sales = client_sales.sort_values('총매출액', ascending=False)
    client_sales['누적비중(%)'] = client_sales['매출비중(%)'].cumsum().round(2)
    
    return client_sales.head(top_n)


def analyze_sales_by_product(df: pd.DataFrame,
                             product_col: str = '품목명',
                             amount_col: str = '공급가액',
                             top_n: int = 20) -> pd.DataFrame:
    """
    제품별 매출 분석
    
    Args:
        df: 매출 데이터프레임
        product_col: 제품 컬럼명
        amount_col: 금액 컬럼명
        top_n: 상위 N개 제품
    
    Returns:
        pd.DataFrame: 제품별 매출 집계
    """
    if product_col not in df.columns or amount_col not in df.columns:
        return None
    
    product_sales = df.groupby(product_col)[amount_col].agg([
        ('총매출액', 'sum'),
        ('판매건수', 'count'),
        ('평균단가', 'mean')
    ]).reset_index()
    
    # 매출 비중 계산
    total_sales = product_sales['총매출액'].sum()
    product_sales['매출비중(%)'] = (product_sales['총매출액'] / total_sales * 100).round(2)
    
    product_sales = product_sales.sort_values('총매출액', ascending=False)
    
    return product_sales.head(top_n)


def calculate_growth_rate(df: pd.DataFrame,
                          date_col: str = '날짜',
                          amount_col: str = '공급가액',
                          period: str = 'M') -> pd.DataFrame:
    """
    전년 대비 성장률 계산
    
    Args:
        df: 매출 데이터프레임
        date_col: 날짜 컬럼명
        amount_col: 금액 컬럼명
        period: 비교 단위
    
    Returns:
        pd.DataFrame: 성장률 데이터
    """
    if date_col not in df.columns or amount_col not in df.columns:
        return None
    
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    
    # 기간별 매출 집계
    period_sales = df_copy.groupby(pd.Grouper(key=date_col, freq=period))[amount_col].sum().reset_index()
    
    # 전기 대비 성장률
    period_sales['전기매출'] = period_sales[amount_col].shift(1)
    period_sales['성장률(%)'] = ((period_sales[amount_col] - period_sales['전기매출']) / period_sales['전기매출'] * 100).round(2)
    
    # 전년 동기 대비 (12개월 전)
    if period == 'M':
        period_sales['전년동기매출'] = period_sales[amount_col].shift(12)
        period_sales['전년대비성장률(%)'] = ((period_sales[amount_col] - period_sales['전년동기매출']) / period_sales['전년동기매출'] * 100).round(2)
    
    return period_sales


def predict_future_sales(df: pd.DataFrame,
                        date_col: str = '날짜',
                        amount_col: str = '공급가액',
                        months_ahead: int = 6) -> Dict:
    """
    향후 매출 예측 (단순 이동평균 기반)
    
    Args:
        df: 매출 데이터프레임
        date_col: 날짜 컬럼명
        amount_col: 금액 컬럼명
        months_ahead: 예측할 개월 수
    
    Returns:
        Dict: 예측 결과
    """
    if date_col not in df.columns or amount_col not in df.columns:
        return None
    
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    
    # 월별 매출 집계
    monthly_sales = df_copy.groupby(pd.Grouper(key=date_col, freq='M'))[amount_col].sum()
    
    # 최근 3개월, 6개월, 12개월 평균
    avg_3m = monthly_sales.tail(3).mean()
    avg_6m = monthly_sales.tail(6).mean()
    avg_12m = monthly_sales.tail(12).mean()
    
    # 추세 계산 (선형 회귀)
    x = np.arange(len(monthly_sales))
    y = monthly_sales.values
    
    if len(x) > 1:
        coefficients = np.polyfit(x, y, 1)
        trend_slope = coefficients[0]
        
        # 예측값 계산
        last_date = monthly_sales.index[-1]
        predictions = []
        
        for i in range(1, months_ahead + 1):
            pred_date = last_date + pd.DateOffset(months=i)
            pred_value = monthly_sales.iloc[-1] + (trend_slope * i)
            predictions.append({
                'date': pred_date,
                'predicted_sales': max(0, pred_value)  # 음수 방지
            })
        
        return {
            'avg_3m': avg_3m,
            'avg_6m': avg_6m,
            'avg_12m': avg_12m,
            'trend_slope': trend_slope,
            'predictions': predictions
        }
    else:
        return None


def get_top_growing_clients(df: pd.DataFrame,
                            date_col: str = '날짜',
                            client_col: str = '거래처명',
                            amount_col: str = '공급가액',
                            top_n: int = 10) -> pd.DataFrame:
    """
    성장률 높은 거래처 분석 (판매처명 = 거래처명)
    
    Args:
        df: 매출 데이터프레임
        date_col: 날짜 컬럼명
        client_col: 거래처 컬럼명
        amount_col: 금액 컬럼명
        top_n: 상위 N개
    
    Returns:
        pd.DataFrame: 고성장 거래처 목록
    """
    if date_col not in df.columns or client_col not in df.columns or amount_col not in df.columns:
        return None
    
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    
    # 최근 6개월과 이전 6개월 비교
    max_date = df_copy[date_col].max()
    recent_6m_start = max_date - pd.DateOffset(months=6)
    prev_6m_start = max_date - pd.DateOffset(months=12)
    prev_6m_end = recent_6m_start
    
    # 최근 6개월 매출
    recent_sales = df_copy[df_copy[date_col] >= recent_6m_start].groupby(client_col)[amount_col].sum()
    
    # 이전 6개월 매출
    prev_sales = df_copy[(df_copy[date_col] >= prev_6m_start) & (df_copy[date_col] < prev_6m_end)].groupby(client_col)[amount_col].sum()
    
    # 성장률 계산
    growth_df = pd.DataFrame({
        '최근6개월매출': recent_sales,
        '이전6개월매출': prev_sales
    })
    
    growth_df['성장률(%)'] = ((growth_df['최근6개월매출'] - growth_df['이전6개월매출']) / growth_df['이전6개월매출'] * 100).round(2)
    growth_df = growth_df.sort_values('성장률(%)', ascending=False)
    
    return growth_df.head(top_n).reset_index()
