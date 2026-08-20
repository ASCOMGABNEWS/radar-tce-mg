import streamlit as st
import feedparser
from datetime import datetime

st.set_page_config(
    page_title="Radar TCE-MG",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ Radar TCE-MG")
st.caption("Monitoramento de notícias relacionadas ao Tribunal de Contas de Minas Gerais")

FONTES = {
    "TCE-MG": 'https://news.google.com/rss/search?q=%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "TCE MG": 'https://news.google.com/rss/search?q=%22TCE+MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Tribunal de Contas + Minas": 'https://news.google.com/rss/search?q=%22Tribunal+de+Contas%22+%22Minas+Gerais%22&hl=pt-BR&gl=BR&ceid=BR:pt-419'
}


@st.cache_data(ttl=300)
def buscar_noticias():
    noticias = []
    links = set()

    for nome, url in FONTES.items():
        feed = feedparser.parse(url)

        for item in feed.entries:
            link = item.get("link", "")

            if not link or link in links:
                continue

            links.add(link)

            noticias.append({
                "titulo": item.get("title", "Sem título"),
                "link": link,
                "fonte": nome,
                "data": item.get("published", "")
            })

    return noticias


noticias = buscar_noticias()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📰 Notícias encontradas", len(noticias))

with col2:
    st.metric("🔎 Fontes pesquisadas", len(FONTES))

with col3:
    agora = datetime.now().strftime("%H:%M")
    st.metric("🕐 Atualizado", agora)


st.divider()

busca = st.text_input(
    "🔎 Filtrar notícias",
    placeholder="Ex.: saúde, educação, licitação, Agostinho..."
)

if busca:
    noticias = [
        n for n in noticias
        if busca.lower() in n["titulo"].lower()
    ]


st.subheader("Últimas notícias")

if not noticias:
    st.warning("Nenhuma notícia encontrada.")
else:
    for noticia in noticias:
        st.markdown(f"### {noticia['titulo']}")
        st.caption(f"Fonte da busca: {noticia['fonte']}")

        if noticia["data"]:
            st.caption(f"📅 {noticia['data']}")

        st.link_button(
            "Ler matéria",
            noticia["link"]
        )

        st.divider()
