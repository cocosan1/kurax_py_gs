import streamlit as st
from PIL import Image

st.set_page_config(page_title='link_page')
st.markdown('### link page/shop来店者管理')

col1, col2, col3 = st.columns(3)
#google form
with col1:
    img_megane = Image.open('img/アンケート.png')
    st.image(img_megane, width=50)
    st.markdown('###### 入力フォーム')

    link = '[仙台店](https://docs.google.com/forms/d/e/1FAIpQLSfN8-ZERfNQXB30-m5WT1I-baquX0HVKaWQfM-WI94vJBlgtw/viewform?usp=sf_link)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[神谷町店](https://docs.google.com/forms/d/e/1FAIpQLSc2ihGhD7PX4_aNhQwHIxEGu5kTFKzJWEgFlN5gQt2XZsB95g/viewform?usp=sf_link)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[大阪店](https://docs.google.com/forms/d/e/1FAIpQLScP7mR9o1RMhCUvScljKK6pY9BLy2aQ_T6P4IXk8ODLRlNcQA/viewform?usp=sf_link)'
    st.markdown(link, unsafe_allow_html=True)

#spreadsheet
with col2:
    img_megane = Image.open('img/file.png')
    st.image(img_megane, width=50)
    st.markdown('###### データ記録ファイル')

    link = '[仙台店](https://docs.google.com/spreadsheets/d/1egsKlud3E88ISztAWpLCIoMyJMqL5FOmHmPz84zP7sQ/edit?usp=sharing)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[神谷町店](https://docs.google.com/spreadsheets/d/1_kYafUvb-5dTSk5WOvwXziVwxf5rBXfrITVHMtSTVa8/edit?usp=sharing)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[大阪店](https://docs.google.com/spreadsheets/d/1tiE2znpKPPqQqGpSSQcuIXxOOg89jKyj9FotJWlL67Q/edit?usp=sharing)'
    st.markdown(link, unsafe_allow_html=True)

#streamlit
with col3:
    img_megane = Image.open('img/graph.png')
    st.image(img_megane, width=50)
    st.markdown('###### 集計アプリ')

    link = '[仙台店](https://cocosan1-kurax-py-gs-main-k9pxb6.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[神谷町店](https://cocosan1-kurax-py-gs-kamiyacho-1fzajz.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)

    link = '[大阪店](https://cocosan1-kurax-py-gs-oosaka-8l24g4.streamlit.app/)'
    st.markdown(link, unsafe_allow_html=True)
