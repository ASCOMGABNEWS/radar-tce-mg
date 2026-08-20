import streamlit as st
import feedparser
from datetime import datetime, timedelta
import re
from collections import Counter
from urllib.parse import urlparse
from html import escape


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Radar TCE-MG",
    page_icon="🏛️",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #10161d;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

/* HEADER */

.radar-header {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 22px;
    padding: 26px 30px;
    margin-bottom: 22px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.20);
}

.radar-title {
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -1px;
}

.radar-subtitle {
    color: #9ca7b4;
    font-size: 14px;
    margin-top: 4px;
}

.status {
    display: inline-block;
    margin-top: 14px;
    padding: 6px 11px;
    border-radius: 20px;
    background: rgba(53,190,105,0.10);
    border: 1px solid rgba(53,190,105,0.20);
    color: #8de2ad;
    font-size: 12px;
}


/* PAINÉIS */

.dashboard-card {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.085);
    border-radius: 18px;
    padding: 20px;
    min-height: 155px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.15);
}

.dashboard-title {
    font-size: 15px;
    font-weight: 750;
    color: #f1f4f7;
    margin-bottom: 13px;
}

.dashboard-row {
    display: flex;
    justify-content: space-between;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    color: #c2cad3;
    font-size: 13px;
}

.dashboard-row:last-child {
    border-bottom: none;
}

.dashboard-number {
    font-weight: 750;
    color: #ffffff;
}


/* MÉTRICAS */

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 10px 14px;
}


/* FILTROS */

div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.045);
    border-color: rgba(255,255,255,0.10);
    border-radius: 10px;
}

div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.045);
    border-color: rgba(255,255,255,0.10);
    border-radius: 10px;
}


/* NOTÍCIA */

.news-card {
    background: rgba(255,255,255,0.038);
    border: 1px solid rgba(255,255,255,0.075);
    border-radius: 18px;
    padding: 21px 23px;
    margin: 13px 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.13);
}

.news-card:hover {
    border-color: rgba(255,255,255,0.15);
}

.news-title {
    font-size: 17px;
    line-height: 1.4;
    font-weight: 700;
    color: #f4f6f8;
}

.news-meta {
    color: #8f9aa7;
    font-size: 12px;
    margin-top: 8px;
}

.news-summary {
    color: #bbc4ce;
    font-size: 13px;
    line-height: 1.55;
    margin-top: 12px;
}

.news-source {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    margin-top: 10px;
    padding: 5px 9px;
    border-radius: 9px;
    background: rgba(255,255,255,0.055);
    color: #d6dce2;
    font-size: 12px;
}

.news-source img {
    width: 18px;
    height: 18px;
    border-radius: 4px;
}

.tag {
    display: inline-block;
    padding: 4px 8px;
    margin: 8px 4px 0 0;
    border-radius: 999px;
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.07);
    color: #bfc8d2;
    font-size: 11px;
}

.read-link {
    display: inline-block;
    margin-top: 14px;
    padding: 7px 11px;
    border-radius: 9px;
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.08);
    color: #e0e6eb !important;
    text-decoration: none !important;
    font-size: 12px;
}

.read-link:hover {
    background: rgba(255,255,255,0.09);
}


/* BOTÃO */

