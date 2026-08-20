import streamlit as st
import feedparser
from datetime import datetime, timedelta
import re
import html
from collections import Counter
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import cm



def esc_html(value):
    return html.escape(
        str(value or ""),
        quote=True
    )


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
# INTERFACE
# ============================================================

st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}

.block-container {
    max-width: 1280px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

.radar-header {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:24px;
    margin-bottom:14px;
}

.radar-brand {
    display:flex;
    align-items:center;
    gap:14px;
}

.radar-icon {
    font-size:42px;
    line-height:1;
}

.radar-title {
    font-size:30px;
    font-weight:800;
    letter-spacing:-.8px;
    color:#18233a;
}

.radar-subtitle {
    font-size:14px;
    color:#667085;
    margin-top:3px;
}

.radar-update {
    text-align:right;
    font-size:13px;
    color:#667085;
}

.radar-update strong {
    color:#18233a;
}

.section-card {
    background:rgba(255,255,255,.72);
    border:1px solid #e4e8ef;
    border-radius:14px;
    padding:16px 18px;
    box-shadow:0 2px 10px rgba(16,24,40,.035);
    height:230px;
    box-sizing:border-box;
    overflow:hidden;
}

.section-title {
    font-size:16px;
    font-weight:700;
    color:#18233a;
    margin-bottom:10px;
}

.mini-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:9px;
}

.mini-card {
    border:1px solid #e4e8ef;
    border-radius:12px;
    padding:13px;
    background:#fff;
    text-align:center;
}

.mini-label {
    font-size:12px;
    color:#344054;
    font-weight:650;
}


