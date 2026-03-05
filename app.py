import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Dashboard - Mall Customers", layout="wide")

CSV_FILE = "Mall_Customers.csv"
SEP = ";"  # importante neste ficheiro

st.title("🛍️ Dashboard - Mall Customers")
st.markdown("Exploração de clientes por género, idade, rendimento anual e spending score.")

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE, sep=SEP)
    # garantir tipos
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Annual Income (k$)"] = pd.to_numeric(df["Annual Income (k$)"], errors="coerce")
    df["Spending Score (1-100)"] = pd.to_numeric(df["Spending Score (1-100)"], errors="coerce")
    df = df.dropna()
    return df

df = load_data()

# ----------------- FILTROS (sidebar) -----------------
st.sidebar.header("Filtros")

if st.sidebar.button("Reset filtros"):
    st.rerun()

genders = sorted(df["Gender"].unique())
gender_sel = st.sidebar.multiselect("Género", genders, default=genders)

age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Idade", age_min, age_max, (age_min, age_max))

inc_min, inc_max = int(df["Annual Income (k$)"].min()), int(df["Annual Income (k$)"].max())
inc_range = st.sidebar.slider("Rendimento anual (k$)", inc_min, inc_max, (inc_min, inc_max))

score_min, score_max = int(df["Spending Score (1-100)"].min()), int(df["Spending Score (1-100)"].max())
score_range = st.sidebar.slider("Spending Score (1-100)", score_min, score_max, (score_min, score_max))

filtered = df[
    (df["Gender"].isin(gender_sel)) &
    (df["Age"].between(age_range[0], age_range[1])) &
    (df["Annual Income (k$)"].between(inc_range[0], inc_range[1])) &
    (df["Spending Score (1-100)"].between(score_range[0], score_range[1]))
].copy()

# ----------------- KPIs -----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Clientes", f"{len(filtered):,}")
c2.metric("Idade média", f"{filtered['Age'].mean():.1f}")
c3.metric("Rend. médio (k$)", f"{filtered['Annual Income (k$)'].mean():.1f}")
c4.metric("Score médio", f"{filtered['Spending Score (1-100)'].mean():.1f}")

st.divider()
st.divider()

st.subheader("KPIs por género")

by_gender = filtered.groupby("Gender").agg(
    Clientes=("CustomerID", "count"),
    Idade_media=("Age", "mean"),
    Rend_medio_k=("Annual Income (k$)", "mean"),
    Score_medio=("Spending Score (1-100)", "mean"),
).round(1)

st.dataframe(by_gender, use_container_width=True)
st.subheader("Comparação de métricas por género")

metrics_df = by_gender.reset_index().melt(
    id_vars="Gender",
    value_vars=["Idade_media", "Rend_medio_k", "Score_medio"],
    var_name="Métrica",
    value_name="Valor"
)

chart = alt.Chart(metrics_df).mark_bar().encode(
    x="Gender:N",
    y="Valor:Q",
    color="Métrica:N",
    column="Métrica:N",
    tooltip=["Gender", "Métrica", "Valor"]
)

st.altair_chart(chart, use_container_width=True)
# ----------------- GRÁFICOS -----------------
left, right = st.columns(2)

with left:
    st.subheader("Rendimento vs Spending Score")

    scatter = alt.Chart(filtered).mark_circle(size=70, opacity=0.7).encode(
        x=alt.X("Annual Income (k$):Q", title="Rendimento anual (k$)"),
        y=alt.Y("Spending Score (1-100):Q", title="Spending Score"),
        color=alt.Color("Gender:N", title="Género"),
        tooltip=["CustomerID", "Gender", "Age", "Annual Income (k$)", "Spending Score (1-100)"]
    ).interactive()

    st.altair_chart(scatter, use_container_width=True)

with right:
    st.subheader("Distribuição de idades")

    age_hist = alt.Chart(filtered).mark_bar().encode(
        x=alt.X("Age:Q", bin=alt.Bin(maxbins=15), title="Idade (bins)"),
        y=alt.Y("count():Q", title="Nº de clientes"),
        tooltip=[alt.Tooltip("count():Q", title="Nº de clientes")]
    )

    st.altair_chart(age_hist, use_container_width=True)

st.divider()

st.subheader("Top 10 clientes por Spending Score")
top10 = filtered.sort_values("Spending Score (1-100)", ascending=False).head(10)
st.dataframe(top10, use_container_width=True)
