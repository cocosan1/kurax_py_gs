import streamlit as st
from PIL import Image

import pandas as pd
import gspread
import json
from google.oauth2 import service_account
from datetime import datetime
from datetime import date
from zoneinfo import ZoneInfo #日本時間指定用
import plotly.figure_factory as ff
import plotly.graph_objects as go

st.set_page_config(page_title='link_page')
st.markdown('### link page/shop来店者管理')

#**************************************************************************************関数開始

def get_data(SP_SHEET_KEY):
    SP_SHEET = 'フォームの回答 1'

    # 秘密鍵jsonファイルから認証情報を取得
    #第一引数　秘密鍵のpath　第二引数　どこのAPIにアクセスするか
    #st.secrets[]内は''で囲むこと
    #scpes 今回実際に使うGoogleサービスの範囲を指定
    credentials = service_account.Credentials.from_service_account_info(st.secrets['gcp_service_account'], scopes=[ "https://www.googleapis.com/auth/spreadsheets", ])

    #OAuth2のクレデンシャル（認証情報）を使用してGoogleAPIにログイン
    gc = gspread.authorize(credentials)

    # IDを指定して、Googleスプレッドシートのワークブックを取得
    sh = gc.open_by_key(st.secrets[SP_SHEET_KEY])

    # シート名を指定して、ワークシートを選択
    worksheet = sh.worksheet(SP_SHEET)

    data= worksheet.get_all_values()

    # スプレッドシートをDataFrameに取り込む
    df = pd.DataFrame(data[1:], columns=data[0])

    return df

def make_data(df2):

    #ゼロ埋め
    miseinen_list = []
    n20_list = []
    n30_list = []
    n40_list = []
    n50_list = []
    n60_list = []
    male_list = []
    female_list = []
    for num in df2['年齢層（未成年）']:
        if num in  ['1', '2', '3', '4', '5']:
            miseinen_list.append(num)
        else:
            miseinen_list.append(0)

    for num in df2['年齢層（20代）']:
        if num in  ['1', '2', '3', '4', '5']:
            n20_list.append(num)
        else:
            n20_list.append(0)

    for num in df2['年齢層 （30代）']:
        if num in  ['1', '2', '3', '4', '5']:
            n30_list.append(num)
        else:
            n30_list.append(0)

    for num in df2['年齢層（40代）']:
        if num in  ['1', '2', '3', '4', '5']:
            n40_list.append(num)
        else:
            n40_list.append(0)

    for num in df2['年齢層（50代）']:
        if num in  ['1', '2', '3', '4', '5']:
            n50_list.append(num)
        else:
            n50_list.append(0)

    for num in df2['年齢層（60代）']:
        if num in  ['1', '2', '3', '4', '5']:
            n60_list.append(num)
        else:
            n60_list.append(0)

    for num in df2['性別（男性）']:
        if num in  ['1', '2', '3', '4', '5']:
            male_list.append(num)
        else:
            male_list.append(0)

    for num in df2['性別（女性）']:
        if num in  ['1', '2', '3', '4', '5']:
            female_list.append(num)
        else:
            female_list.append(0)

    df_temp = pd.DataFrame(list(zip(miseinen_list, n20_list, n30_list, n40_list, n50_list, n60_list, male_list, female_list)),\
                        columns=df2.columns[1:9], index=df2.index)

    #datetime型に変換
    df2['timestamp'] = pd.to_datetime(df2['timestamp'])

    #空欄の0埋め処理したdf_tempとtimestampをmerge df3
    df_date = (df2[['timestamp']])

    df3 = df_date.merge(df_temp, left_index=True, right_index=True, how='inner')

    #int変換
    df3['年齢層（未成年）'] = df3['年齢層（未成年）'].astype(int)
    df3['年齢層（20代）'] = df3['年齢層（20代）'].astype(int)
    df3['年齢層 （30代）'] = df3['年齢層 （30代）'].astype(int)
    df3['年齢層（40代）'] = df3['年齢層（40代）'].astype(int)
    df3['年齢層（50代）'] = df3['年齢層（50代）'].astype(int)
    df3['年齢層（60代）'] = df3['年齢層（60代）'].astype(int)
    df3['性別（男性）'] = df3['性別（男性）'].astype(int)
    df3['性別（女性）'] = df3['性別（女性）'].astype(int)

    #時刻データを削除した列の新設 str化
    df3['timestamp2'] = df3['timestamp'].map(lambda x: x.strftime('%Y-%m-%d'))
    #datetime化
    df3['timestamp2'] = pd.to_datetime(df3['timestamp2'])

    df3['timestamp3'] = df3['timestamp'].map(lambda x: x.strftime('%Y-%m'))
    #datetime化
    df3['timestamp3'] = pd.to_datetime(df3['timestamp3'])

    df3['day_name'] = df3['timestamp'].map(lambda x: x.day_name())
    df3['hour'] = df3['timestamp'].map(lambda x: x.hour)
    df3['day_num'] = df3['timestamp'].map(lambda x: x.dayofweek)

    df3['hour'] = df3['hour'].astype(str)
    df3['day_num'] = df3['day_num'].astype(str)

    df3['total'] = df3.loc[:, '年齢層（未成年）' :'年齢層（60代）'].sum(axis=1)


    #組数の算出 日にち
    kumi_dict = {}
    for  date in df3['timestamp2'].unique():
        df = df3[df3['timestamp2']==date]
        kumi_dict[date] = len(df)

    df_kumi = pd.DataFrame(kumi_dict, index=['組数']).T

    #組数の算出 月
    kumi_month_dict = {}
    for  month in df3['timestamp3'].unique():
        df = df3[df3['timestamp3']==month]
        kumi_month_dict[month] = len(df)

    df_kumi_month = pd.DataFrame(kumi_month_dict, index=['組数']).T

    #日にちで集計
    df3_date = df3.groupby('timestamp2', as_index=False)['total'].sum()
    df3_date = df3_date.sort_values('timestamp2')

    #月で集計
    df3_month = df3.groupby('timestamp3', as_index=False)['total'].sum()
    df3_month = df3_month.sort_values('timestamp3')

    #組数のmerge 日にち
    df3_date = df3_date.merge(df_kumi, left_on='timestamp2', right_index=True, how='inner')

    #組数のmerge 月
    df3_month = df3_month.merge(df_kumi_month, left_on='timestamp3', right_index=True, how='inner')
    df3_month = df3_month.sort_values('timestamp3', ascending=False)

    #年齢層リスト
    age_list = ['年齢層（未成年）', '年齢層（20代）', '年齢層 （30代）', '年齢層（40代）', \
                '年齢層（50代）', '年齢層（60代）']

    #性別リスト
    sex_list = ['total', '性別（男性）', '性別（女性）']

    #曜日リスト
    day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', ]

    #時間リスト
    time_list = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19']

    #集計/日にち
    

    # 現在の日付を取得する
    now = datetime.now(ZoneInfo("Asia/Tokyo"))

    # 指定された形式の文字列にフォーマットする
    now_string = now.strftime('%Y-%m-%d 00:00:00')

    # フォーマットされた文字列をdatetimeオブジェクトに変換する
    date_format = '%Y-%m-%d %H:%M:%S'
    d_now = datetime.strptime(now_string, date_format)
  
    df_today = df3_date[df3_date['timestamp2']==d_now]

    return df_today
    
   
