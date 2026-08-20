import streamlit as st
import feedparser
from datetime import datetime, timedelta
from urllib.parse import urlparse

st.set_page_config(
    page_title="Radar TCE-MG",
    page_icon="🏛️",
    layout="wide"
)

FONTES = {
    "TCE-MG": 'https://news.google.com/rss/search?q=%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "TCE MG": 'https://news.google.com/rss/search?q=%22TCE%20MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Tribunal de Contas": 'https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22%20%22Minas%20Gerais%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Durval Ângelo": 'https://news.google.com/rss/search?q=%22Durval%20Ângelo%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Agostinho Patrus": 'https://news.google.com/rss/search?q=%22Agostinho%20Patrus%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    "Gilberto Diniz": 'https://news.google.com/rss/search?q=%22Gilberto%20Diniz%22%20TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',
}


def obter_data(item):
    try:
        if hasattr(item, "published_parsed") and item.published_parsed:
            return datetime(*item.published_parsed[:6])
    except Exception:
        pass

    return None


def extrair_veiculo(item):
    titulo = item.get("title", "")
    
    if " - " in titulo:
        partes = titulo.rsplit(" - ", 1)
        return partes[-1].strip()

    return "Fonte não identificada"


@st.cache_data(ttl=300)
def buscar_noticias():

    noticias = []
    links = set()

    limite = datetime.now() - timedelta(days=7)

    for nome, url in FONTES.items():

        feed = feedparser.parse(url)

        for item in feed.entries:

            link = item.get("link", "")

            if not link or link in links:
                continue

            data = obter_data(item)

            if data and data < limite:
                continue

            links.add(link)

            noticias.append({
                "titulo": item.get("title", "Sem título"),
                "link": link,
                "monitoramento": nome,
                "veiculo": extrair_veiculo(item),
                "data": data
            })

    noticias.sort(
        key=lambda x: x["data"] or datetime.min,
        reverse=True
    )

    return noticias


# -----------------------------
# CABEÇALHO
# -----------------------------

st.title("🏛️ Radar TCE-MG")

st.caption(
    "Monitoramento automático de notícias relacionadas "
    "ao Tribunal de Contas de Minas Gerais"
)

col_botao, col_atualizacao = st.columns([1, 5])

with col_botao:
    if st.button("🔄 Atualizar agora"):
        st.cache_data.clear()
        st.rerun()

with col_atualizacao:
    st.caption(
        "Atualização automática da coleta: a cada 5 minutos"
    )

st.divider()


# -----------------------------
# COLETA
# -----------------------------

noticias = buscar_noticias()


# -----------------------------
# MÉTRICAS
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📰 Notícias", len(noticias))

with col2:
    st.metric(
        "📡 Monitoramentos",
        len(FONTES)
    )

with col3:
    veiculos = len(set(n["veiculo"] for n in noticias))
    st.metric("🗞️ Veículos", veiculos)

with col4:
    st.metric(
        "📅 Período",
        "7 dias"
    )


st.divider()


# -----------------------------
# FILTROS
# -----------------------------

st.subheader("🔎 Filtrar notícias")

col1, col2, col3 = st.columns(3)

with col1:

    filtro = st.selectbox(
        "Monitoramento",
        ["Todos"] + list(FONTES.keys())
    )

with col2:

    busca = st.text_input(
        "Palavra-chave",
        placeholder="Ex.: saúde, educação, licitação..."
    )

with col3:

    limite_resultados = st.selectbox(
        "Exibir",
        [25, 50, 100, 200],
        index=1
    )


# -----------------------------
# APLICA FILTROS
# -----------------------------

filtradas = noticias

if filtro != "Todos":

    filtradas = [
        n for n in filtradas
        if n["monitoramento"] == filtro
    ]

if busca:

    termo = busca.lower()

    filtradas = [
        n for n in filtradas
        if termo in n["titulo"].lower()
    ]


total_filtradas = len(filtradas)

filtradas = filtradas[:limite_resultados]


# -----------------------------
# RESULTADOS
# -----------------------------

st.subheader(
    f"📰 {total_filtradas} notícias encontradas"
)

if not filtradas:

    st.info(
        "Nenhuma notícia encontrada com os filtros selecionados."
    )

else:

    for noticia in filtradas:

        data_formatada = ""

        if noticia["data"]:
            data_formatada = noticia["data"].strftime(
                "%d/%m/%Y %H:%M"
            )

        st.markdown(
            f"### {noticia['titulo']}"
        )

        col1, col2 = st.columns([5, 1])

        with col1:

            st.caption(
                f"🗞️ {noticia['veiculo']}  •  "
                f"🔎 {noticia['monitoramento']}  •  "
                f"📅 {data_formatada}"
            )

        with col2:

            st.link_button(
                "Ler matéria ↗",
                noticia["link"]
            )

        st.divider()