.stButton > button {
    border-radius: 10px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FONTES
# ============================================================

FONTES = {

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

    "TCE-MG":
        'https://news.google.com/rss/search?q=%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "TCE MG":
        'https://news.google.com/rss/search?q=%22TCE%20MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tribunal de Contas MG":
        'https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22+%22Minas%20Gerais%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

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
# PESSOAS
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
# MAPA DE BUSCA DAS PESSOAS
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


def obter_dominio(url):

    try:

        dominio = urlparse(
            url
        ).netloc.lower()

        return dominio.replace(
            "www.",
            ""
        )

    except Exception:

        return ""


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

    score += len(pessoas) * 12

    score += len(temas) * 5

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

            # Busca específica por pessoa
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
                temas,
                pessoas
            )

            noticias.append({

                "titulo": titulo,
                "resumo": resumo,
                "link": link,
                "monitoramento": nome,
                "veiculo": extrair_veiculo(item),
                "dominio": obter_dominio(link),
                "data": data,
                "score": score,
                "bolinha": classificar(score),
                "temas": temas,
                "pessoas": pessoas,

            })

    noticias.sort(

        key=lambda x: (
            x["score"],
            x["data"] or datetime.min
        ),

        reverse=True
    )

    return noticias


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="radar-header">

    <div class="radar-title">
        🏛️ Radar TCE-MG
    </div>

    <div class="radar-subtitle">
        Monitoramento de imprensa e assuntos estratégicos
    </div>

    <div class="status">
        ● Monitoramento ativo
    </div>

</div>
""", unsafe_allow_html=True)


col1, col2 = st.columns(
    [1, 5]
)


with col1:

    if st.button(
        "🔄 Atualizar"
    ):

        st.cache_data.clear()

        st.rerun()


with col2:

    st.caption(
        "Atualização automática a cada 5 minutos"
    )


# ============================================================
# NOTÍCIAS
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
        and n["data"] >= limite_periodo
    )
]


# ============================================================
# CONTADORES
# ============================================================

criticas = [

    n for n in noticias_periodo
    if n["score"] >= 85
]

altas = [

    n for n in noticias_periodo
    if 65 <= n["score"] < 85
]

contador_temas = Counter()
contador_pessoas = Counter()


for noticia in noticias_periodo:

    for tema in noticia["temas"]:
        contador_temas[tema] += 1

    for pessoa in noticia["pessoas"]:
        contador_pessoas[pessoa] += 1


# ============================================================
# PAINÉIS
# ============================================================

col1, col2, col3 = st.columns(3)


# RADAR

with col1:

    html = """
    <div class="dashboard-card">

        <div class="dashboard-title">
            🚨 Radar de atenção
        </div>

        <div class="dashboard-row">
            <span>🔴 Críticas</span>
            <span class="dashboard-number">
                %d
            </span>
        </div>

        <div class="dashboard-row">
            <span>🟠 Alta relevância</span>
            <span class="dashboard-number">
                %d
            </span>
        </div>

    </div>
    """ % (
        len(criticas),
        len(altas)
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ASSUNTOS

with col2:

    html = """
    <div class="dashboard-card">

        <div class="dashboard-title">
            🔥 Assuntos quentes
        </div>
    """

    if contador_temas:

        for tema, quantidade in contador_temas.most_common(5):

            html += f"""
            <div class="dashboard-row">

                <span>{escape(tema)}</span>

                <span class="dashboard-number">
                    {quantidade}
                </span>

            </div>
            """

    else:

        html += """
        <div class="dashboard-row">
            <span>Nenhum tema identificado</span>
        </div>
        """

    html += "</div>"

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# PESSOAS

with col3:

    html = """
    <div class="dashboard-card">

        <div class="dashboard-title">
            👥 Pessoas mais citadas
        </div>
    """

    if contador_pessoas:

        for pessoa, quantidade in contador_pessoas.most_common(5):

            html += f"""
            <div class="dashboard-row">

                <span>{escape(pessoa)}</span>

                <span class="dashboard-number">
                    {quantidade}
                </span>

            </div>
            """

    else:

        html += """
        <div class="dashboard-row">
            <span>Nenhuma pessoa identificada</span>
        </div>
        """

    html += "</div>"

    st.markdown(
        html,
        unsafe_allow_html=True
    )


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


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


col1, col2, col3, col4, col5 = st.columns(5)


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


# ============================================================
# FILTROS
# ============================================================

st.subheader(
    "🔎 Monitorar"
)


todas_pessoas = []


for grupo in PESSOAS.values():

    todas_pessoas.extend(
        grupo.keys()
    )


col1, col2, col3 = st.columns(3)


with col1:

    filtro_pessoa = st.selectbox(
        "👤 Pessoa",
        ["Todas"] + todas_pessoas
    )


with col2:

    filtro_tema = st.selectbox(
        "🏷️ Tema",
        ["Todos"] + list(TEMAS.keys())
    )


with col3:

    filtro_fonte = st.selectbox(
        "🗞️ Fonte",
        ["Todas"] + list(FONTES.keys())
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
        ]
    )


with col2:

    busca = st.text_input(
        "🔍 Buscar palavra",
        placeholder="Ex.: Copasa, mineração, transporte..."
    )


# ============================================================
# APLICA FILTROS
# ============================================================

filtradas = noticias_periodo


if filtro_pessoa != "Todas":

    filtradas = [
        n for n in filtradas
        if filtro_pessoa in n["pessoas"]
    ]


if filtro_tema != "Todos":

    filtradas = [
        n for n in filtradas
        if filtro_tema in n["temas"]
    ]


if filtro_fonte != "Todas":

    filtradas = [
        n for n in filtradas
        if n["monitoramento"] == filtro_fonte
    ]


if filtro_relevancia != "Todas":

    mapa = {
        "🔴 Crítica": "🔴",
        "🟠 Alta": "🟠",
        "🟡 Média": "🟡",
        "⚪ Menção": "⚪"
    }

    filtradas = [
        n for n in filtradas
        if n["bolinha"] == mapa[filtro_relevancia]
    ]


if busca:

    termo = busca.lower()

    filtradas = [
        n for n in filtradas
        if termo in (
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

        titulo = escape(
            noticia["titulo"]
        )

        resumo = escape(
            noticia["resumo"]
        )

        veiculo = escape(
            noticia["veiculo"]
        )

        link = escape(
            noticia["link"],
            quote=True
        )

        dominio = noticia["dominio"]


        if noticia["data"]:

            data_formatada = (
                noticia["data"]
                .strftime(
                    "%d/%m/%Y %H:%M"
                )
            )

        else:

            data_formatada = ""


        # ----------------------------------------------------
        # LOGO / FAVICON
        # ----------------------------------------------------

        if dominio:

            logo = (
                "https://www.google.com/"
                "s2/favicons?"
                f"domain={dominio}&sz=64"
            )

        else:

            logo = ""


        # ----------------------------------------------------
        # TAGS DE PESSOAS
        # ----------------------------------------------------

        pessoas_html = ""

        for pessoa in noticia["pessoas"]:

            pessoas_html += (
                f'<span class="tag">'
                f'👤 {escape(pessoa)}'
                f'</span>'
            )


        # ----------------------------------------------------
        # TAGS DE TEMAS
        # ----------------------------------------------------

        temas_html = ""

        for tema in noticia["temas"]:

            temas_html += (
                f'<span class="tag">'
                f'{escape(tema)}'
                f'</span>'
            )


        # ----------------------------------------------------
        # CARD
        # ----------------------------------------------------

        card = f"""
        <div class="news-card">

            <div class="news-title">
                {noticia["bolinha"]}
                {titulo}
            </div>

            <div class="news-source">

                <img
                    src="{logo}"
                    onerror="this.style.display='none';"
                >

                {veiculo}

            </div>

            <div class="news-meta">
                📅 {data_formatada}
            </div>

            <div>
                {pessoas_html}
                {temas_html}
            </div>

            <div class="news-summary">
                {resumo[:600]}
                {"..." if len(noticia["resumo"]) > 600 else ""}
            </div>

            <a
                class="read-link"
                href="{link}"
                target="_blank"
            >
                Ler matéria ↗
            </a>

        </div>
        """

        st.markdown(
            card,
            unsafe_allow_html=True
        )