.red-number { color:#d92d20; }
.orange-number { color:#e76f00; }

.empty-note {
    font-size:12px;
    color:#98a2b3;
    padding:8px 0;
}

.secondary-card .compact-row {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding:7px 0;
    border-bottom:1px solid #eef1f5;
    font-size:12px;
    color:#344054;
}

.compact-row:last-child {
    border-bottom:none;
}

.compact-row strong {
    color:#18233a;
}

.mini-number {
    font-size:27px;
    font-weight:800;
    margin-top:5px;
    color:#18233a;
}

.mini-note {
    font-size:11px;
    color:#667085;
    margin-top:2px;
}

.hot-row {
    display:grid;
    grid-template-columns:1fr 34px;
    align-items:center;
    gap:8px;
    margin:7px 0;
}

.hot-name {
    font-size:12px;
    color:#344054;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}

.hot-bar {
    height:4px;
    background:#eef1f5;
    border-radius:10px;
    margin-top:4px;
    overflow:hidden;
}

.hot-fill {
    height:100%;
    background:#f4b400;
    border-radius:10px;
}

.hot-count {
    text-align:right;
    font-size:12px;
    color:#344054;
    font-weight:700;
}

.person-row {
    display:grid;
    grid-template-columns:1fr 36px;
    gap:8px;
    margin:7px 0;
}

.person-name {
    font-size:12px;
    color:#344054;
}

.person-bar {
    height:4px;
    background:#eef1f5;
    border-radius:10px;
    margin-top:4px;
    overflow:hidden;
}

.person-fill {
    height:100%;
    background:#f4b400;
    border-radius:10px;
}

.person-count {
    text-align:right;
    font-size:12px;
    font-weight:700;
    color:#344054;
}


.news-card {
    display:grid;
    grid-template-columns:1fr 82px;
    gap:18px;
    align-items:start;
    background:rgba(255,255,255,.82);
    border:1px solid #e4e8ef;
    border-radius:14px;
    padding:13px 16px;
    margin:9px 0;
    box-shadow:0 2px 8px rgba(16,24,40,.025);
}

.news-source {
    display:none;
    text-align:center;
    border-right:1px solid #edf0f4;
    padding-right:14px;
    min-height:84px;
}

.news-logo {
    width:48px;
    height:48px;
    object-fit:contain;
    border-radius:8px;
    margin-bottom:4px;
}

.news-source-name {
    font-size:10px;
    font-weight:700;
    color:#344054;
}


.news-content {
    min-width:0;
}

.severity-dot {
    display:inline-block;
    margin-right:5px;
}

.news-title {
    font-size:16px;
    line-height:1.35;
    font-weight:750;
    margin-bottom:7px;
}

.news-title a {
    color:#18233a;
    text-decoration:none;
}

.news-title a:hover {
    color:#164194;
    text-decoration:underline;
}

.news-meta {
    font-size:11px;
    color:#667085;
    margin-bottom:7px;
}

.tag {
    display:inline-block;
    background:#f6f8fa;
    border:1px solid #e7eaee;
    border-radius:12px;
    padding:3px 7px;
    margin:0 4px 4px 0;
    font-size:10px;
    color:#475467;
}

.news-summary {
    font-size:12px;
    line-height:1.55;
    color:#667085;
    margin-top:5px;
}

.news-time {
    text-align:right;
    font-size:11px;
    color:#667085;
}


@media (max-width: 800px) {
    .news-card { grid-template-columns:1fr; }
    .news-time { display:none; }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CABEÇALHO
# ============================================================

agora = datetime.now()

st.markdown(
    f"""
    <div class="radar-header">
        <div class="radar-brand">
            <div class="radar-icon">🏛️</div>
            <div>
                <div class="radar-title">Radar TCE-MG</div>
                <div class="radar-subtitle">
                    Monitoramento inteligente de notícias<br>
                    relacionadas ao Tribunal de Contas de Minas Gerais
                </div>
            </div>
        </div>
        <div class="radar-update">
            Última atualização: <strong>{agora.strftime('%d/%m/%Y %H:%M')}</strong><br>
            Atualização automática a cada 5 minutos
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

col_atualizar, col_status = st.columns([1.1, 3.5])

with col_atualizar:

    atualizar_agora = st.button(
        "🔄 Atualizar agora"
    )

with col_status:

    status_area = st.empty()


if atualizar_agora:

    st.cache_data.clear()
    st.rerun()


# ============================================================
# COLETA
# ============================================================

with status_area:

    with st.spinner("Atualizando notícias..."):

        noticias = buscar_noticias()


# ============================================================
# PERÍODO
# ============================================================

periodo = st.radio(
    "Período",
    [
        "Últimas 6 horas",
        "Últimas 24 horas",
        "Últimos 3 dias",
        "Últimos 7 dias",
    ],
    horizontal=True,
    label_visibility="collapsed"
)


if periodo == "Últimas 6 horas":
    limite_periodo = agora - timedelta(hours=6)
elif periodo == "Últimas 24 horas":
    limite_periodo = agora - timedelta(hours=24)
elif periodo == "Últimos 3 dias":
    limite_periodo = agora - timedelta(days=3)
else:
    limite_periodo = agora - timedelta(days=7)


noticias_periodo = [
    n for n in noticias
    if n["data"] and n["data"] >= limite_periodo
]


# ============================================================
# CONTADORES DO PAINEL
# ============================================================

criticas = [n for n in noticias_periodo if n["score"] >= 85]
altas = [n for n in noticias_periodo if 65 <= n["score"] < 85]
medias = [n for n in noticias_periodo if 45 <= n["score"] < 65]
mencoes = [n for n in noticias_periodo if n["score"] < 45]

contador_temas = Counter()
contador_pessoas = Counter()
contador_veiculos = Counter()
contador_instituicoes = Counter()

for noticia in noticias_periodo:
    for tema in noticia["temas"]:
        contador_temas[tema] += 1
    for pessoa in noticia["pessoas"]:
        contador_pessoas[pessoa] += 1
    if noticia["veiculo"]:
        contador_veiculos[noticia["veiculo"]] += 1
    for instituicao in noticia.get("instituicoes", []):
        contador_instituicoes[instituicao] += 1



# ============================================================
# PAINEL SUPERIOR
# ============================================================

criticas = [
    n for n in noticias_periodo
    if n["score"] >= 85
]

altas = [
    n for n in noticias_periodo
    if 65 <= n["score"] < 85
]

medias = [
    n for n in noticias_periodo
    if 45 <= n["score"] < 65
]

mencoes = [
    n for n in noticias_periodo
    if n["score"] < 45
]

col1, col2, col3 = st.columns(
    [1.05, 1.25, 1.25],
    gap="medium"
)

# ------------------------------------------------------------
# RADAR DE ATENÇÃO
# ------------------------------------------------------------

with col1:

    with st.container(border=True):

        st.markdown("**🚨 Radar de atenção**")

        r1, r2 = st.columns(2)

        with r1:

            st.markdown("🔴 **Críticas**")

            st.markdown(
                f"<h2 style='margin:2px 0 0 0'>{len(criticas)}</h2>",
                unsafe_allow_html=True
            )

            st.caption(
                "merecem atenção imediata"
            )

        with r2:

            st.markdown("🟠 **Alta relevância**")

            st.markdown(
                f"<h2 style='margin:2px 0 0 0'>{len(altas)}</h2>",
                unsafe_allow_html=True
            )

            st.caption(
                "potencialmente importantes"
            )

# ------------------------------------------------------------
# ASSUNTOS QUENTES
# ------------------------------------------------------------

with col2:

    with st.container(border=True):

        st.markdown("**🔥 Assuntos quentes**")

        temas_quentes = contador_temas.most_common(6)

        if temas_quentes:

            max_tema = max(
                quantidade
                for _, quantidade
                in temas_quentes
            )

            for tema, quantidade in temas_quentes:

                c1, c2 = st.columns([5, 1])

                with c1:

                    st.markdown(
                        f"**{tema}**"
                    )

                    st.progress(
                        quantidade / max_tema
                    )

                with c2:

                    st.markdown(
                        f"**{quantidade}**"
                    )

        else:

            st.caption(
                "Nenhum assunto identificado."
            )

# ------------------------------------------------------------
# PESSOAS MAIS CITADAS
# ------------------------------------------------------------

with col3:

    with st.container(border=True):

        st.markdown("**👥 Pessoas mais citadas**")

        pessoas_quentes = (
            contador_pessoas
            .most_common(6)
        )

        if pessoas_quentes:

            max_pessoa = max(
                quantidade
                for _, quantidade
                in pessoas_quentes
            )

            for pessoa, quantidade in pessoas_quentes:

                c1, c2 = st.columns([5, 1])

                with c1:

                    st.markdown(
                        f"**{pessoa}**"
                    )

                    st.progress(
                        quantidade / max_pessoa
                    )

                with c2:

                    st.markdown(
                        f"**{quantidade}**"
                    )

        else:

            st.caption(
                "Nenhuma pessoa identificada."
            )


# ============================================================
# MÉTRICAS
# ============================================================

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.metric("📰 Total de notícias", len(noticias_periodo))
with m2:
    st.metric("🔴 Críticas", len(criticas))
with m3:
    st.metric("🟠 Altas", len(altas))
with m4:
    st.metric("🟡 Médias", len(medias))
with m5:
    st.metric("⚪ Menções", len(mencoes))


# ============================================================
# FILTROS
# ============================================================

st.subheader("🔎 Monitorar")

todas_pessoas = []
for grupo in PESSOAS.values():
    todas_pessoas.extend(grupo.keys())

f1, f2, f3 = st.columns(3)

with f1:
    filtro_pessoa = st.selectbox(
        "👤 Pessoa",
        ["Todas"] + todas_pessoas
    )

with f2:
    filtro_tema = st.selectbox(
        "🏷️ Tema",
        ["Todos"] + list(TEMAS.keys())
    )

with f3:
    filtro_fonte = st.selectbox(
        "🗞️ Fonte",
        ["Todas"] + list(FONTES.keys())
    )

f4, f5 = st.columns(2)

with f4:
    filtro_relevancia = st.selectbox(
        "🎯 Relevância",
        ["Todas", "🔴 Crítica", "🟠 Alta", "🟡 Média", "⚪ Menção"]
    )

with f5:
    busca = st.text_input(
        "🔍 Buscar palavra",
        placeholder="Ex.: Copasa, mineração, transporte..."
    )

apenas_relevantes = st.checkbox(
    "🎯 Apenas relevantes (🔴 + 🟠)"
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

    mapa_relevancia = {
        "🔴 Crítica": "🔴",
        "🟠 Alta": "🟠",
        "🟡 Média": "🟡",
        "⚪ Menção": "⚪",
    }

    filtradas = [
        n for n in filtradas
        if n["bolinha"] == mapa_relevancia[filtro_relevancia]
    ]

if apenas_relevantes:
    filtradas = [
        n for n in filtradas
        if n["score"] >= 65
    ]

if busca:

    termo = busca.lower()

    filtradas = [
        n for n in filtradas
        if termo in (
            n["titulo"] + " " + n["resumo"]
        ).lower()
    ]


# ============================================================
# DOWNLOAD DO CLIPPING
# ============================================================

def gerar_pdf_clipping(noticias_clipping):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
    )

    styles = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloClipping",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitulo = ParagraphStyle(
        "SubtituloClipping",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=18,
    )

    secao = ParagraphStyle(
        "SecaoClipping",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=8,
    )

    manchete = ParagraphStyle(
        "MancheteClipping",
        parent=styles["Heading3"],
        fontSize=11.5,
        leading=15,
        spaceAfter=5,
    )

    corpo = ParagraphStyle(
        "CorpoClipping",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        spaceAfter=6,
    )

    meta = ParagraphStyle(
        "MetaClipping",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.grey,
        spaceAfter=5,
    )

    story = []

    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")

    story.append(Paragraph("CLIPPING TCE-MG", titulo))
    story.append(
        Paragraph(
            f"Gerado em {data_geracao} • "
            f"{len(noticias_clipping)} notícia(s)",
            subtitulo,
        )
    )

    # Destaques
    criticas_pdf = [
        n for n in noticias_clipping
        if n["score"] >= 85
    ]
    altas_pdf = [
        n for n in noticias_clipping
        if 65 <= n["score"] < 85
    ]

    if criticas_pdf or altas_pdf:
        story.append(Paragraph("DESTAQUES", secao))

        for noticia in (criticas_pdf[:5] + altas_pdf[:5]):
            story.append(
                Paragraph(
                    f"{noticia['bolinha']} {noticia['titulo']}",
                    manchete,
                )
            )
            story.append(
                Paragraph(
                    f"<b>{noticia['veiculo']}</b>",
                    meta,
                )
            )

    # Notícias
    story.append(Paragraph("NOTÍCIAS", secao))

    for noticia in noticias_clipping:

        data = ""

        if noticia["data"]:
            data = noticia["data"].strftime("%d/%m/%Y %H:%M")

        pessoas = ", ".join(noticia["pessoas"])
        temas = ", ".join(noticia["temas"])
        resumo = noticia["resumo"]

        if len(resumo) > 700:
            resumo = resumo[:700] + "..."

        story.append(
            Paragraph(
                f"{noticia['bolinha']} {noticia['titulo']}",
                manchete,
            )
        )

        story.append(
            Paragraph(
                f"{noticia['veiculo']} • {data}",
                meta,
            )
        )

        if pessoas:
            story.append(
                Paragraph(
                    f"<b>Pessoas:</b> {pessoas}",
                    corpo,
                )
            )

        if temas:
            story.append(
                Paragraph(
                    f"<b>Temas:</b> {temas}",
                    corpo,
                )
            )

        if resumo:
            story.append(
                Paragraph(
                    resumo,
                    corpo,
                )
            )

        story.append(
            Paragraph(
                f'<link href="{noticia["link"]}" color="blue">'
                f"{noticia['link']}</link>",
                meta,
            )
        )

        story.append(Spacer(1, 0.18 * cm))

    # Assuntos
    contador_temas_pdf = Counter()

    for noticia in noticias_clipping:
        for tema in noticia["temas"]:
            contador_temas_pdf[tema] += 1

    if contador_temas_pdf:
        story.append(PageBreak())
        story.append(Paragraph("ASSUNTOS EM DESTAQUE", secao))

        for tema, quantidade in contador_temas_pdf.most_common(10):
            story.append(
                Paragraph(
                    f"{tema} — {quantidade} notícia(s)",
                    corpo,
                )
            )

    # Pessoas
    contador_pessoas_pdf = Counter()

    for noticia in noticias_clipping:
        for pessoa in noticia["pessoas"]:
            contador_pessoas_pdf[pessoa] += 1

    if contador_pessoas_pdf:
        story.append(Paragraph("PESSOAS MAIS CITADAS", secao))

        for pessoa, quantidade in contador_pessoas_pdf.most_common(10):
            story.append(
                Paragraph(
                    f"{pessoa} — {quantidade} notícia(s)",
                    corpo,
                )
            )

    doc.build(story)

    buffer.seek(0)
    return buffer.getvalue()


pdf_bytes = gerar_pdf_clipping(filtradas)

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
# RESULTADOS
# ============================================================

st.subheader(
    f"📰 {len(filtradas)} notícias encontradas"
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

        pessoas_html = "".join(
            [
                f'<span class="tag">👤 {esc_html(p)}</span>'
                for p in noticia["pessoas"]
            ]
        )

        temas_html = "".join(
            [
                f'<span class="tag">{esc_html(tema)}</span>'
                for tema in noticia["temas"]
            ]
        )

        resumo = esc_html(
            noticia["resumo"] or ""
        )

        if len(resumo) > 420:
            resumo = resumo[:420] + "..."

        titulo_html = esc_html(
            noticia["titulo"]
        )

        veiculo_html = esc_html(
            noticia["veiculo"]
        )

        link = noticia["link"]

        html = f"""
        <div class="news-card">

            <div class="news-content">

                <div class="news-meta">
                    📰 {veiculo_html}
                </div>

                <div class="news-title">
                    <span class="severity-dot">{noticia["bolinha"]}</span>
                    <a href="{link}"
                       target="_blank"
                       rel="noopener noreferrer">
                       {titulo_html}
                    </a>
                </div>

                <div class="news-meta">
                    {pessoas_html}
                    {temas_html}
                </div>

                <div class="news-summary">
                    {resumo}
                </div>

            </div>

            <div class="news-time">
                {data_formatada}
            </div>

        </div>
        """

        st.html(html)

# ============================================================
# RODAPÉ
# ============================================================

st.caption(
    "As notícias são classificadas automaticamente com base em relevância para o TCE-MG."
)
