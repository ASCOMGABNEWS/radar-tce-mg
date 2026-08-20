import streamlit as st
import feedparser
from datetime import datetime, timedelta

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


# --------------------------------
# SCORE DE RELEVÂNCIA
# --------------------------------

def calcular_relevancia(titulo, monitoramento):

    texto = titulo.lower()

    score = 20

    # Menções diretas ao Tribunal
    if "tce-mg" in texto:
        score += 40

    if "tce mg" in texto:
        score += 35

    if "tribunal de contas" in texto:
        score += 30

    # Conselheiros
    nomes = [
        "durval ângelo",
        "agostinho patrus",
        "gilberto diniz"
    ]

    for nome in nomes:
        if nome in texto:
            score += 25

    # Termos de fiscalização
    termos_importantes = [
        "decisão",
        "julgamento",
        "auditoria",
        "fiscalização",
        "determina",
        "recomenda",
        "irregularidade",
        "contas",
        "denúncia",
        "acórdão",
        "condena"
    ]

    for termo in termos_importantes:
        if termo in texto:
            score += 8

    # Temas muito comuns no universo do Tribunal
    temas = [
        "licitação",
        "contrato",
        "prefeitura",
        "saúde",
        "educação",
        "transporte",
        "obra pública",
        "servidor",
        "dinheiro público"
    ]

    for tema in temas:
        if tema in texto:
            score += 4

    # Pequeno bônus se a própria busca foi feita
    # especificamente pelo nome de alguém
    if monitoramento in [
        "Durval Ângelo",
        "Agostinho Patrus",
        "Gilberto Diniz"
    ]:
        score += 10

    return min(score, 100)


def classificar(score):

    if score >= 80:
        return "🔴 Alta"

    if score >= 50:
        return "🟠 Média"

    return "⚪ Menção"


# --------------------------------
# DATA
# --------------------------------

def obter_data(item):

    try:
        if hasattr(item, "published_parsed") and item.published_parsed:
            return datetime(*item.published_parsed[:6])
    except Exception:
        pass

    return None


# --------------------------------
# VEÍCULO
# --------------------------------

def extrair_veiculo(item):

    titulo = item.get("title", "")

    if " - " in titulo:
        partes = titulo.rsplit(" - ", 1)
        return partes[-1].strip()

    return "Fonte não identificada"


# --------------------------------
# COLETA
# --------------------------------

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

            titulo = item.get(
                "title",
                "Sem título"
            )

            score = calcular_relevancia(
                titulo,
                nome
            )

            noticias.append({
                "titulo": titulo,
                "link": link,
                "monitoramento": nome,
                "veiculo": extrair_veiculo(item),
                "data": data,
                "score": score,
                "classificacao": classificar(score)
            })

    noticias.sort(
        key=lambda x: (
            x["score"],
            x["data"] or datetime.min
        ),
        reverse=True
    )

    return noticias


# --------------------------------
# CABEÇALHO
# --------------------------------

st.title("🏛️ Radar TCE-MG")

st.caption(
    "Monitoramento inteligente de notícias relacionadas "
    "ao Tribunal de Contas de Minas Gerais"
)

col_botao, col_info = st.columns([1, 5])

with col_botao:

    if st.button("🔄 Atualizar agora"):

        st.cache_data.clear()
        st.rerun()

with col_info:

    st.caption(
        "Coleta: últimos 7 dias • atualização aproximada: 5 minutos"
    )

st.divider()


# --------------------------------
# COLETA
# --------------------------------

noticias = buscar_noticias()


# --------------------------------
# MÉTRICAS
# --------------------------------

alta = len([
    n for n in noticias
    if n["score"] >= 80
])

media = len([
    n for n in noticias
    if 50 <= n["score"] < 80
])

mencao = len([
    n for n in noticias
    if n["score"] < 50
])


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📰 Notícias", len(noticias))

with col2:
    st.metric("🔴 Alta", alta)

with col3:
    st.metric("🟠 Média", media)

with col4:
    st.metric("⚪ Menção", mencao)


st.divider()


# --------------------------------
# FILTROS
# --------------------------------

st.subheader("🔎 Filtrar")

col1, col2, col3 = st.columns(3)

with col1:

    filtro = st.selectbox(
        "Monitoramento",
        ["Todos"] + list(FONTES.keys())
    )

with col2:

    filtro_relevancia = st.selectbox(
        "Relevância",
        [
            "Todas",
            "🔴 Alta",
            "🟠 Média",
            "⚪ Menção"
        ]
    )

with col3:

    busca = st.text_input(
        "Palavra-chave",
        placeholder="Ex.: saúde, educação, licitação..."
    )


# --------------------------------
# APLICA FILTROS
# --------------------------------

filtradas = noticias

if filtro != "Todos":

    filtradas = [
        n for n in filtradas
        if n["monitoramento"] == filtro
    ]

if filtro_relevancia != "Todas":

    filtradas = [
        n for n in filtradas
        if n["classificacao"] == filtro_relevancia
    ]

if busca:

    termo = busca.lower()

    filtradas = [
        n for n in filtradas
        if termo in n["titulo"].lower()
    ]


# --------------------------------
# RESULTADOS
# --------------------------------

st.subheader(
    f"📰 {len(filtradas)} notícias"
)


if not filtradas:

    st.info(
        "Nenhuma notícia encontrada."
    )

else:

    for noticia in filtradas:

        data_formatada = ""

        if noticia["data"]:

            data_formatada = noticia["data"].strftime(
                "%d/%m/%Y %H:%M"
            )

        st.markdown(
            f"### {noticia['classificacao']} "
            f"**{noticia['score']}/100**"
        )

        st.markdown(
            f"**{noticia['titulo']}**"
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
