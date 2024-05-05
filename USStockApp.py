

import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title('株価可視化アプリ')

try:
    st.sidebar.write("""
    # 対象株価
    こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
    """)

    st.sidebar.write("""
    ## 表示日数選択
    """)
    days = st.sidebar.slider('日数', 1, 50, 20)

    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider('範囲を指定してください。', 0.0, 350.0, (0.0, 350.0))

    @st.cache_data
    def get_data(days, tickers):
        df = pd.DataFrame()
        for company in tickers.keys():
            data = yf.download(tickers[company], period=f'{days}d')
            data = data[['Close']]
            data.columns = [company]
            data = data.T
            data.index.name = 'Name'
            df = pd.concat([df, data])
        return df

    tickers = {
        'apple': 'AAPL',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    df = get_data(days, tickers)

    st.sidebar.write(f"""
    ### 過去 **{days}日間の** 株価
    """)

    selectedCompanies = st.multiselect(
        '会社名を選択してください',
        list(df.index),
        ['google', 'amazon', 'apple']
    )

    if not selectedCompanies:
        st.error('少なくとも1社は選んでください')
    else:
        data = df.loc[selectedCompanies]
        st.write("## 株価USD", data.sort_index())
        dataReset = data.T.reset_index()
        dataMelted = pd.melt(dataReset, id_vars=['Date']).rename(
            columns={'variable': 'Name', 'value': 'StockPrices(USD)'}
        )
        
        chart = (
            alt.Chart(dataMelted)
            .mark_line(opacity=0.8)
            .encode(
                x="Date:T",
                y=alt.Y("StockPrices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color="Name:N"
            )
            .properties(title='Stock Prices')
        )
        
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "何かエラーが起きているようです。"
    )