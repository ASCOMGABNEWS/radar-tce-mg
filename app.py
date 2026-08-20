import streamlit as st
import feedparser
from datetime import datetime

st.set_page_config(
    page_title="Radar TCE-MG",
    page_icon="🏛️",
    layout="wide"
)

# -----------------------------
# CONFIGURAÇÃO
# -----------------------------

FONTES = {
    "TCE-MG": 'https://news.google.com/rss/search?q=%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "TCE MG": 'https://news.google.com/rss/search?q=%22TCE%20MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Tribunal de Contas": 'https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22%20%22Minas%20Gerais%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Durval Ângelo": 'https://news.google.com/rss/search?q=%22Durval%20Ângelo%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Agostinho Patrus": 'https://news.google.com/rss/search?q=%22Agostinho%20Patrus%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Gilberto Diniz": 'https://news.google.com/rss/search?q=%22Gilberto%20Diniz%22%20TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',
}

# -----------------------------
# FUNÇÕES
# -----------------------------

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

            titulo = item.get("title", "")

            noticias.append({
                "titulo": titulo,
                "link": link,
                "fonte": nome,
                "data": item.get("published", "")
            })

    return noticias


# -----------------------------
# CABEÇALHO
# -----------------------------

st.title("🏛️ Radar TCE-MG")

st.markdown(
    """
    **Monitoramento de notícias relacionadas ao Tribunal de Contas
    do Estado de Minas Gerais**
    """
)

st.divider()

# -----------------------------
# NOTÍCIAS
# -----------------------------

noticias = buscar_noticias()

# -----------------------------
# MÉTRICAS
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📰 Notícias",
        len(noticias)
    )

with col2:
    st.metric(
        "🔎 Monitoramentos",
        len(FONTES)
    )

with col3:
    st.metric(
        "👤 Conselheiros",
        3
    )

with col4:
    st.metric(
        "🕐 Atualizado",
        datetime.now().strftime("%H:%M")
    )

st.divider()

# -----------------------------
# FILTROS
# -----------------------------

st.subheader("🔎 Filtros")

col1, col2 = st.columns(2)

with col1:

    filtro = st.selectbox(
        "Monitoramento",
        [
            "Todos",
            "TCE-MG",
            "TCE MG",
            "Tribunal de Contas",
            "Durval Ângelo",
            "Agostinho Patrus",
            "Gilberto Diniz"
        ]
    )

with col2:

    busca = st.text_input(
        "Buscar palavra",
        placeholder="Ex.: saúde, educação, licitação..."
    )


# -----------------------------
# APLICA FILTROS
# -----------------------------

filtradas = noticias

if filtro != "Todos":

    filtradas = [
        n for n in filtradas
        if n["fonte"] == filtro
    ]

if busca:

    filtradas = [
        n for n in filtradas
        if busca.lower() in n["titulo"].lower()
    ]


# -----------------------------
# RESULTADOS
# -----------------------------

st.subheader(
    f"📰 {len(filtradas)} notícias encontradas"
)

if not filtradas:

    st.info(
        "Nenhuma notícia encontrada com esses filtros."
    )

else:

    for noticia in filtradas:

        st.markdown(
            f"### {noticia['titulo']}"
        )

        col1, col2 = st.columns([4, 1])

        with col1:

            st.caption(
                f"🔎 {noticia['fonte']}"
            )

            if noticia["data"]:

                st.caption(
                    f"📅 {noticia['data']}"
                )

        with col2:

            st.link_button(
                "Ler matéria",
                noticia["link"]
            )

        st.divider()
