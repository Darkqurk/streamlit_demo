import streamlit as st
import pandas as pd
import plotly.express as px

st.title("키릴 생존 지수 분석기")
data = {"Episode": ["1화", "2화"], "Danger_Level": [3, 5], "Survival_Score": [80, 75]}
df = pd.DataFrame(data)
st.write(df)
fig = px.line(df, x="Episode", y="Survival_Score", title="키릴 생존 확률")
st.plotly_chart(fig)