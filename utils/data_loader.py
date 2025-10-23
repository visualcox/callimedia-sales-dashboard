"""
데이터 로딩 및 전처리 유틸리티
"""
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple
import io


@st.cache_data
def load_excel_file(uploaded_file) -> pd.DataFrame:
    """
    업로드된 Excel 파일을 DataFrame으로 로드
    
    Args:
        uploaded_file: Streamlit UploadedFile 객체
    
    Returns:
        pd.DataFrame: 로드된 데이터프레임
    """
    try:
        df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {e}")
        return None


def merge_sales_data(sales_files: List) -> pd.DataFrame:
    """
    여러 매출 데이터 파일을 하나로 병합 (Excel 또는 CSV)
    
    Args:
        sales_files: 업로드된 파일 리스트
    
    Returns:
        pd.DataFrame: 병합된 데이터프레임
    """
    dfs = []
    
    for file in sales_files:
        try:
            # 파일 형식에 따라 로드
            if file.name.endswith('.csv'):
                df = pd.read_csv(file, encoding='utf-8-sig')
            else:
                df = load_excel_file(file)
            
            if df is not None:
                dfs.append(df)
        except Exception as e:
            st.error(f"{file.name} 로드 중 오류: {e}")
    
    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True)
        return merged_df
    else:
        return None


def enrich_sales_with_client_info(sales_df: pd.DataFrame, 
                                   client_df: pd.DataFrame) -> pd.DataFrame:
    """
    매출 데이터에 거래처 정보 추가
    
    Args:
        sales_df: 매출 데이터프레임
        client_df: 거래처 데이터프레임
    
    Returns:
        pd.DataFrame: 거래처 정보가 추가된 매출 데이터프레임
    """
    # 판매처명/거래처명 컬럼 찾기
    sales_client_col = None
    for col in ['거래처명', '판매처명', '거래처', '고객명']:
        if col in sales_df.columns:
            sales_client_col = col
            break
    
    client_name_col = None
    for col in ['거래처명', '회사명', '업체명', '고객명']:
        if col in client_df.columns:
            client_name_col = col
            break
    
    if sales_client_col and client_name_col:
        # 거래처 정보와 병합
        enriched_df = sales_df.merge(
            client_df,
            left_on=sales_client_col,
            right_on=client_name_col,
            how='left'
        )
        return enriched_df
    else:
        st.warning("거래처명 컬럼을 찾을 수 없어 병합을 건너뜁니다.")
        return sales_df


def clean_and_prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    데이터 정리 및 전처리
    
    Args:
        df: 원본 데이터프레임
    
    Returns:
        pd.DataFrame: 정리된 데이터프레임
    """
    # 판매처명을 거래처명으로 통일 (판매처명 = 거래처명)
    if '판매처명' in df.columns and '거래처명' not in df.columns:
        df = df.rename(columns={'판매처명': '거래처명'})
    
    # 날짜 컬럼 찾기 및 변환
    date_cols = ['날짜', '일자', '전표일자', '판매일자', '거래일자']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # 금액 컬럼 찾기 및 숫자 변환
    amount_cols = ['공급가액', '금액', '합계금액', '매출금액', '판매금액']
    for col in amount_cols:
        if col in df.columns:
            # 문자열로 된 금액을 숫자로 변환
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 결측치 처리
    df = df.dropna(how='all')  # 모든 값이 NaN인 행 제거
    
    return df


def get_data_summary(df: pd.DataFrame) -> Dict:
    """
    데이터 요약 정보 생성
    
    Args:
        df: 데이터프레임
    
    Returns:
        Dict: 요약 정보 딕셔너리
    """
    summary = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'date_range': None,
        'total_amount': None,
        'unique_clients': None
    }
    
    # 날짜 범위
    date_cols = ['날짜', '일자', '전표일자', '판매일자', '거래일자']
    for col in date_cols:
        if col in df.columns:
            summary['date_range'] = (
                df[col].min().strftime('%Y-%m-%d') if pd.notna(df[col].min()) else None,
                df[col].max().strftime('%Y-%m-%d') if pd.notna(df[col].max()) else None
            )
            break
    
    # 총 매출액
    amount_cols = ['공급가액', '금액', '합계금액', '매출금액']
    for col in amount_cols:
        if col in df.columns:
            summary['total_amount'] = df[col].sum()
            break
    
    # 고유 거래처 수
    client_cols = ['거래처명', '판매처명', '거래처', '고객명']
    for col in client_cols:
        if col in df.columns:
            summary['unique_clients'] = df[col].nunique()
            break
    
    return summary
