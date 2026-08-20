from zoneinfo import ZoneInfo

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")

def formatar_horario_noticia(data):
    """Exibe a data da notícia no horário de Brasília."""
    if not data:
        return ""
    try:
        if data.tzinfo is None:
            # Compatibilidade com registros antigos: o feed representa UTC.
            data = data.replace(tzinfo=ZoneInfo("UTC"))
        return data.astimezone(FUSO_BRASIL).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return ""
import streamlit as st
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
from urllib.request import Request, urlopen
from openai import OpenAI

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

if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    client = None


def esc_html(value):
    if value is None:
        return ""
    return html.escape(
        str(value),
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
    # MONITORAMENTO INSTITUCIONAL — CONTROLE EXTERNO
    # --------------------------------------------------------

    # Atricon é monitorada de forma independente: a notícia não precisa
    # citar TCE-MG para ser relevante ao ambiente dos Tribunais de Contas.
    "Atricon":
        'https://news.google.com/rss/search?q=%22Atricon%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "IRB":
        'https://news.google.com/rss/search?q=%22Instituto%20Rui%20Barbosa%22+OR+%22IRB%22+%22Tribunais%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tribunais de Contas":
        'https://news.google.com/rss/search?q=%22Tribunais%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Tribunal de Contas":
        'https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Presidentes de Tribunais de Contas":
        'https://news.google.com/rss/search?q=%22presidente%20do%20Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "Conselheiros de Tribunais de Contas":
        'https://news.google.com/rss/search?q=%22conselheiro%22+%22Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',

    "TCEs":
        'https://news.google.com/rss/search?q=%22TCE%22+%22Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419',


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

            data_utc = datetime(
                *item.published_parsed[:6],
                tzinfo=ZoneInfo("UTC")
            )
            return data_utc.astimezone(FUSO_BRASIL)

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
# ABRANGÊNCIA DAS FONTES
# ============================================================

FONTES_NACIONAIS = {
    "Folha",
    "UOL",
    "Globo",
    "G1",
    "Poder360",
    "JOTA",
    "Migalhas",
    "O Bastidor",
    "Intercept Brasil",
    "revista piauí",
    "Brasil de Fato",
    "Correio Braziliense",
    "Estadão",
    "O Antagonista",
    "CartaCapital",
    "CNN Brasil",
    "Agência Brasil",
    "Valor Econômico",
    "ConJur",
    "Metrópoles",
}

FONTES_MINAS = {
    "Estado de Minas",
    "Itatiaia",
    "O TEMPO",
    "Hoje em Dia",
    "Tribuna de Minas",
    "Diário do Comércio",
    "BHAZ",
    "Agência Minas",
    "O Fator",
    "Edição do Brasil",
    "Moon BH",
}

# Termos que identificam claramente outros estados. Uma notícia sobre
# um TCE de outro estado é Nacional para este Radar, não Minas Gerais.
OUTROS_ESTADOS = (
    "tce-pi", "tce pi", "tce-piauí", "tce piauí",
    "tce-ma", "tce ma", "tce-maranhão", "tce maranhão",
    "tce-sp", "tce sp", "tce-são paulo",
    "tce-rj", "tce rj", "tce-rio de janeiro",
    "tce-pr", "tce pr", "tce-paraná",
    "tce-sc", "tce sc", "tce-santa catarina",
    "tce-rs", "tce rs", "tce-rio grande do sul",
    "tce-go", "tce go", "tce-goiás",
    "tce-ba", "tce ba", "tce-bahia",
    "tce-pe", "tce pe", "tce-pernambuco",
    "tce-ce", "tce ce", "tce-ceará",
    "tce-es", "tce es", "tce-espírito santo",
    "tce-df", "tce df",
    "tce-ms", "tce ms", "tce-mato grosso do sul",
    "tce-mt", "tce mt", "tce-mato grosso",
    "tce-pa", "tce pa", "tce-pará",
    "tce-am", "tce am", "tce-amazonas",
    "tce-ro", "tce ro", "tce-rondônia",
    "tce-to", "tce to", "tce-tocantins",
    "tce-ac", "tce ac", "tce-acre",
    "tce-al", "tce al", "tce-alagoas",
    "tce-se", "tce se", "tce-sergipe",
    "tce-pb", "tce pb", "tce-paraíba",
    "tce-rn", "tce rn", "tce-rio grande do norte",
)

def classificar_abrangencia(veiculo, titulo="", resumo=""):
    texto = " ".join([
        str(veiculo or ""),
        str(titulo or ""),
        str(resumo or "")
    ]).lower()

    # Primeiro: fontes claramente mineiras.
    if any(f.lower() in str(veiculo or "").lower() for f in FONTES_MINAS):
        return "Minas Gerais"

    # Segundo: uma matéria explicitamente sobre outro TCE/estado
    # nunca deve cair como Minas só porque a fonte é um portal nacional.
    if any(termo in texto for termo in OUTROS_ESTADOS):
        return "Nacional"

    # Terceiro: conteúdo explicitamente ligado a Minas/TCE-MG.
    termos_minas = (
        "tce-mg", "tce mg", "tce de minas gerais",
        "tribunal de contas de minas gerais",
        "tribunal de contas de mg", "minas gerais",
        "minas", "belo horizonte", "mg"
    )

    if any(termo in texto for termo in termos_minas):
        return "Minas Gerais"

    # Portais nacionais e notícias institucionais sem estado definido
    # ficam como Nacional por padrão.
    return "Nacional"


# ============================================================
# COLETA
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def analisar_relevancia_ia(titulo, resumo, veiculo, abrangencia, instituicoes):
    try:
        if not client:
            return {
                "nota": 0,
                "nivel": "Menção",
                "motivo": "IA não configurada."
            }

        resposta = client.responses.create(
            model="gpt-5.4-mini",
            input=f"""
Você é o analista de inteligência institucional do Radar TCE-MG.

O Radar monitora notícias para o Gabinete do Conselheiro
Agostinho Patrus, do Tribunal de Contas do Estado de Minas Gerais.

Analise a relevância institucional da notícia abaixo.

TÍTULO:
{titulo}

RESUMO:
{resumo}

VEÍCULO:
{veiculo}

ABRANGÊNCIA:
{abrangencia}

INSTITUIÇÕES IDENTIFICADAS:
{instituicoes}

Dê mais importância para:
- TCE-MG;
- Conselheiros do TCE-MG;
- Agostinho Patrus;
- Atricon;
- IRB;
- outros Tribunais de Contas;
- presidentes e conselheiros de outros Tribunais de Contas;
- controle externo;
- fiscalização;
- contas públicas;
- administração pública;
- reforma tributária;
- concessões;
- assuntos institucionais relevantes.

Uma notícia sobre outro Tribunal de Contas também pode ser relevante,
mesmo que não mencione o TCE-MG.

Classifique:

CRÍTICA: 90 a 100
ALTA: 75 a 89
MÉDIA: 50 a 74
MENÇÃO: 0 a 49

Responda EXATAMENTE neste formato:

NOTA: número de 0 a 100
NÍVEL: Crítica, Alta, Média ou Menção
MOTIVO: explicação curta em até 2 frases
"""
        )

        texto = resposta.output_text.strip()

        nota = 0
        nivel = "Menção"
        motivo = texto

        for linha in texto.splitlines():
            linha_limpa = linha.strip()

            if linha_limpa.upper().startswith("NOTA:"):
                try:
                    nota = int(
                        ''.join(
                            c for c in linha_limpa.split(":", 1)[1]
                            if c.isdigit()
                        )
                    )
                    nota = max(0, min(100, nota))
                except Exception:
                    nota = 0

            elif linha_limpa.upper().startswith("NÍVEL:"):
                nivel = linha_limpa.split(":", 1)[1].strip()

            elif linha_limpa.upper().startswith("MOTIVO:"):
                motivo = linha_limpa.split(":", 1)[1].strip()

        return {
            "nota": nota,
            "nivel": nivel,
            "motivo": motivo
        }

    except Exception as e:
        return {
            "nota": 0,
            "nivel": "Menção",
            "motivo": "Não foi possível realizar a análise da IA."
        }
        
@st.cache_data(ttl=300, show_spinner=False)
def buscar_noticias():

    noticias = []

    links = set()

    limite = (
        datetime.now(FUSO_BRASIL)
        - timedelta(days=7)
    )


    for nome, url in FONTES.items():

        try:

            # Não deixe uma fonte RSS fora do ar travar o Radar inteiro.
            request = Request(
                url,
                headers={
                    "User-Agent": "Radar-TCE-MG/1.0"
                }
            )

            with urlopen(
                request,
                timeout=6
            ) as resposta:

                conteudo = resposta.read()

            feed = feedparser.parse(
                conteudo
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

                "abrangencia":
                    classificar_abrangencia(
                        extrair_veiculo(item),
                        titulo,
                        resumo
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
            or datetime.min.replace(tzinfo=FUSO_BRASIL)

        ),

        reverse=True
    )


    return noticias



# ============================================================
# INTERFACE
# ============================================================

st.markdown("""
<style>
.st-key-metricas-centralizadas [data-testid="stMetric"] {
    text-align: center;
}
.st-key-metricas-centralizadas [data-testid="stMetricLabel"] {
    justify-content: center;
    width: 100%;
}
.st-key-metricas-centralizadas [data-testid="stMetricValue"] {
    justify-content: center;
    width: 100%;
}
.st-key-apenas-relevantes-box {
    background: #eef0f3;
    border-radius: 12px;
    padding: 10px 14px 4px 14px;
    min-height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.st-key-apenas-relevantes-box [data-testid="stCheckbox"] {
    justify-content: center;
}
.st-key-abrangencia-estadual button {
    background: #c62828 !important;
    color: white !important;
    border: 1px solid #c62828 !important;
}
.st-key-abrangencia-estadual button:hover {
    background: #a91f1f !important;
    color: white !important;
    border-color: #a91f1f !important;
}
.st-key-abrangencia-nacional button {
    background: #2e7d32 !important;
    color: white !important;
    border: 1px solid #2e7d32 !important;
}
.st-key-abrangencia-nacional button:hover {
    background: #256628 !important;
    color: white !important;
    border-color: #256628 !important;
}
#MainMenu, footer {visibility: hidden;}

.block-container {
    max-width: 1280px;
    padding-top: 3.2rem;
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
    align-items:flex-start;
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
    line-height:1.18;
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

/* Títulos dos painéis ficam fixos; somente o conteúdo interno pode rolar. */
.dashboard-panel-title {
    position: sticky;
    top: 0;
    z-index: 2;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# CABEÇALHO
# ============================================================

agora = datetime.now(FUSO_BRASIL)

st.markdown(
    f"""
    <div class="radar-header">
        <div class="radar-brand">
            <div class="radar-icon">🏛️</div>
            <div>
                <div class="radar-title">Radar TCE-MG</div>
                <div class="radar-subtitle">
                    Monitoramento inteligente do Gab. Agostinho Patrus sobre notícias<br>
                    relacionadas ao Tribunal de Contas de Minas Gerais
                </div>
            </div>
        </div>
        <div class="radar-update">
            Última atualização: <strong>{agora.strftime("%d/%m/%Y")}</strong><br>
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

status_area.markdown(
    "⏳ **Atualizando notícias...**"
)

noticias = buscar_noticias()


status_area.empty()

st.markdown("### 📡 Monitoramento em tempo real")

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

col1, col2, col3 = st.columns(
    [1.05, 1.25, 1.25],
    gap="medium"
)

def box_title(text):
    st.markdown(
        f"""
        <div class="dashboard-panel-title" style="
            background:rgba(100,116,139,.07);
            border:1px solid rgba(100,116,139,.10);
            border-radius:9px;
            padding:8px 12px;
            margin:-4px -4px 12px -4px;
            position:relative;
            z-index:5;
            font-size:17px;
            font-weight:750;
            color:#27324a;
        ">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )


with col1:

    with st.container(border=True, height=310):

        box_title("🚨 Radar de atenção")

        r1, r2 = st.columns(2, gap="small")

        with r1:

            st.markdown("🔴 **Críticas**")

            st.markdown(
                f"""
                <div style="
                    font-size:44px;
                    font-weight:800;
                    line-height:1;
                    margin:0;
                    color:#2f3340;
                ">{len(criticas)}</div>
                """,
                unsafe_allow_html=True
            )

            st.caption("merecem atenção imediata")

        with r2:

            st.markdown("🟠 **Alta relevância**")

            st.markdown(
                f"""
                <div style="
                    font-size:44px;
                    font-weight:800;
                    line-height:1;
                    margin:0;
                    color:#2f3340;
                ">{len(altas)}</div>
                """,
                unsafe_allow_html=True
            )

            st.caption("potencialmente importantes")


with col2:

    with st.container(border=True, height=310):

        st.markdown(
            """
            <div style="
                background:rgba(100,116,139,.07);
                border:1px solid rgba(100,116,139,.10);
                border-radius:9px;
                padding:8px 12px;
                margin:-4px -4px 12px -4px;
                font-size:17px;
                font-weight:750;
                color:#27324a;
            ">
                🔥 Assuntos quentes
            </div>
            """,
            unsafe_allow_html=True
        )

        temas_quentes = contador_temas.most_common(20)

        temas_html = ""

        for tema, quantidade in temas_quentes:

            temas_html += f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:7px 3px;
                font-size:14px;
                color:#27324a;
            ">
                <span><strong>{tema}</strong></span>
                <strong>{quantidade}</strong>
            </div>
            """

        if not temas_html:

            temas_html = """
            <div style="color:#98a2b3;padding:8px 3px;">
                Nenhum assunto identificado.
            </div>
            """

        st.markdown(
            f"""
            <div style="
                height:225px;
                overflow-y:auto;
                overflow-x:hidden;
                padding-right:6px;
            ">
                {temas_html}
            </div>
            """,
            unsafe_allow_html=True
        )


with col3:

    with st.container(border=True, height=310):

        st.markdown(
            """
            <div style="
                background:rgba(100,116,139,.07);
                border:1px solid rgba(100,116,139,.10);
                border-radius:9px;
                padding:8px 12px;
                margin:-4px -4px 12px -4px;
                font-size:17px;
                font-weight:750;
                color:#27324a;
            ">
                👥 Pessoas mais citadas
            </div>
            """,
            unsafe_allow_html=True
        )

        pessoas_quentes = contador_pessoas.most_common(20)

        pessoas_html = ""

        for pessoa, quantidade in pessoas_quentes:

            pessoas_html += f"""
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                padding:7px 3px;
                font-size:14px;
                color:#27324a;
            ">
                <span><strong>{pessoa}</strong></span>
                <strong>{quantidade}</strong>
            </div>
            """

        if not pessoas_html:

            pessoas_html = """
            <div style="color:#98a2b3;padding:8px 3px;">
                Nenhuma pessoa identificada.
            </div>
            """

        st.markdown(
            f"""
            <div style="
                height:225px;
                overflow-y:auto;
                overflow-x:hidden;
                padding-right:6px;
            ">
                {pessoas_html}
            </div>
            """,
            unsafe_allow_html=True
        )



# ============================================================
# MATÉRIA MAIS IMPORTANTE DOS ÚLTIMOS 7 DIAS
# ============================================================

# O destaque considera sempre os últimos 7 dias, independentemente
# do período selecionado no filtro principal.
limite_destaque_7d = datetime.now(FUSO_BRASIL) - timedelta(days=7)

noticias_7d = [
    n for n in noticias
    if n.get("data") and n["data"] >= limite_destaque_7d
]

materias_relevantes_7d = [
    n for n in noticias_7d
    if n.get("score", 0) >= 65
]

if materias_relevantes_7d:

    materia_destaque = max(
        materias_relevantes_7d,
        key=lambda n: (
            n.get("score", 0),
            n.get("data") or datetime.min.replace(tzinfo=FUSO_BRASIL)
        )
    )

    with st.container(border=True):

        st.markdown(
            """
            <div style="
                background:rgba(100,116,139,.07);
                border:1px solid rgba(100,116,139,.10);
                border-radius:9px;
                padding:8px 12px;
                margin:-4px -4px 12px -4px;
                font-size:17px;
                font-weight:750;
                color:#27324a;
            ">
                ⭐ Matéria mais importante dos últimos 7 dias
            </div>
            """,
            unsafe_allow_html=True
        )

        nivel = (
            "🔴 Crítica"
            if materia_destaque.get("score", 0) >= 85
            else "🟠 Alta relevância"
        )

        st.markdown(
            f"{nivel}  •  📰 **{materia_destaque.get('veiculo', 'Fonte não identificada')}**"
        )

        st.markdown(
            f"### {materia_destaque.get('titulo', 'Sem título')}"
        )

        resumo_destaque = (
            materia_destaque.get("resumo") or ""
        ).strip()

        if len(resumo_destaque) > 350:
            resumo_destaque = resumo_destaque[:350].rstrip() + "..."

        if resumo_destaque:
            st.write(resumo_destaque)

        col_dest_1, col_dest_2 = st.columns([1, 1], gap="small")

        with col_dest_1:
            st.link_button(
                "**Ler matéria ↗**",
                materia_destaque["link"],
                key="ler_materia_destaque_7d"
            )

        with col_dest_2:

            titulo_whatsapp = (
                str(materia_destaque.get("titulo") or "")
                .replace("*", "")
                .strip()
            )

            texto_whatsapp = (
                f"*{titulo_whatsapp}*\n\n"
                f"{materia_destaque['link']}"
            )

            whatsapp_url = (
                "https://wa.me/?text="
                + quote(texto_whatsapp)
            )

            st.link_button(
                "📲 Compartilhar no WhatsApp",
                whatsapp_url,
                key="whatsapp_materia_destaque_7d"
            )


# ============================================================
# MÉTRICAS
# ============================================================

with st.container(border=True, key="metricas-centralizadas"):
    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric(
            "📰 Total de notícias",
            len(noticias_periodo)
        )

    with m2:
        st.metric(
            "🔴 Críticas",
            len(criticas)
        )

    with m3:
        st.metric(
            "🟠 Altas",
            len(altas)
        )

    with m4:
        st.metric(
            "🟡 Médias",
            len(medias)
        )

    with m5:
        st.metric(
            "⚪ Menções",
            len(mencoes)
        )


# ============================================================
# FILTROS
# ============================================================

INSTITUICOES_FILTRO = {
    "TCE-MG": "TCE-MG",
    "MPMG": "MPMG",
    "ALMG": "ALMG",
    "Procuradoria": "Procuradoria",
    "TJMG": "TJMG",
    "Atricon": "Atricon",
    "IRB": "IRB",
}

st.subheader("🔎 Monitorar")

todas_pessoas = []
for grupo in PESSOAS.values():
    todas_pessoas.extend(grupo.keys())

f1, f2, f3, f4 = st.columns(4)

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

with f4:
    filtro_instituicao = st.selectbox(
        "🏛️ Instituição",
        ["Todas"] + list(INSTITUICOES_FILTRO.keys())
    )

f5, f6, f7 = st.columns([1.05, 1.05, 0.85])

with f5:
    filtro_relevancia = st.selectbox(
        "🎯 Relevância",
        ["Todas", "🔴 Crítica", "🟠 Alta", "🟡 Média", "⚪ Menção"]
    )

with f6:
    busca = st.text_input(
        "🔍 Buscar palavra",
        placeholder="Ex.: Copasa, mineração, transporte..."
    )

with f7:
    with st.container(key="apenas-relevantes-box"):
        apenas_relevantes = st.checkbox(
            "🎯 Apenas relevantes (🔴 + 🟠)"
        )

# A abrangência agora é controlada pelos botões ao lado de
# 'Notícias monitoradas', sem abrir outra página.
filtro_abrangencia = st.session_state.get("abrangencia_botao", "Todas")


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

if filtro_instituicao != "Todas":
    filtradas = [
        n for n in filtradas
        if filtro_instituicao in n.get("instituicoes", [])
    ]

if filtro_abrangencia != "Todas":
    filtradas = [
        n for n in filtradas
        if n.get("abrangencia") == filtro_abrangencia
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

        data = formatar_horario_noticia(
            noticia.get("data")
        )

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

# ============================================================
# RESULTADOS
# ============================================================
col_titulo, col_estadual, col_nacional = st.columns([4.6, 1.8, 1.8])

with col_titulo:
    st.subheader("📰 Notícias monitoradas")

with col_estadual:
    with st.container(key="abrangencia-estadual"):
        if st.button(
            "Abrangência Estadual - MG",
            key="btn_abrangencia_estadual",
            use_container_width=True
        ):
            if st.session_state.get("abrangencia_botao", "Todas") == "Minas Gerais":
                st.session_state["abrangencia_botao"] = "Todas"
            else:
                st.session_state["abrangencia_botao"] = "Minas Gerais"
            st.rerun()

with col_nacional:
    with st.container(key="abrangencia-nacional"):
        if st.button(
            "Abrangência Nacional - BR",
            key="btn_abrangencia_nacional",
            use_container_width=True
        ):
            if st.session_state.get("abrangencia_botao", "Todas") == "Nacional":
                st.session_state["abrangencia_botao"] = "Todas"
            else:
                st.session_state["abrangencia_botao"] = "Nacional"
            st.rerun()

st.caption(
    f"{len(filtradas)} notícias encontradas no período selecionado."
)

if not filtradas:

    st.info(
        "Nenhuma notícia encontrada com os filtros selecionados."
    )

else:

    for i, noticia in enumerate(filtradas):

        data_formatada = formatar_horario_noticia(
            noticia.get("data")
        )

        with st.container(border=True):

            col_main, col_time = st.columns(
                [6, 1],
                gap="medium"
            )

            with col_main:

                st.markdown(
                    f"{noticia['bolinha']} **{noticia['titulo']}**"
                )

                meta = f"📰 {noticia['veiculo']}"

                if data_formatada:
                    meta += f"  •  📅 {data_formatada}"

                st.caption(meta)

                tags = []

                for pessoa in noticia.get("pessoas", [])[:4]:
                    tags.append(f"👤 {pessoa}")

                for tema in noticia.get("temas", [])[:4]:
                    tags.append(tema)

                if tags:
                    st.write("  •  ".join(tags))

                resumo = noticia.get("resumo") or ""

                if len(resumo) > 350:
                    resumo = resumo[:350] + "..."

                if resumo:
                    st.write(resumo)

                col_ler, col_whatsapp = st.columns(
                    [1, 1],
                    gap="small"
                )

                with col_ler:

                    st.link_button(
                        "**Ler matéria ↗**",
                        noticia["link"],
                        key=f"ler_materia_{i}_{hash(noticia['link'])}"
                    )

                # WhatsApp: título em negrito, espaço e link.
                titulo_whatsapp = (
                    str(noticia.get("titulo") or "")
                    .replace("*", "")
                    .strip()
                )

                texto_whatsapp = (
                    f"*{titulo_whatsapp}*\n\n"
                    f"{noticia['link']}"
                )

                whatsapp_url = (
                    "https://wa.me/?text="
                    + quote(texto_whatsapp)
                )

                with col_whatsapp:

                    st.link_button(
                        "📲 Compartilhar no WhatsApp",
                        whatsapp_url,
                        key=f"whatsapp_materia_{i}_{hash(noticia['link'])}"
                    )

            with col_time:

                if data_formatada:
                    st.caption(data_formatada)


# ============================================================
# RODAPÉ
# ============================================================

st.caption(
    "As notícias são classificadas automaticamente com base em relevância para o TCE-MG."
)
