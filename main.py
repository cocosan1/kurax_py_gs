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
#scpes 今回実際に使うGoogleサービスの範囲を指定
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
df3_date = df3.groupby('timestamp2', as_index=False).sum()
df3_date = df3_date.sort_values('timestamp2')

#月で集計
df3_month = df3.groupby('timestamp3', as_index=False).sum()
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

#********************************************************関数
#*************************1日集計
def oneday():
    selected_date = st.selectbox(
            '日にちを選択',
            df3_date['timestamp2'].sort_values(ascending=False)
            )
    
    df_selected = df3_date[df3_date['timestamp2']==selected_date]

    col1, col2, col3 = st.columns([1, 3, 5])

    with col1:
        st.metric('組数', value= df_selected['組数'])
        st.metric('人数', value= df_selected['total'])

    with col2:
        #可視化
        #グラフを描くときの土台となるオブジェクト
        fig = go.Figure()

        for col in df_selected.columns[7:9]:
           
            fig.add_trace(
                go.Bar(
                    x=[col],
                    y=df_selected[col],
                    text=df_selected[col],
                    textposition="outside", 
                    name= col)
        )

        #レイアウト設定     
        fig.update_layout(
            title='人数(性別)',
            showlegend=False #凡例表示
        )
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig, use_container_width=True) 

    with col3:
       #可視化
        #グラフを描くときの土台となるオブジェクト
        fig2 = go.Figure()

        for col in df_selected.columns[1:7]:
           
            fig2.add_trace(
                go.Bar(
                    x=[col],
                    y=df_selected[col],
                    text=df_selected[col],
                    textposition="outside", 
                    name=col)
        )

        #レイアウト設定     
        fig2.update_layout(
            title='人数(年齢層)',
            showlegend=False #凡例表示
        )
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig2, use_container_width=True)

    #時間帯別組数
    time_dict = {}
    df3_selected = df3[df3['timestamp2']== selected_date] 
    for time in time_list:
       df = df3_selected[df3_selected['hour']==time]
       time_dict[time] = len(df)

    df_time = pd.DataFrame(time_dict, index=['組数']).T

    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig3 = go.Figure()
    #今期のグラフの追加

    fig3.add_trace(
        go.Scatter(
            x=df_time.index,
            y=df_time['組数'],
            mode = 'lines+markers+text', #値表示
            text=df_time['組数'],
            textposition="top center",
            name='来店組数')
        )

    #レイアウト設定     
    fig3.update_layout(
        title='1日集計',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig3, use_container_width=True) 

#*********************************月集計
def month():
   
    selected_month = st.selectbox(
                '月を選択',
                df3_month['timestamp3'].sort_values(ascending=False)
                )
    
    df_selected = df3_month[df3_month['timestamp3']==selected_month]

    col1, col2, col3 = st.columns([1, 3, 5])

    with col1:
        st.metric('組数', value= df_selected['組数'])
        st.metric('人数', value= df_selected['total'])

    with col2:
        #可視化
        #グラフを描くときの土台となるオブジェクト
        fig = go.Figure()

        for col in df_selected.columns[7:9]:
            
            fig.add_trace(
                go.Bar(
                    x=[col],
                    y=df_selected[col],
                    text=df_selected[col],
                    textposition="outside", 
                    name= col)
        )

        #レイアウト設定     
        fig.update_layout(
            title='人数(性別)',
            showlegend=False #凡例表示
        )
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig, use_container_width=True) 

    with col3:
        #可視化
        #グラフを描くときの土台となるオブジェクト
        fig2 = go.Figure()

        for col in df_selected.columns[1:7]:
            
            fig2.add_trace(
                go.Bar(
                    x=[col],
                    y=df_selected[col],
                    text=df_selected[col],
                    textposition="outside", 
                    name=col)
        )

        #レイアウト設定     
        fig2.update_layout(
            title='人数(年齢層)',
            showlegend=False #凡例表示
        )
        #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
        st.plotly_chart(fig2, use_container_width=True)

    # col4, col5 = st.columns(2)
    # with col4:
    #     st.markdown('###### 比率(性別)')

    #     label_lst = []
    #     temp_list = []
    #     for col in df_selected.columns[7:9]:
    #        label_lst.append(col)
    #        temp_list.append(df_selected[col])
           
    #     fig_sex = go.Figure()
    #     fig_sex.add_trace(
    #        go.Pie(
    #         labels=label_lst,
    #         values=temp_list
    #         )
    #     )
    #     fig_sex.update_layout(
    #         showlegend=True, #凡例表示
    #         # height=200,
    #         # margin={'l': 20, 'r': 60, 't': 0, 'b': 0},
    #         )
    #     fig_sex.update_traces(textposition='inside', textinfo='label+percent') 
    #     #inside グラフ上にテキスト表示
    #     st.plotly_chart(fig_sex, use_container_width=True)
    #     #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅


    #時間帯別組数
    time_dict = {}
    df3_selected = df3[df3['timestamp3']== selected_month] 
    for time in time_list:
        df = df3_selected[df3_selected['hour']==time]
        time_dict[time] = len(df)

    df_time = pd.DataFrame(time_dict, index=['組数']).T

    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig3 = go.Figure()
    #今期のグラフの追加

    fig3.add_trace(
        go.Scatter(
            x=df_time.index,
            y=df_time['組数'],
            mode = 'lines+markers+text', #値表示
            text=df_time['組数'],
            textposition="top center",
            name='来店組数')
        )

    #レイアウト設定     
    fig3.update_layout(
        title='集計(月)',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig3, use_container_width=True) 
   

