import streamlit as st
import feedparser
from datetime import datetime, timedelta
import re


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Radar TCE-MG",
    page_icon="🏛️",
    layout="wide"
)


# ============================================================
# FONTES
# ============================================================

FONTES = {

    # Busca geral
    "TCE-MG":
        'https://news.google.com/rss/search?q=%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "TCE MG":
        'https://news.google.com/rss/search?q=%22TCE%20MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tribunal de Contas":
        'https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22%20%22Minas%20Gerais%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',


    # Veículos
    "Estado de Minas":
        'https://news.google.com/rss/search?q=site%3Aem.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Itatiaia":
        'https://news.google.com/rss/search?q=site%3Aitatiaia.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "O TEMPO":
        'https://news.google.com/rss/search?q=site%3Aotempo.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Hoje em Dia":
        'https://news.google.com/rss/search?q=site%3Ahojeemdia.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "G1 Minas":
        'https://news.google.com/rss/search?q=site%3Ag1.globo.com%2Fmg+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',


    # Pessoas
    "Durval Ângelo":
        'https://news.google.com/rss/search?q=%22Durval%20Ângelo%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Agostinho Patrus":
        'https://news.google.com/rss/search?q=%22Agostinho%20Patrus%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Gilberto Diniz":
        'https://news.google.com/rss/search?q=%22Gilberto%20Diniz%22%20TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Alencar da Silveira":
        'https://news.google.com/rss/search?q=%22Alencar%20da%20Silveira%22%20TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Ione Pinheiro":
        'https://news.google.com/rss/search?q=%22Ione%20Pinheiro%22%20TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tadeu Martins Leite":
        'https://news.google.com/rss/search?q=%22Tadeu%20Martins%20Leite%22%20TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tadeuzinho":
        'https://news.google.com/rss/search?q=%22Tadeuzinho%22%20TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',
}


# ============================================================
# PESSOAS
# ============================================================

PESSOAS = {

    "Conselheiros": [
        "Durval Ângelo",
        "Agostinho Patrus",
        "Gilberto Diniz",
        "Alencar da Silveira",
        "Ione Pinheiro",
    ],

    "Eleito / transição": [
        "Tadeu Martins Leite",
        "Tadeuzinho",
    ],

    "Conselheiros substitutos": [
        "Licurgo Mourão",
        "Hamilton Coelho",
        "Adonias Fernandes",
        "Victor Meyer",
    ],
}


# ============================================================
# TEMAS ESTRATÉGICOS
# ============================================================

TEMAS = {

    "⛏️ Mineração": [
        "mineração",
        "mineradora",
        "Vale",
        "CSN",
        "CFEM",
        "royalties",
        "barragem",
        "barragens",
    ],

    "🚰 Copasa": [
        "Copasa",
        "saneamento",
        "água",
        "abastecimento",
    ],

    "🏭 Estatais": [
        "Cemig",
        "Codemig",
        "empresa estatal",
        "estatal",
    ],

    "🏛️ Privatização": [
        "privatização",
        "privatizar",
        "desestatização",
        "venda da estatal",
    ],

    "🚌 Transporte": [
        "transporte",
        "ônibus",
        "metro",
        "metrô",
        "rodovia",
        "pedágio",
        "concessão",
        "mobilidade",
    ],

    "💰 Benefícios fiscais": [
        "benefícios fiscais",
        "benefício fiscal",
        "incentivos fiscais",
        "incentivo fiscal",
        "renúncia fiscal",
        "ICMS",
        "crédito presumido",
    ],

    "⚖️ Controle": [
        "auditoria",
        "fiscalização",
        "licitação",
        "contrato",
        "contas",
        "denúncia",
        "irregularidade",
        "multa",
        "ressarcimento",
        "julgamento",
        "acórdão",
        "determina",
        "recomenda",
    ],

    "🏥 Saúde": [
        "saúde",
        "hospital",
        "hospitais",
        "SUS",
        "medicamento",
        "médico",
    ],

    "🎓 Educação": [
        "educação",
        "escola",
        "escolas",
        "ensino",
        "universidade",
        "educacional",
    ],

    "🏗️ Obras públicas": [
        "obra pública",
        "obras públicas",
        "obras",
        "infraestrutura",
        "construção",
    ],
}


# ============================================================
# FUNÇÕES
# ============================================================

def limpar_texto(texto):

    if not texto:
        return ""

    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def obter_data(item):

    try:

        if (
            hasattr(item, "published_parsed")
            and item.published_parsed
        ):

            return datetime(
                *item.published_parsed[:6]
            )

    except Exception:
        pass

    return None


def extrair_veiculo(item):

    titulo = item.get(
        "title",
        ""
    )

    if " - " in titulo:

        return titulo.rsplit(
            " - ",
            1
        )[-1].strip()

    return "Fonte não identificada"


# ============================================================
# IDENTIFICA TEMAS
# ============================================================

def identificar_temas(titulo, resumo):

    texto = (
        titulo + " " + resumo
    ).lower()

    temas_encontrados = []

    for tema, palavras in TEMAS.items():

        encontrou = False

        for palavra in palavras:

            if palavra.lower() in texto:

                encontrou = True
                break

        if encontrou:

            temas_encontrados.append(
                tema
            )

    return temas_encontrados


# ============================================================
# IDENTIFICA PESSOAS
# ============================================================

def identificar_pessoas(titulo, resumo):

    texto = (
        titulo + " " + resumo
    ).lower()

    pessoas_encontradas = []

    for grupo, pessoas in PESSOAS.items():

        for pessoa in pessoas:

            if pessoa.lower() in texto:

                if pessoa not in pessoas_encontradas:

                    pessoas_encontradas.append(
                        pessoa
                    )

    return pessoas_encontradas


# ============================================================
# SCORE
# ============================================================

def calcular_relevancia(
    titulo,
    resumo,
    monitoramento,
    temas,
    pessoas
):

    texto = (
        titulo + " " + resumo
    ).lower()

    score = 15


    # --------------------------------------------------------
    # MENÇÃO DIRETA AO TRIBUNAL
    # --------------------------------------------------------

    if "tce-mg" in texto:

        score += 35

    elif "tce mg" in texto:

        score += 30

    elif "tribunal de contas" in texto:

        score += 25


    # --------------------------------------------------------
    # PESSOAS
    # --------------------------------------------------------

    score += len(pessoas) * 12


    # --------------------------------------------------------
    # TEMAS
    # --------------------------------------------------------

    score += len(temas) * 5


    # --------------------------------------------------------
    # TERMOS DE ATUAÇÃO
    # --------------------------------------------------------

    termos_acao = [

        "determina",
        "decide",
        "suspende",
        "condena",
        "multa",
        "auditoria",
        "fiscalização",
        "julgamento",
        "acórdão",
        "denúncia",
        "irregularidade",
        "recomenda",
        "processo",
        "ressarcimento",
        "contas",
    ]

    for termo in termos_acao:

        if termo in texto:

            score += 5


    # --------------------------------------------------------
    # VALOR FINANCEIRO
    # --------------------------------------------------------

    if "r$" in texto:

        score += 5


    # --------------------------------------------------------
    # BUSCA ESPECÍFICA
    # --------------------------------------------------------

    if monitoramento in [

        "Durval Ângelo",
        "Agostinho Patrus",
        "Gilberto Diniz",
        "Alencar da Silveira",
        "Ione Pinheiro",
        "Tadeu Martins Leite",
        "Tadeuzinho",

    ]:

        score += 8


    return min(
        score,
        100
    )


def classificar(score):

    if score >= 85:

        return "🔴 Crítica"

    if score >= 65:

        return "🟠 Alta"

    if score >= 45:

        return "🟡 Média"

    return "⚪ Menção"


# ============================================================
# COLETA
# ============================================================

@st.cache_data(ttl=300)
def buscar_noticias():

    noticias = []

    links = set()

    limite = (
        datetime.now()
        - timedelta(days=7)
    )


    for nome, url in FONTES.items():

        try:

            feed = feedparser.parse(
                url
            )

        except Exception:

            continue


        for item in feed.entries:

            link = item.get(
                "link",
                ""
            )


            # Remove duplicadas
            if (
                not link
                or link in links
            ):

                continue


            data = obter_data(
                item
            )


            # Apenas últimos 7 dias
            if (
                data
                and data < limite
            ):

                continue


            links.add(
                link
            )


            titulo = item.get(
                "title",
                "Sem título"
            )


            resumo = limpar_texto(
                item.get(
                    "summary",
                    ""
                )
            )


            temas = identificar_temas(
                titulo,
                resumo
            )


            pessoas = identificar_pessoas(
                titulo,
                resumo
            )


            score = calcular_relevancia(

                titulo,

                resumo,

                nome,

                temas,

                pessoas
            )


            noticias.append({

                "titulo":
                    titulo,

                "resumo":
                    resumo,

                "link":
                    link,

                "monitoramento":
                    nome,

                "veiculo":
                    extrair_veiculo(
                        item
                    ),

                "data":
                    data,

                "score":
                    score,

                "classificacao":
                    classificar(
                        score
                    ),

                "temas":
                    temas,

                "pessoas":
                    pessoas,
            })


    # Ordena primeiro por relevância
    # e depois por data

    noticias.sort(

        key=lambda x: (

            x["score"],

            x["data"]
            or datetime.min

        ),

        reverse=True
    )


    return noticias


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "🏛️ Radar TCE-MG"
)

st.caption(
    "Monitoramento inteligente de notícias "
    "relacionadas ao Tribunal de Contas de Minas Gerais"
)


col1, col2 = st.columns(
    [1, 5]
)


with col1:

    if st.button(
        "🔄 Atualizar agora"
    ):

        st.cache_data.clear()

        st.rerun()


with col2:

    st.caption(
        "Últimos 7 dias • atualização aproximada a cada 5 minutos"
    )


st.divider()


# ============================================================
# BUSCA
# ============================================================

noticias = buscar_noticias()


# ============================================================
# MÉTRICAS
# ============================================================

criticas = len([

    n for n in noticias

    if n["score"] >= 85

])


altas = len([

    n for n in noticias

    if 65 <= n["score"] < 85

])


medias = len([

    n for n in noticias

    if 45 <= n["score"] < 65

])


mencoes = len([

    n for n in noticias

    if n["score"] < 45

])


col1, col2, col3, col4, col5 = st.columns(
    5
)


with col1:

    st.metric(
        "📰 Notícias",
        len(noticias)
    )


with col2:

    st.metric(
        "🔴 Críticas",
        criticas
    )


with col3:

    st.metric(
        "🟠 Altas",
        altas
    )


with col4:

    st.metric(
        "🟡 Médias",
        medias
    )


with col5:

    st.metric(
        "⚪ Menções",
        mencoes
    )


st.divider()


# ============================================================
# FILTROS
# ============================================================

st.subheader(
    "🔎 Monitorar"
)


col1, col2, col3 = st.columns(
    3
)


with col1:

    filtro_pessoa = st.selectbox(

        "👤 Pessoa",

        [
            "Todas"
        ]
        + [
            pessoa
            for grupo in PESSOAS.values()
            for pessoa in grupo
        ]
    )


with col2:

    filtro_tema = st.selectbox(

        "🏷️ Tema",

        [
            "Todos"
        ]
        + list(
            TEMAS.keys()
        )
    )


with col3:

    filtro_fonte = st.selectbox(

        "🗞️ Fonte",

        [
            "Todas"
        ]
        + list(
            FONTES.keys()
        )
    )


col1, col2 = st.columns(
    2
)


with col1:

    filtro_relevancia = st.selectbox(

        "🎯 Relevância",

        [
            "Todas",
            "🔴 Crítica",
            "🟠 Alta",
            "🟡 Média",
            "⚪ Menção"
        ]
    )


with col2:

    busca = st.text_input(

        "🔍 Buscar palavra",

        placeholder=
        "Ex.: Copasa, mineração, ônibus..."
    )


# ============================================================
# APLICA FILTROS
# ============================================================

filtradas = noticias


if filtro_pessoa != "Todas":

    filtradas = [

        n for n in filtradas

        if filtro_pessoa
        in n["pessoas"]

    ]


if filtro_tema != "Todos":

    filtradas = [

        n for n in filtradas

        if filtro_tema
        in n["temas"]

    ]


if filtro_fonte != "Todas":

    filtradas = [

        n for n in filtradas

        if n["monitoramento"]
        == filtro_fonte

    ]


if filtro_relevancia != "Todas":

    filtradas = [

        n for n in filtradas

        if n["classificacao"]
        == filtro_relevancia

    ]


if busca:

    termo = busca.lower()

    filtradas = [

        n for n in filtradas

        if termo
        in (
            n["titulo"]
            + " "
            + n["resumo"]
        ).lower()

    ]


# ============================================================
# RESULTADOS
# ============================================================

st.subheader(

    f"📰 {len(filtradas)} notícias"
)


if not filtradas:

    st.info(
        "Nenhuma notícia encontrada "
        "com os filtros selecionados."
    )


else:

    for noticia in filtradas:

        data_formatada = ""


        if noticia["data"]:

            data_formatada = (

                noticia["data"]
                .strftime(
                    "%d/%m/%Y %H:%M"
                )

            )


        # ----------------------------------------------------
        # TÍTULO E SCORE
        # ----------------------------------------------------

        st.markdown(

            f"### "
            f"{noticia['classificacao']} "
            f"**{noticia['score']}/100**"
        )


        st.markdown(

            f"**{noticia['titulo']}**"
        )


        # ----------------------------------------------------
        # INFORMAÇÕES
        # ----------------------------------------------------

        st.caption(

            f"🗞️ {noticia['veiculo']}  •  "
            f"🔎 {noticia['monitoramento']}  •  "
            f"📅 {data_formatada}"
        )


        # ----------------------------------------------------
        # TAGS DE PESSOAS
        # ----------------------------------------------------

        if noticia["pessoas"]:

            st.markdown(
                " ".join(
                    [
                        f"`👤 {p}`"
                        for p in noticia["pessoas"]
                    ]
                )
            )


        # ----------------------------------------------------
        # TAGS DE TEMAS
        # ----------------------------------------------------

        if noticia["temas"]:

            st.markdown(
                " ".join(
                    [
                        f"`{tema}`"
                        for tema in noticia["temas"]
                    ]
                )
            )


        # ----------------------------------------------------
        # RESUMO
        # ----------------------------------------------------

        if noticia["resumo"]:

            resumo = noticia["resumo"]


            if len(resumo) > 500:

                resumo = (
                    resumo[:500]
                    + "..."
                )


            st.write(
                resumo
            )


        # ----------------------------------------------------
        # LINK
        # ----------------------------------------------------

        st.link_button(

            "Ler matéria ↗",

            noticia["link"]
        )


        st.divider()
