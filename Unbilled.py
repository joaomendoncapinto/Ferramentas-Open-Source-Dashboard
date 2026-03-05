# Analise do Unbilled
# Install dependencies: pip install pandas openpyxl streamlit altair

import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="Dashboard Outstanding por País", layout="wide")

st.title("📊 Outstanding por País (apenas Days Since Due Date > 0)")

# 1) Ler o ficheiro Excel
# (se o ficheiro estiver noutra pasta, ajusta o nome/caminho)
ficheiro = "Unbilled Estimates_03_03_2026.xlsx"
df = pd.read_excel(ficheiro)

# 2) Garantir que as colunas são numéricas (para evitar erros)
df["Days Since Due Date"] = pd.to_numeric(df["Days Since Due Date"], errors="coerce")
df["OUTSTANDING_TOTAL_EST_CURR"] = pd.to_numeric(df["OUTSTANDING_TOTAL_EST_CURR"], errors="coerce")

# 3) Filtrar: só valores POSITIVOS em "Days Since Due Date"
df_filtrado = df[df["Days Since Due Date"] > 0].copy()

# 4) Agrupar por país e somar o outstanding
tabela = (
    df_filtrado
    .groupby("PGB_Country", as_index=False)["OUTSTANDING_TOTAL_EST_CURR"]
    .sum()
    .sort_values("OUTSTANDING_TOTAL_EST_CURR", ascending=False)
)

# 5) KPI (total geral)
total_geral = tabela["OUTSTANDING_TOTAL_EST_CURR"].sum()

col1, col2 = st.columns([1, 2])

with col1:
    st.metric("✅ Total Outstanding (EST_CURR)", f"{total_geral:,.2f}")

    # Filtro opcional por país
    paises = ["(Todos)"] + sorted(tabela["PGB_Country"].dropna().unique().tolist())
    pais_escolhido = st.selectbox("Filtrar por país", paises)

    if pais_escolhido != "(Todos)":
        tabela_mostrar = tabela[tabela["PGB_Country"] == pais_escolhido]
    else:
        tabela_mostrar = tabela

with col2:
    # 6) Gráfico de barras
    chart = (
        alt.Chart(tabela_mostrar)
        .mark_bar()
        .encode(
            x=alt.X("OUTSTANDING_TOTAL_EST_CURR:Q", title="Somatório OUTSTANDING_TOTAL_EST_CURR"),
            y=alt.Y("PGB_Country:N", sort="-x", title="País"),
            tooltip=["PGB_Country", alt.Tooltip("OUTSTANDING_TOTAL_EST_CURR:Q", format=",.2f")]
        )
        .properties(height=500)
    )

    st.altair_chart(chart, use_container_width=True)

st.subheader("📋 Tabela (somatório por país)")
st.dataframe(tabela_mostrar, use_container_width=True)

st.caption("Regras: entra apenas quem tem Days Since Due Date > 0.")