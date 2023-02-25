import pandas as pd
import gspread
import json
import streamlit as st
from google.oauth2 import service_account
import datetime
import plotly.figure_factory as ff
import plotly.graph_objects as go
# from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title='kurax_py_gs')
st.markdown('#### shop仙台 来場者分析')

#APIを叩くURL
# SP_COPE = [
#     'https://www.googleapis.com/auth/drive',
#     'https://spreadsheets.google.com/feeds'  
# ]

SP_SHEET = 'フォームの回答 1'

# 秘密鍵jsonファイルから認証情報を取得
#第一引数　秘密鍵のpath　第二引数　どこのAPIにアクセスするか
#st.secrets[]内は''で囲むこと
credentials = service_account.Credentials.from_service_account_info(st.secrets['gcp_service_account'], scopes=[ "https://www.googleapis.com/auth/spreadsheets", ])

#OAuth2のクレデンシャル（認証情報）を使用してGoogleAPIにログイン
gc = gspread.authorize(credentials)

# IDを指定して、Googleスプレッドシートのワークブックを取得
sh = gc.open_by_key(st.secrets['SP_SHHET_KEY'])

# シート名を指定して、ワークシートを選択
worksheet = sh.worksheet(SP_SHEET)

data= worksheet.get_all_values()

# スプレッドシートをDataFrameに取り込む
df = pd.DataFrame(data[1:], columns=data[0])

#カラム名変更
df2 = df.rename(columns={'-': 'timestamp'})

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
                       columns=df.columns[1:9], index=df.index)

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

df3['day_name'] = df3['timestamp'].map(lambda x: x.day_name())
df3['hour'] = df3['timestamp'].map(lambda x: x.hour)
df3['day_num'] = df3['timestamp'].map(lambda x: x.dayofweek)

df3['hour'] = df3['hour'].astype(str)
df3['day_num'] = df3['day_num'].astype(str)

df3['total'] = df3.loc[:, '年齢層（未成年）' :'年齢層（60代）'].sum(axis=1)

#日にちで集計
df3_date = df3.groupby('timestamp2', as_index=False).sum()
df3_date = df3_date.sort_values('timestamp2')

#年齢層リスト
age_list = ['年齢層（未成年）', '年齢層（20代）', '年齢層 （30代）', '年齢層（40代）', \
            '年齢層（50代）', '年齢層（60代）']

def zentai():
  #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加

    fig.add_trace(
        go.Scatter(
            x=df3_date['timestamp2'],
            y=df3_date['total'],
            # mode = 'lines+markers+text', #値表示
            # text=round(df_results[col][:2]/10000),
            # textposition="top center",
            name='来店者数')
        )

    #レイアウト設定     
    fig.update_layout(
        title='全体',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def age():
    selected_list = st.multiselect(
        '年齢層を選択',
        age_list
        )


    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in selected_list:
        fig.add_trace(
            go.Scatter(
                x=df3_date['timestamp2'],
                y=df3_date[col],
                # mode = 'lines+markers+text', #値表示
                # text=round(df_results[col][:2]/10000),
                # textposition="top center",
                name=col)
        )

    #レイアウト設定     
    fig.update_layout(
        title='年齢層別',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 





def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '全体': zentai,
        '年齢層別': age,

    }
    selected_app_name = st.sidebar.selectbox(label='分析項目の選択',
                                             options=list(apps.keys()))

    if selected_app_name == '-':
        st.info('サイドバーから分析項目を選択してください')
        st.stop()

    link = '[home](http://linkpagetest.s3-website-ap-northeast-1.amazonaws.com/)'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.caption('homeに戻る')    

    # 選択されたアプリケーションを処理する関数を呼び出す
    render_func = apps[selected_app_name]
    render_func()
  
if __name__ == '__main__':
    main()
  