"""
차트 생성 함수들
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List


def create_line_chart(df: pd.DataFrame, 
                     x_col: str, 
                     y_col: str,
                     title: str = "시계열 차트",
                     y_title: str = "금액 (원)") -> go.Figure:
    """
    시계열 라인 차트 생성
    """
    fig = px.line(df, x=x_col, y=y_col, 
                  title=title,
                  markers=True)
    
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title=y_title,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_yaxes(tickformat=",")
    
    return fig


def create_bar_chart(df: pd.DataFrame,
                    x_col: str,
                    y_col: str,
                    title: str = "막대 차트",
                    orientation: str = 'v') -> go.Figure:
    """
    막대 차트 생성
    """
    fig = px.bar(df, x=x_col, y=y_col,
                 title=title,
                 orientation=orientation)
    
    fig.update_layout(
        xaxis_title=x_col if orientation == 'v' else y_col,
        yaxis_title=y_col if orientation == 'v' else x_col,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    if orientation == 'v':
        fig.update_yaxes(tickformat=",")
    else:
        fig.update_xaxes(tickformat=",")
    
    return fig


def create_pie_chart(df: pd.DataFrame,
                    names_col: str,
                    values_col: str,
                    title: str = "파이 차트") -> go.Figure:
    """
    파이 차트 생성
    """
    fig = px.pie(df, names=names_col, values=values_col,
                 title=title,
                 hole=0.3)  # 도넛 차트
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig


def create_stacked_bar_chart(df: pd.DataFrame,
                             x_col: str,
                             y_col: str,
                             color_col: str,
                             title: str = "누적 막대 차트") -> go.Figure:
    """
    누적 막대 차트 생성
    """
    fig = px.bar(df, x=x_col, y=y_col, color=color_col,
                 title=title,
                 barmode='stack')
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_yaxes(tickformat=",")
    
    return fig


def create_growth_chart(df: pd.DataFrame,
                       date_col: str,
                       amount_col: str,
                       growth_col: str,
                       title: str = "매출 및 성장률") -> go.Figure:
    """
    매출액과 성장률을 함께 보여주는 차트
    """
    fig = go.Figure()
    
    # 매출액 (막대)
    fig.add_trace(go.Bar(
        x=df[date_col],
        y=df[amount_col],
        name='매출액',
        yaxis='y',
        marker_color='lightblue'
    ))
    
    # 성장률 (선)
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[growth_col],
        name='성장률 (%)',
        yaxis='y2',
        mode='lines+markers',
        marker_color='red',
        line=dict(width=2)
    ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(title='날짜'),
        yaxis=dict(
            title='매출액 (원)',
            side='left',
            tickformat=","
        ),
        yaxis2=dict(
            title='성장률 (%)',
            side='right',
            overlaying='y',
            ticksuffix='%'
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_heatmap(df: pd.DataFrame,
                  x_col: str,
                  y_col: str,
                  z_col: str,
                  title: str = "히트맵") -> go.Figure:
    """
    히트맵 생성
    """
    pivot_df = df.pivot(index=y_col, columns=x_col, values=z_col)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='Blues',
        text=pivot_df.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_col,
    )
    
    return fig


def create_prediction_chart(historical_df: pd.DataFrame,
                           prediction_data: List[Dict],
                           date_col: str,
                           amount_col: str,
                           title: str = "매출 예측") -> go.Figure:
    """
    실적과 예측을 함께 보여주는 차트
    """
    fig = go.Figure()
    
    # 실적 데이터
    fig.add_trace(go.Scatter(
        x=historical_df[date_col],
        y=historical_df[amount_col],
        name='실적',
        mode='lines+markers',
        marker_color='blue'
    ))
    
    # 예측 데이터
    if prediction_data:
        pred_dates = [p['date'] for p in prediction_data]
        pred_values = [p['predicted_sales'] for p in prediction_data]
        
        fig.add_trace(go.Scatter(
            x=pred_dates,
            y=pred_values,
            name='예측',
            mode='lines+markers',
            marker_color='red',
            line=dict(dash='dash')
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='날짜',
        yaxis_title='매출액 (원)',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_yaxes(tickformat=",")
    
    return fig


def create_pareto_chart(df: pd.DataFrame,
                       category_col: str,
                       value_col: str,
                       cumulative_col: str = None,
                       title: str = "파레토 차트") -> go.Figure:
    """
    파레토 차트 (80/20 법칙 시각화)
    """
    fig = go.Figure()
    
    # 매출액 (막대)
    fig.add_trace(go.Bar(
        x=df[category_col],
        y=df[value_col],
        name='매출액',
        yaxis='y',
        marker_color='lightblue'
    ))
    
    # 누적 비중 (선)
    if cumulative_col and cumulative_col in df.columns:
        fig.add_trace(go.Scatter(
            x=df[category_col],
            y=df[cumulative_col],
            name='누적 비중',
            yaxis='y2',
            mode='lines+markers',
            marker_color='red',
            line=dict(width=2)
        ))
        
        # 80% 기준선
        fig.add_hline(
            y=80,
            line_dash="dash",
            line_color="orange",
            annotation_text="80%",
            annotation_position="right",
            yref='y2'
        )
    
    fig.update_layout(
        title=title,
        xaxis=dict(title=category_col),
        yaxis=dict(
            title='매출액 (원)',
            side='left',
            tickformat=","
        ),
        yaxis2=dict(
            title='누적 비중 (%)',
            side='right',
            overlaying='y',
            range=[0, 100],
            ticksuffix='%'
        ),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig
