import streamlit as st
import feedparser
from datetime import datetime, timedelta
import re
from collections import Counter
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import cm



# ============================================================
# CONFIGURAÇÃO
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

    # --------------------------------------------------------
    # IMPRENSA MINEIRA
    # --------------------------------------------------------

    "Estado de Minas":
        'https://news.google.com/rss/search?q=site%3Aem.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Itatiaia":
        'https://news.google.com/rss/search?q=site%3Aitatiaia.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "O TEMPO":
        'https://news.google.com/rss/search?q=site%3Aotempo.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Hoje em Dia":
        'https://news.google.com/rss/search?q=site%3Ahojeemdia.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tribuna de Minas":
        'https://news.google.com/rss/search?q=site%3Atribunademinas.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Diário do Comércio":
        'https://news.google.com/rss/search?q=site%3Adiariodocomercio.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "BHAZ":
        'https://news.google.com/rss/search?q=site%3Abhaz.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Agência Minas":
        'https://news.google.com/rss/search?q=site%3Aagenciaminas.mg.gov.br+%22Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "O Fator":
        'https://news.google.com/rss/search?q=site%3Aofator.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Edição do Brasil":
        'https://news.google.com/rss/search?q=site%3Aedicaodobrasil.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Moon BH":
        'https://news.google.com/rss/search?q=site%3Amoonbh.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',


    # --------------------------------------------------------
    # IMPRENSA NACIONAL
    # --------------------------------------------------------

    "G1 Minas":
        'https://news.google.com/rss/search?q=site%3Ag1.globo.com%2Fmg+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Folha de S.Paulo":
        'https://news.google.com/rss/search?q=site%3Afolha.uol.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "O Globo":
        'https://news.google.com/rss/search?q=site%3Aoglobo.globo.com+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Correio Braziliense":
        'https://news.google.com/rss/search?q=site%3Acorreiobraziliense.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Poder360":
        'https://news.google.com/rss/search?q=site%3Apoder360.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "O Antagonista":
        'https://news.google.com/rss/search?q=site%3Aoantagonista.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Brasil de Fato":
        'https://news.google.com/rss/search?q=site%3Abrasildefato.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "revista piauí":
        'https://news.google.com/rss/search?q=site%3Apiaui.folha.uol.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "JOTA":
        'https://news.google.com/rss/search?q=site%3Ajota.info+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Migalhas":
        'https://news.google.com/rss/search?q=site%3Amigalhas.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "O Bastidor":
        'https://news.google.com/rss/search?q=site%3Aobastidor.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Intercept Brasil":
        'https://news.google.com/rss/search?q=site%3Aintercept.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Bem Minas":
        'https://news.google.com/rss/search?q=site%3Abemminas.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',


    # --------------------------------------------------------
    # BUSCAS GERAIS
    # --------------------------------------------------------

    "TCE-MG":
        'https://news.google.com/rss/search?q=%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "TCE MG":
        'https://news.google.com/rss/search?q=%22TCE%20MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tribunal de Contas MG":
        'https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22+%22Minas%20Gerais%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',


    # --------------------------------------------------------
    # PESSOAS
    # --------------------------------------------------------

    "Durval Ângelo":
        'https://news.google.com/rss/search?q=%22Durval%20Ângelo%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Agostinho Patrus":
        'https://news.google.com/rss/search?q=%22Agostinho%20Patrus%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Gilberto Diniz":
        'https://news.google.com/rss/search?q=%22Gilberto%20Diniz%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Alencar da Silveira":
        'https://news.google.com/rss/search?q=%22Alencar%20da%20Silveira%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Ione Pinheiro":
        'https://news.google.com/rss/search?q=%22Ione%20Pinheiro%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tadeu Martins Leite / Tadeuzinho":
        'https://news.google.com/rss/search?q=%22Tadeu%20Martins%20Leite%22+OR+%22Tadeuzinho%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Licurgo Mourão":
        'https://news.google.com/rss/search?q=%22Licurgo%20Mourão%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Hamilton Coelho":
        'https://news.google.com/rss/search?q=%22Hamilton%20Coelho%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Adonias Fernandes":
        'https://news.google.com/rss/search?q=%22Adonias%20Fernandes%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Telmo Passareli":
        'https://news.google.com/rss/search?q=%22Telmo%20Passareli%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419',
}


# ============================================================
# PESSOAS MONITORADAS
# ============================================================

PESSOAS = {

    "Conselheiros": {

        "Durval Ângelo": [
            "Durval Ângelo"
        ],

        "Agostinho Patrus": [
            "Agostinho Patrus"
        ],

        "Gilberto Diniz": [
            "Gilberto Diniz"
        ],

        "Alencar da Silveira": [
            "Alencar da Silveira",
            "Alencar Silveira"
        ],

        "Ione Pinheiro": [
            "Ione Pinheiro"
        ],
    },

    "Eleito / transição": {

        "Tadeu Martins Leite (Tadeuzinho)": [
            "Tadeu Martins Leite",
            "Tadeuzinho",
            "Tadeu Leite"
        ],
    },

    "Conselheiros substitutos": {

        "Licurgo Joseph Mourão de Oliveira": [
            "Licurgo Joseph Mourão",
            "Licurgo Mourão"
        ],

        "Hamilton Antônio Coelho": [
            "Hamilton Antônio Coelho",
            "Hamilton Coelho"
        ],

        "Adonias Fernandes Monteiro": [
            "Adonias Fernandes Monteiro",
            "Adonias Fernandes"
        ],

        "Telmo de Moura Passareli": [
            "Telmo de Moura Passareli",
            "Telmo Passareli"
        ],
    }
}


# ============================================================
# RELAÇÃO BUSCA → PESSOA
# ============================================================

MAPA_FONTE_PESSOA = {

    "Durval Ângelo":
        "Durval Ângelo",

    "Agostinho Patrus":
        "Agostinho Patrus",

    "Gilberto Diniz":
        "Gilberto Diniz",

    "Alencar da Silveira":
        "Alencar da Silveira",

    "Ione Pinheiro":
        "Ione Pinheiro",

    "Tadeu Martins Leite / Tadeuzinho":
        "Tadeu Martins Leite (Tadeuzinho)",

    "Licurgo Mourão":
        "Licurgo Joseph Mourão de Oliveira",

    "Hamilton Coelho":
        "Hamilton Antônio Coelho",

    "Adonias Fernandes":
        "Adonias Fernandes Monteiro",

    "Telmo Passareli":
        "Telmo de Moura Passareli",
}


# ============================================================
# TEMAS
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
        "barragens"
    ],

    "🚰 Copasa": [
        "Copasa",
        "saneamento",
        "água",
        "abastecimento"
    ],

    "🏭 Estatais": [
        "Cemig",
        "Codemig",
        "empresa estatal",
        "estatal"
    ],

    "🏛️ Privatização": [
        "privatização",
        "privatizar",
        "desestatização",
        "venda da estatal"
    ],

    "🚌 Transporte": [
        "transporte",
        "ônibus",
        "metro",
        "metrô",
        "rodovia",
        "pedágio",
        "concessão",
        "mobilidade"
    ],

    "💰 Benefícios fiscais": [
        "benefícios fiscais",
        "benefício fiscal",
        "incentivos fiscais",
        "incentivo fiscal",
        "renúncia fiscal",
        "ICMS",
        "crédito presumido"
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
        "determina"
    ],

    "🏥 Saúde": [
        "saúde",
        "hospital",
        "hospitais",
        "SUS",
        "medicamento"
    ],

    "🎓 Educação": [
        "educação",
        "escola",
        "escolas",
        "ensino",
        "universidade",
        "educacional"
    ],

    "🏗️ Obras públicas": [
        "obra pública",
        "obras públicas",
        "obras",
        "infraestrutura",
        "construção"
    ],

    "🏢 Instituições": [
        "Governo de Minas",
        "Governo de MG",
        "Assembleia Legislativa",
        "ALMG",
        "TCU",
        "STF",
        "STJ",
        "Ministério Público",
        "MPMG",
        "Prefeitura de Belo Horizonte",
        "Cemig",
        "Codemig",
        "Vale"
    ],
}


# ============================================================
# FUNÇÕES
# ============================================================

def limpar_texto(texto):

    if not texto:
        return ""

    texto = re.sub(
        r"<[^>]+>",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

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


def identificar_temas(
    titulo,
    resumo
):

    texto = (
        titulo
        + " "
        + resumo
    ).lower()

    encontrados = []

    for tema, palavras in TEMAS.items():

        for palavra in palavras:

            if palavra.lower() in texto:

                encontrados.append(
                    tema
                )

                break

    return encontrados


def identificar_instituicoes(
    titulo,
    resumo
):

    texto = (
        titulo
        + " "
        + resumo
    ).lower()

    mapa = {
        "Governo de Minas": [
            "governo de minas",
            "governo de mg"
        ],
        "ALMG": [
            "assembleia legislativa",
            "almg"
        ],
        "TCU": [
            "tcu",
            "tribunal de contas da união"
        ],
        "STF": [
            "stf",
            "supremo tribunal federal"
        ],
        "STJ": [
            "stj",
            "superior tribunal de justiça"
        ],
        "Ministério Público": [
            "ministério público",
            "mpmg"
        ],
        "Prefeitura de Belo Horizonte": [
            "prefeitura de belo horizonte",
            "prefeitura de bh"
        ],
        "Cemig": [
            "cemig"
        ],
        "Copasa": [
            "copasa"
        ],
        "Codemig": [
            "codemig"
        ],
        "Vale": [
            "vale"
        ],
    }

    encontrados = []

    for instituicao, variacoes in mapa.items():

        for variacao in variacoes:

            if variacao in texto:

                encontrados.append(instituicao)
                break

    return encontrados


def identificar_pessoas(
    titulo,
    resumo
):

    texto = (
        titulo
        + " "
        + resumo
    ).lower()

    encontrados = []

    for grupo in PESSOAS.values():

        for pessoa, variacoes in grupo.items():

            for variacao in variacoes:

                if (
                    variacao.lower()
                    in texto
                ):

                    if pessoa not in encontrados:

                        encontrados.append(
                            pessoa
                        )

                    break

    return encontrados


def calcular_relevancia(
    titulo,
    resumo,
    monitoramento,
    temas,
    pessoas
):

    texto = (
        titulo
        + " "
        + resumo
    ).lower()

    score = 15


    if "tce-mg" in texto:

        score += 35

    elif "tce mg" in texto:

        score += 30

    elif "tribunal de contas" in texto:

        score += 25


    score += (
        len(pessoas) * 12
    )


    score += (
        len(temas) * 5
    )


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


    if "r$" in texto:

        score += 5


    return min(
        score,
        100
    )


def classificar(score):

    if score >= 85:

        return "🔴"

    if score >= 65:

        return "🟠"

    if score >= 45:

        return "🟡"

    return "⚪"


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


            if (
                not link
                or link in links
            ):

                continue


            data = obter_data(
                item
            )


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

            instituicoes = identificar_instituicoes(
                titulo,
                resumo
            )


            # ------------------------------------------------
            # CORREÇÃO DAS PESSOAS
            # ------------------------------------------------

            if nome in MAPA_FONTE_PESSOA:

                pessoa_fonte = (
                    MAPA_FONTE_PESSOA[
                        nome
                    ]
                )

                if pessoa_fonte not in pessoas:

                    pessoas.append(
                        pessoa_fonte
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

                "bolinha":
                    classificar(
                        score
                    ),

                "temas":
                    temas,

                "pessoas":
                    pessoas,

                "instituicoes":
                    instituicoes,
            })


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
# VISUAL — PAINÉIS
# ============================================================

st.markdown("""
<style>

.insight-box {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 16px 18px;
    margin: 8px 0 14px 0;
}

.insight-title {
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 5px;
}

.insight-subtitle {
    font-size: 12px;
    opacity: .68;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
.nav-note {
    font-size: 12px;
    opacity: .65;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

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
        "Monitoramento em tempo real - Gabinete Agostinho Patrus • "
        "atualização automática a cada 5 minutos"
    )


st.divider()


# ============================================================
# COLETA
# ============================================================

noticias = buscar_noticias()


# ============================================================
# PERÍODO
# ============================================================

periodo = st.radio(

    "🕐 Período",

    [
        "Últimas 6 horas",
        "Últimas 24 horas",
        "Últimos 3 dias",
        "Últimos 7 dias",
    ],

    horizontal=True
)


agora = datetime.now()


if periodo == "Últimas 6 horas":

    limite_periodo = (
        agora
        - timedelta(hours=6)
    )

elif periodo == "Últimas 24 horas":

    limite_periodo = (
        agora
        - timedelta(hours=24)
    )

elif periodo == "Últimos 3 dias":

    limite_periodo = (
        agora
        - timedelta(days=3)
    )

else:

    limite_periodo = (
        agora
        - timedelta(days=7)
    )


noticias_periodo = [

    n for n in noticias

    if (
        n["data"]
        and n["data"]
        >= limite_periodo
    )
]



# ============================================================
# CONTADORES PARA O PAINEL
# ============================================================

contador_temas = Counter()
contador_pessoas = Counter()

for noticia in noticias_periodo:

    for tema in noticia["temas"]:
        contador_temas[tema] += 1

    for pessoa in noticia["pessoas"]:
        contador_pessoas[pessoa] += 1

# ============================================================
# PAINEL INTERATIVO
# ============================================================

tabs = st.tabs([
    "🏠 Radar",
    "📰 Notícias",
    "👥 Pessoas",
    "🏷️ Assuntos",
    "🗞️ Veículos",
    "🏛️ Instituições",
    "📄 Clipping",
])


# ============================================================
# ABA RADAR
# ============================================================

with tabs[0]:

    criticas = [
        n for n in noticias_periodo
        if n["score"] >= 85
    ]

    altas = [
        n for n in noticias_periodo
        if 65 <= n["score"] < 85
    ]

    st.subheader("🚨 O que merece atenção")

    atencao = [
        n for n in noticias_periodo
        if n["score"] >= 65
    ]

    if atencao:

        for noticia in atencao[:6]:

            data_atencao = ""

            if noticia["data"]:
                data_atencao = noticia["data"].strftime(
                    "%d/%m %H:%M"
                )

            st.markdown(
                f"{noticia['bolinha']} "
                f"**{noticia['titulo']}**"
            )

            st.caption(
                f"🗞️ {noticia['veiculo']} • "
                f"📅 {data_atencao}"
            )

            st.link_button(
                "Ler matéria ↗",
                noticia["link"]
            )

            st.divider()

    else:

        st.info(
            "Nenhuma matéria de alta relevância "
            "no período selecionado."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📰 Notícias",
            len(noticias_periodo)
        )

    with col2:
        st.metric(
            "🔴 Críticas",
            len(criticas)
        )

    with col3:
        st.metric(
            "🟠 Alta",
            len(altas)
        )

    with col4:
        st.metric(
            "👥 Pessoas citadas",
            len(contador_pessoas)
            if "contador_pessoas" in globals()
            else 0
        )


# ============================================================
# ABA NOTÍCIAS
# ============================================================

with tabs[1]:

    st.subheader("📰 Todas as notícias")

    st.caption(
        "Use os filtros abaixo para refinar o monitoramento."
    )

    todas_pessoas = []

    for grupo in PESSOAS.values():
        todas_pessoas.extend(grupo.keys())

    col1, col2, col3 = st.columns(3)

    with col1:

        filtro_pessoa = st.selectbox(
            "👤 Pessoa",
            ["Todas"] + todas_pessoas,
            key="tab_pessoa"
        )

    with col2:

        filtro_tema = st.selectbox(
            "🏷️ Tema",
            ["Todos"] + list(TEMAS.keys()),
            key="tab_tema"
        )

    with col3:

        filtro_fonte = st.selectbox(
            "🗞️ Fonte",
            ["Todas"] + list(FONTES.keys()),
            key="tab_fonte"
        )

    col1, col2 = st.columns(2)

    with col1:

        filtro_relevancia = st.selectbox(
            "🎯 Relevância",
            [
                "Todas",
                "🔴 Crítica",
                "🟠 Alta",
                "🟡 Média",
                "⚪ Menção"
            ],
            key="tab_relevancia"
        )

    with col2:

        busca = st.text_input(
            "🔍 Buscar palavra",
            placeholder="Ex.: Copasa, mineração, transporte...",
            key="tab_busca"
        )

    apenas_relevantes = st.checkbox(
        "🎯 Apenas relevantes (🔴 + 🟠)",
        key="tab_apenas_relevantes"
    )

    filtradas_tabs = noticias_periodo

    if filtro_pessoa != "Todas":
        filtradas_tabs = [
            n for n in filtradas_tabs
            if filtro_pessoa in n["pessoas"]
        ]

    if filtro_tema != "Todos":
        filtradas_tabs = [
            n for n in filtradas_tabs
            if filtro_tema in n["temas"]
        ]

    if filtro_fonte != "Todas":
        filtradas_tabs = [
            n for n in filtradas_tabs
            if n["monitoramento"] == filtro_fonte
        ]

    if filtro_relevancia != "Todas":

        mapa_relevancia = {
            "🔴 Crítica": "🔴",
            "🟠 Alta": "🟠",
            "🟡 Média": "🟡",
            "⚪ Menção": "⚪",
        }

        filtradas_tabs = [
            n for n in filtradas_tabs
            if n["bolinha"] ==
            mapa_relevancia[filtro_relevancia]
        ]

    if apenas_relevantes:

        filtradas_tabs = [
            n for n in filtradas_tabs
            if n["score"] >= 65
        ]

    if busca:

        termo = busca.lower()

        filtradas_tabs = [
            n for n in filtradas_tabs
            if termo in (
                n["titulo"]
                + " "
                + n["resumo"]
            ).lower()
        ]

    st.write(
        f"**{len(filtradas_tabs)} notícias encontradas**"
    )

    for noticia in filtradas_tabs:

        data_formatada = ""

        if noticia["data"]:
            data_formatada = noticia["data"].strftime(
                "%d/%m/%Y %H:%M"
            )

        st.markdown(
            f"### {noticia['bolinha']} "
            f"**{noticia['titulo']}**"
        )

        st.caption(
            f"🗞️ {noticia['veiculo']} • "
            f"📅 {data_formatada}"
        )

        if noticia["pessoas"]:

            st.markdown(
                " ".join(
                    [
                        f"`👤 {p}`"
                        for p in noticia["pessoas"]
                    ]
                )
            )

        if noticia["temas"]:

            st.markdown(
                " ".join(
                    [
                        f"`{tema}`"
                        for tema in noticia["temas"]
                    ]
                )
            )

        resumo = noticia["resumo"]

        if len(resumo) > 500:
            resumo = resumo[:500] + "..."

        if resumo:
            st.write(resumo)

        st.link_button(
            "Ler matéria ↗",
            noticia["link"]
        )

        st.divider()


# ============================================================
# ABA PESSOAS
# ============================================================

with tabs[2]:

    st.subheader("👥 Pessoas mais citadas")

    contador_pessoas_tabs = Counter()

    for noticia in noticias_periodo:

        for pessoa in noticia["pessoas"]:
            contador_pessoas_tabs[pessoa] += 1

    if contador_pessoas_tabs:

        for pessoa, quantidade in contador_pessoas_tabs.most_common():

            if st.button(
                f"👤 {pessoa}  •  {quantidade} notícia(s)",
                key=f"pessoa_{pessoa}"
            ):

                st.session_state["pessoa_selecionada"] = pessoa

        pessoa_selecionada = st.session_state.get(
            "pessoa_selecionada"
        )

        if pessoa_selecionada:

            st.divider()

            st.subheader(
                f"Notícias sobre {pessoa_selecionada}"
            )

            for noticia in noticias_periodo:

                if pessoa_selecionada in noticia["pessoas"]:

                    st.markdown(
                        f"{noticia['bolinha']} "
                        f"**{noticia['titulo']}**"
                    )

                    st.caption(
                        f"{noticia['veiculo']}"
                    )

                    st.link_button(
                        "Ler matéria ↗",
                        noticia["link"],
                        key=f"pessoa_link_{hash(noticia['link'])}"
                    )


# ============================================================
# ABA ASSUNTOS
# ============================================================

with tabs[3]:

    st.subheader("🏷️ Assuntos em destaque")

    contador_temas_tabs = Counter()

    for noticia in noticias_periodo:

        for tema in noticia["temas"]:
            contador_temas_tabs[tema] += 1

    if contador_temas_tabs:

        for tema, quantidade in contador_temas_tabs.most_common():

            if st.button(
                f"{tema}  •  {quantidade} notícia(s)",
                key=f"tema_{tema}"
            ):

                st.session_state["tema_selecionado"] = tema

        tema_selecionado = st.session_state.get(
            "tema_selecionado"
        )

        if tema_selecionado:

            st.divider()

            st.subheader(
                f"Notícias sobre {tema_selecionado}"
            )

            for noticia in noticias_periodo:

                if tema_selecionado in noticia["temas"]:

                    st.markdown(
                        f"{noticia['bolinha']} "
                        f"**{noticia['titulo']}**"
                    )

                    st.caption(
                        noticia["veiculo"]
                    )

                    st.link_button(
                        "Ler matéria ↗",
                        noticia["link"],
                        key=f"tema_link_{hash(noticia['link'])}"
                    )


# ============================================================
# ABA VEÍCULOS
# ============================================================

with tabs[4]:

    st.subheader("🗞️ Veículos que mais repercutiram")

    contador_veiculos_tabs = Counter()

    for noticia in noticias_periodo:

        veiculo = noticia["veiculo"]

        if veiculo:
            contador_veiculos_tabs[veiculo] += 1

    veiculo_selecionado = st.selectbox(
        "Escolha um veículo para ver as matérias",
        ["Todos"] + [
            v for v, _ in contador_veiculos_tabs.most_common()
        ],
        key="veiculo_tab"
    )

    for veiculo, quantidade in contador_veiculos_tabs.most_common():

        if veiculo_selecionado != "Todos" and veiculo != veiculo_selecionado:
            continue

        st.markdown(
            f"**{veiculo}** — {quantidade} matéria(s)"
        )

        for noticia in noticias_periodo:

            if noticia["veiculo"] == veiculo:

                st.markdown(
                    f"{noticia['bolinha']} "
                    f"**{noticia['titulo']}**"
                )

                st.link_button(
                    "Ler matéria ↗",
                    noticia["link"],
                    key=f"veiculo_link_{hash(noticia['link'])}"
                )


# ============================================================
# ABA INSTITUIÇÕES
# ============================================================

with tabs[5]:

    st.subheader("🏛️ Instituições mais citadas")

    contador_instituicoes_tabs = Counter()

    for noticia in noticias_periodo:

        for instituicao in noticia.get(
            "instituicoes",
            []
        ):

            contador_instituicoes_tabs[instituicao] += 1

    if contador_instituicoes_tabs:

        for instituicao, quantidade in (
            contador_instituicoes_tabs.most_common()
        ):

            st.markdown(
                f"**🏛️ {instituicao}** — "
                f"{quantidade} citação(ões)"
            )

            with st.expander(
                f"Ver matérias — {instituicao}"
            ):

                for noticia in noticias_periodo:

                    if instituicao in noticia.get(
                        "instituicoes",
                        []
                    ):

                        st.markdown(
                            f"{noticia['bolinha']} "
                            f"**{noticia['titulo']}**"
                        )

                        st.link_button(
                            "Ler matéria ↗",
                            noticia["link"],
                            key=f"inst_link_{hash(noticia['link'])}"
                        )


# ============================================================
# ABA CLIPPING
# ============================================================

with tabs[6]:

    st.subheader("📄 Clipping")

    st.write(
        "O PDF será gerado com o recorte de notícias "
        "selecionado no painel."
    )

    pdf_bytes = gerar_pdf_clipping(
        noticias_periodo
    )

    st.download_button(
        label="📄 Baixar clipping em PDF",
        data=pdf_bytes,
        file_name=(
            f"clipping_tce_mg_"
            f"{datetime.now().strftime('%Y-%m-%d')}.pdf"
        ),
        mime="application/pdf",
    )




# ============================================================
# CONTADORES
# ============================================================

contador_temas = Counter()

contador_pessoas = Counter()


for noticia in noticias_periodo:

    for tema in noticia["temas"]:

        contador_temas[
            tema
        ] += 1


    for pessoa in noticia["pessoas"]:

        contador_pessoas[
            pessoa
        ] += 1


# ============================================================
# ASSUNTOS + PESSOAS
# ============================================================

col1, col2 = st.columns(
    2
)


with col1:

    st.subheader(
        "🔥 Assuntos quentes"
    )


    if contador_temas:

        temas_quentes = (
            contador_temas
            .most_common(8)
        )


        for tema, quantidade in temas_quentes:

            st.markdown(
                f"**{tema}** — "
                f"{quantidade} notícia(s)"
            )

    else:

        st.info(
            "Nenhum tema identificado."
        )


with col2:

    st.subheader(
        "👥 Pessoas mais citadas"
    )


    if contador_pessoas:

        pessoas_quentes = (
            contador_pessoas
            .most_common(8)
        )


        for pessoa, quantidade in pessoas_quentes:

            st.markdown(
                f"**{pessoa}** — "
                f"{quantidade} notícia(s)"
            )

    else:

        st.info(
            "Nenhuma pessoa monitorada citada."
        )


st.divider()


# ============================================================
# MÉTRICAS
# ============================================================

criticas_total = len([

    n for n in noticias_periodo

    if n["score"] >= 85
])


altas_total = len([

    n for n in noticias_periodo

    if 65 <= n["score"] < 85
])


medias_total = len([

    n for n in noticias_periodo

    if 45 <= n["score"] < 65
])


mencoes_total = len([

    n for n in noticias_periodo

    if n["score"] < 45
])


col1, col2, col3, col4, col5 = st.columns(
    5
)


with col1:

    st.metric(
        "📰 Notícias",
        len(noticias_periodo)
    )


with col2:

    st.metric(
        "🔴 Críticas",
        criticas_total
    )


with col3:

    st.metric(
        "🟠 Altas",
        altas_total
    )


with col4:

    st.metric(
        "🟡 Médias",
        medias_total
    )


with col5:

    st.metric(
        "⚪ Menções",
        mencoes_total
    )


st.divider()