def make_graph(x_list, y_list):
    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()

    for (shop_name, kumi_num) in zip(x_list, y_list):
        
        fig.add_trace(
            go.Bar(
                x=[shop_name],
                y=[kumi_num],
                text=kumi_num,
                textposition="outside", 
                name= shop_name)
    )
    #y軸の設定　tick0開始位置　dtick目盛り間隔
    fig.update_yaxes(
        tick0=0,
        dtick=5
        )

    #日本時間の表示
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    formatted_now = now.strftime("%Y-%m-%d %H:%M")
    #レイアウト設定     
    fig.update_layout(
        title=f'{formatted_now} 現在',
        showlegend=False #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 
#***********************************************************************関数終了

tab1, tab2, tab3 = st.tabs(['リンクページ', '本日の来店組数', 'spreadsheetへのアクセスについて'])

with tab1:

    col1, col2, col3 = st.columns(3)
    #google form
    with col1:
        img_megane = Image.open('img/アンケート.png')
        st.image(img_megane, width=50)
        st.markdown('###### 入力フォーム/google form')

        link = '[仙台店](https://docs.google.com/forms/d/e/1FAIpQLSfN8-ZERfNQXB30-m5WT1I-baquX0HVKaWQfM-WI94vJBlgtw/viewform?usp=sf_link)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[神谷町店](https://docs.google.com/forms/d/e/1FAIpQLSc2ihGhD7PX4_aNhQwHIxEGu5kTFKzJWEgFlN5gQt2XZsB95g/viewform?usp=sf_link)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[ミッドタウン店](https://docs.google.com/forms/d/e/1FAIpQLSdd1rb4DDEaEzTiQQnYOCX3hUK5Rdtq2b4VWxRByzhTfllieA/viewform?usp=sf_link)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[高山店](https://docs.google.com/forms/d/e/1FAIpQLSeleAgqgS4e2vkOey5lnIBG4zHIte9gxQRFCtzV4vKQo4ITFA/viewform?usp=sf_link)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[名古屋店](https://docs.google.com/forms/d/e/1FAIpQLSfnaJUQpl9g6q6CpdzHdojjgjA_6TfM2SeBdxTuBe_GF56Qgg/viewform?usp=sf_link)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[大阪店](https://docs.google.com/forms/d/e/1FAIpQLScP7mR9o1RMhCUvScljKK6pY9BLy2aQ_T6P4IXk8ODLRlNcQA/viewform?usp=sf_link)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[福岡店](https://docs.google.com/forms/d/e/1FAIpQLSeuZQqbYlDRB8xe5ap3kZCx4cf7Hi1bxf8yDS4YJU95tWfzzw/viewform?usp=sf_link)'
        st.markdown(link, unsafe_allow_html=True)

    #spreadsheet
    with col2:
        img_megane = Image.open('img/file.png')
        st.image(img_megane, width=50)
        st.markdown('###### データ保存/spreadsheet')

        link = '[仙台店](https://docs.google.com/spreadsheets/d/1egsKlud3E88ISztAWpLCIoMyJMqL5FOmHmPz84zP7sQ/edit?usp=sharing)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[神谷町店](https://docs.google.com/spreadsheets/d/1_kYafUvb-5dTSk5WOvwXziVwxf5rBXfrITVHMtSTVa8/edit?usp=sharing)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[ミッドタウン店](https://docs.google.com/spreadsheets/d/1987tNuYDI_1jZHqPHnuuXjSx8vwDl-JNIZODRxmBIXQ/edit?usp=sharing)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[高山店](https://docs.google.com/spreadsheets/d/1yI5flPSnVQYElfrJW3Ht0twyI5SedayhhPKLmLBurII/edit?usp=sharing)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[名古屋店](https://docs.google.com/spreadsheets/d/1gpged-YStsGNqwYg-qxItsouJf2sI3OOT-MIF_6HXxw/edit?usp=sharing)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[大阪店](https://docs.google.com/spreadsheets/d/1tiE2znpKPPqQqGpSSQcuIXxOOg89jKyj9FotJWlL67Q/edit?usp=sharing)'
        st.markdown(link, unsafe_allow_html=True)

        link = '[福岡店](https://docs.google.com/spreadsheets/d/160s4VTER_bHB8AZ2ehcUDLZKZjUJUNBOcUq1cJbydFI/edit?usp=sharing)'
        st.markdown(link, unsafe_allow_html=True)

    #streamlit
    with col3:
        img_megane = Image.open('img/graph.png')
        st.image(img_megane, width=50)
        st.markdown('###### 集計アプリ')

        link = '[全店共通](https://cocosan1-kurax-py-gs-calc-sj6dv8.streamlit.app/)'
        st.markdown(link, unsafe_allow_html=True)

with tab2:
    #全店グラフ作成
    st.markdown('###### 集計/本日')
    if st.button('全店の来店組数を見る ▼'): 

        #データ集約
        df_sendai = get_data('SP_SHEET_KEY_SENDAI')
        df_sendai2 = make_data(df_sendai)
        if len(df_sendai2) == 0:
            val_sendai = 0
        else:    
            val_sendai = int(df_sendai2['組数'])

        df_kamiyacho = get_data('SP_SHEET_KEY_KAMIYACHO')
        df_kamiyacho2 = make_data(df_kamiyacho)
        if len(df_kamiyacho2) == 0:
            val_kamiyacho = 0
        else:
            val_kamiyacho = int(df_kamiyacho2['組数'])


        df_midtown = get_data('SP_SHEET_KEY_MIDTOWN')
        df_midtown2 = make_data(df_midtown)
        if len(df_midtown2) == 0:
            val_midtown = 0
        else:
            val_midtown = int(df_midtown2['組数'])
            
        df_takayama = get_data('SP_SHEET_KEY_TAKAYAMA')
        df_takayama2 = make_data(df_takayama)
        if len(df_takayama2) == 0:
            val_takayama = 0
        else:    
            val_takayama = int(df_takayama2['組数'])

        df_nagoya = get_data('SP_SHEET_KEY_NAGOYA')
        df_nagoya2 = make_data(df_nagoya)
        if len(df_nagoya2) == 0:
            val_nagoya = 0
        else:    
            val_nagoya = int(df_nagoya2['組数'])

        df_oosaka = get_data('SP_SHEET_KEY_OOSAKA')
        df_oosaka2 = make_data(df_oosaka)
        if len(df_oosaka2) == 0:
            val_oosaka = 0
        else:     
            val_oosaka = int(df_oosaka2['組数'])

        df_fukuoka = get_data('SP_SHEET_KEY_FUKUOKA')
        df_fukuoka2 = make_data(df_fukuoka)
        if len(df_fukuoka2) == 0:
            val_fukuoka = 0
        else:    
            val_fukuoka = int(df_fukuoka2['組数'])

        x_list = ['仙台店', '神谷町店', 'ミッドタウン店', '高山店', '名古屋店', '大阪店', '福岡店']
        y_list = [val_sendai, val_kamiyacho, val_midtown, val_takayama, val_nagoya, val_oosaka, val_fukuoka]

        #グラフ作成
        make_graph(x_list, y_list)

with tab3:
        st.write('■ google chromeに下記のアドレスでログイン → spreadsheetにアクセス')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### 仙台店')
            st.write('hida.kitutuki44@gmail.com')
            st.markdown('###### 神谷町店')
            st.write('hida.kitutuki47@gmail.com')
            st.markdown('###### ミッドタウン店')
            st.write('hida.kitutuki17@gmail.com')
            st.markdown('###### 高山店')
            st.write('hida.kitutuki38@gmail.com')
            
        with col2: 
            st.markdown('###### 名古屋店')
            st.write('hida.kitutuki25@gmail.com')
            st.markdown('###### 大阪店')
            st.write('hida.kitutuki30@gmail.com')
            st.markdown('###### 福岡店')
            st.write('hida.kitutuki34@gmail.com')   