#*********************************全体
def zentai():
  #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加

    fig.add_trace(
        go.Scatter(
            x=df3_date['timestamp2'],
            y=df3_date['組数'],
            # mode = 'lines+markers+text', #値表示
            # text=round(df_results[col][:2]/10000),
            # textposition="top center",
            name='来店組数')
        )

    #レイアウト設定     
    fig.update_layout(
        title='日にち/全体',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def zentai_month():

    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig_month = go.Figure()
    #今期のグラフの追加

    fig_month.add_trace(
        go.Scatter(
            x=df3_month['timestamp3'],
            y=df3_month['組数'],
            mode = 'lines+markers+text', #値表示
            text=df3_month['組数'],
            textposition="top center",
            name='来店組数')
        )

    #レイアウト設定     
    fig_month.update_layout(
        title='全体(月)',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig_month, use_container_width=True) 

def age():
    selected_list = st.multiselect(
        '年齢層を選択/複数選択可',
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
        title='日にち/年齢層別/人数',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def age_month():
    selected_list = st.multiselect(
        '年齢層を選択/複数選択可',
        age_list
        )


    #可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in selected_list:
        fig.add_trace(
            go.Scatter(
                x=df3_month['timestamp3'],
                y=df3_month[col],
                mode = 'lines+markers+text', #値表示
                text=df3_month[col],
                textposition="top center",
                name=col)
        )

    #レイアウト設定     
    fig.update_layout(
        title='月/年齢層別/人数',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def day_sex():
  #groupbyで消去されたday_nameを追加
    df3_dayname = df3[['timestamp2', 'day_name']]
    df3_date2 = df3_date.merge(df3_dayname, on='timestamp2', how='left')

    df_day = df3_date2.groupby('day_name', as_index=False).mean()

    #grupbyで消えたday_name列の追加
    dayname_list = []
    for day_name in df_day['day_name']:
        if day_name == 'Monday':
            dayname_list.append(0)
        elif day_name == 'Tuesday':
            dayname_list.append(1)
        elif day_name == 'Wednesday':
            dayname_list.append(2)
        elif day_name == 'Thursday':
            dayname_list.append(3)
        elif day_name == 'Friday':
            dayname_list.append(4)
        elif day_name == 'Saturday':
            dayname_list.append(5)
        elif day_name == 'Sunday':
            dayname_list.append(6)

    df_day['day_num'] = dayname_list
    df_day = df_day.sort_values('day_num')

    selected_list = st.multiselect(
            '性別を選択/複数選択可',
            sex_list
            )

    #************************可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in selected_list:
        fig.add_trace(
            go.Scatter(
                x=df_day['day_name'],
                y=df_day[col],
                mode = 'lines+markers+text', #値表示
                text=round(df_day[col]),
                textposition="top center",
                name=col)
        )

    #レイアウト設定     
    fig.update_layout(
        title='曜日/性別/人数',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def day_age():
  #groupbyで消去されたday_nameを追加
    df3_dayname = df3[['timestamp2', 'day_name']]
    df3_date2 = df3_date.merge(df3_dayname, on='timestamp2', how='left')

    df_day = df3_date2.groupby('day_name', as_index=False).mean()

    #grupbyで消えたday_name列の追加
    dayname_list = []
    for day_name in df_day['day_name']:
        if day_name == 'Monday':
            dayname_list.append(0)
        elif day_name == 'Tuesday':
            dayname_list.append(1)
        elif day_name == 'Wednesday':
            dayname_list.append(2)
        elif day_name == 'Thursday':
            dayname_list.append(3)
        elif day_name == 'Friday':
            dayname_list.append(4)
        elif day_name == 'Saturday':
            dayname_list.append(5)
        elif day_name == 'Sunday':
            dayname_list.append(6)

    df_day['day_num'] = dayname_list
    df_day = df_day.sort_values('day_num')

    selected_list = st.multiselect(
            '年齢層を選択/複数選択可',
            age_list
            )

    #************************可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in selected_list:
        fig.add_trace(
            go.Scatter(
                x=df_day['day_name'],
                y=df_day[col],
                mode = 'lines+markers+text', #値表示
                text=round(df_day[col]),
                textposition="top center",
                name=col)
        )

    #レイアウト設定     
    fig.update_layout(
        title='曜日/年齢層/人数',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def time_day_sex():
   #時間毎に集計
    df3_hour = df3.groupby(['timestamp2', 'hour'], as_index=False).sum()
    df3_hour['day_name'] = df3_hour['timestamp2'].map(lambda x: x.day_name())

    dayname = st.selectbox(
            '曜日を選択',
            day_list
            )
    #曜日で絞込み
    df3_hour_selected = df3_hour[df3_hour['day_name']== dayname]
    df3_hour_selected = df3_hour_selected.groupby('hour', as_index=False).mean()
    df3_hour_selected = df3_hour_selected.sort_values('hour')

    selected_list = st.multiselect(
            '性別を選択/複数選択可',
            sex_list
            )

    #************************可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in selected_list:
        fig.add_trace(
            go.Scatter(
                x=df3_hour_selected['hour'],
                y=df3_hour_selected[col][:-2],
                mode = 'lines+markers+text', #値表示
                text=round(df3_hour_selected[col][:-2], 1), #小数点以下1ケタ
                textposition="top center",
                name=col)
        )
    #y軸設定 tick開始　dtick間隔    
    fig.update_yaxes(tick0=0, dtick=1)    

    #レイアウト設定     
    fig.update_layout(
        title='時間帯/曜日/性別/人数',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 

def time_day_age():
   #時間毎に集計
    df3_hour = df3.groupby(['timestamp2', 'hour'], as_index=False).sum()
    df3_hour['day_name'] = df3_hour['timestamp2'].map(lambda x: x.day_name())

    dayname = st.selectbox(
            '曜日を選択',
            day_list
            )
    #曜日で絞込み
    df3_hour_selected = df3_hour[df3_hour['day_name']== dayname]
    df3_hour_selected = df3_hour_selected.groupby('hour', as_index=False).mean()
    df3_hour_selected = df3_hour_selected.sort_values('hour')

    selected_list = st.multiselect(
            '年齢層を選択/複数選択可',
            age_list
            )

    #************************可視化
    #グラフを描くときの土台となるオブジェクト
    fig = go.Figure()
    #今期のグラフの追加
    for col in selected_list:
        fig.add_trace(
            go.Scatter(
                x=df3_hour_selected['hour'],
                y=df3_hour_selected[col][:-2],
                mode = 'lines+markers+text', #値表示
                text=round(df3_hour_selected[col][:-2], 1), #小数点以下1ケタ
                textposition="top center",
                name=col)
        )
    #y軸設定 tick開始　dtick間隔    
    fig.update_yaxes(tick0=0, dtick=1)     

    #レイアウト設定     
    fig.update_layout(
        title='時間帯/曜日/年齢層/人数',
        showlegend=True #凡例表示
    )
    #plotly_chart plotlyを使ってグラグ描画　グラフの幅が列の幅
    st.plotly_chart(fig, use_container_width=True) 
  





def main():
    # アプリケーション名と対応する関数のマッピング
    apps = {
        '-': None,
        '集計/日': oneday,
        '集計/月': month,
        '全体/日': zentai,
        '全体/月': zentai_month,
        '年齢層別/日': age,
        '年齢層別/月': age_month,
        '曜日/性別': day_sex,
        '曜日/年齢層': day_age,
        '時間帯/曜日/性別': time_day_sex,
        '時間帯/曜日/年齢層': time_day_age,

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
  