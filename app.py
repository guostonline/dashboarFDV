import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import emoji

current_day = datetime.now().day

dataframe=""

def day_without_sunday():
    if current_day > 7:
        return current_day-1
    elif current_day > 14:
        return current_day-2
    elif current_day > 21:
        return current_day - 3
    else: return current_day-4


st.set_page_config(page_title="Rapport FDV",
                    page_icon=":bar_chart:",
                    layout="wide"
)

df = pd.read_excel(
    io="suivi.xlsx",
    engine="openpyxl",
    sheet_name=["AGADIR","QUALI NV"],
    #skiprows=8,
    usecols="A:AC",
    #nrows=163,
)

# st.dataframe(df)
# ------Sidebar-------
st.sidebar.header("Filter:")
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    # bytes_data = uploaded_file.getvalue()
    df = pd.read_excel(uploaded_file,
                                
                                engine="openpyxl",
                                sheet_name=["AGADIR","QUALI NV"],     
                                usecols="A:AC",
                                nrows=163,

    )
    
quantitatif_df=df.get("AGADIR")
qualitatif_df=df.get("QUALI NV")

    # st.write(bytes_data)
show_all_fdv = st.sidebar.checkbox('Tout les FDV')
vendeur = st.sidebar.multiselect(
    "Vendeur:",
    options=quantitatif_df["Vendeur"].unique(),
    default=quantitatif_df["Vendeur"][0],
    disabled=show_all_fdv
)



famille = st.sidebar.multiselect(
    "Famille:",
    options=quantitatif_df["Famille"].unique(),
    default=quantitatif_df["Famille"][6]
)


jour_travail = st.sidebar.text_input(
    label="Jour Travail", value=day_without_sunday())
jour_reste = st.sidebar.text_input(label="Jour Reste", value=24)




df_selection_quantitatif = quantitatif_df.query(
    "Vendeur== @vendeur & Famille==@famille"
)
df_select_qualitatif = qualitatif_df.query(
    "Vendeur== @vendeur" 
)


if show_all_fdv:
    df_selection_quantitatif = quantitatif_df.query(
        "Famille==@famille & Vendeur!='SOUATI NOUREDDINE'  & Vendeur!='CDZ AGADIR GROS' &Vendeur!='CHAKIB ELFIL' & Vendeur!='CDZ AGADIR DET2'& Vendeur!='VIDE' ", 
    )
df_selection_quantitatif = df_selection_quantitatif.astype({
    "REAL": "int",
    "OBJ": "int",
    "J-1": "int",
    "REAL.1": "int",
    '2021.1': "int",

})


st.dataframe(df_selection_quantitatif)
st.dataframe(df_select_qualitatif)


total_ht = int(df_selection_quantitatif["REAL"].sum())
total_ttc = round(total_ht*1.2)
min_ca = int(df_selection_quantitatif["REAL"].min())
min_ca_index = int(df_selection_quantitatif["REAL"].idxmin())

max_ca = int(df_selection_quantitatif["REAL"].max())
max_ca_index = int(df_selection_quantitatif["REAL"].idxmax())

objectif_ht = ((round(df_selection_quantitatif["OBJ"].sum()))*24/int(jour_travail))
objectif_ttc = round(objectif_ht*1.2)
rest_jour_ttc = round((objectif_ttc-(total_ttc))/int(jour_reste))
average_ttc = round(total_ttc/int(jour_travail))

moyenne_client_facture=round(int(df_select_qualitatif["CLT FACTURE"].sum())/ int(jour_travail))

col1, col2, col3, col4, col5,col6,col7,col8 = st.columns(8)
with col1:
    st.caption("Total HT",)
    st.subheader(f'{total_ht:,}')
with col2:
    st.caption("Total TTC")
    st.subheader(f'{total_ttc:,}')
with col3:
    st.caption("Objectif TTC")
    st.subheader(f'{objectif_ttc:,}')
with col4:
    st.caption("Rest jour TTC")
    st.subheader(f'{rest_jour_ttc:,}')
with col5:
    st.caption("ACM")
    st.subheader(f'{round(df_select_qualitatif["% vs Obj"].sum()*100):,}%')
with col6:
    st.caption("Moyenne TSM")
    st.subheader(moyenne_client_facture)
with col7:
    st.caption("Line /bl")
    st.subheader(f'{round(df_select_qualitatif["%"].sum()*100):,}%')
with col8:
    st.caption("TSM")
    st.subheader(f'{round(df_select_qualitatif["%.1"].sum()*100):,}%')
st.text(f"Maximum Réaliser : {max_ca:} ({quantitatif_df['Vendeur'][max_ca_index]:} {emoji.emojize(':1st_place_medal:')})")
st.text(f"Minimum Réaliser : {min_ca:} ({quantitatif_df['Vendeur'][min_ca_index]:} {emoji.emojize(':thumbs_down:')})")


vendeur_ca = (
    df_selection_quantitatif.groupby(by=["Vendeur"]).sum()[["REAL"]].sort_values(by="REAL")
)



fig_produit_sales = px.bar(
    vendeur_ca,
    x="REAL",
    y=vendeur_ca.index,
    orientation="h",
    title='<b>CA par Vendeur</b>',
    color_discrete_sequence=["#0083B8"] * len(vendeur_ca),
    template="plotly_white",
    color='REAL'
    
)
st.plotly_chart(fig_produit_sales)

hide_st_style = """
<style>

footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

print(moyenne_client_facture)
