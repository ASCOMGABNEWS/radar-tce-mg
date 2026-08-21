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
from streamlit_autorefresh import st_autorefresh
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote
from urllib.request import Request, urlopen
from openai import OpenAI

import re
import html
from difflib import SequenceMatcher
from collections import Counter
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    page_icon="radar.png",
    layout="wide"
)


# ============================================================
# FONTES
# ============================================================

FONTES = {'Estado de Minas': 'https://news.google.com/rss/search?q=site%3Aem.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Itatiaia': 'https://news.google.com/rss/search?q=site%3Aitatiaia.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'O TEMPO': 'https://news.google.com/rss/search?q=site%3Aotempo.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Hoje em Dia': 'https://news.google.com/rss/search?q=site%3Ahojeemdia.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Tribuna de Minas': 'https://news.google.com/rss/search?q=site%3Atribunademinas.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Diário do Comércio': 'https://news.google.com/rss/search?q=site%3Adiariodocomercio.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'BHAZ': 'https://news.google.com/rss/search?q=site%3Abhaz.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Agência Minas': 'https://news.google.com/rss/search?q=site%3Aagenciaminas.mg.gov.br+%22Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'O Fator': 'https://news.google.com/rss/search?q=site%3Aofator.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Edição do Brasil': 'https://news.google.com/rss/search?q=site%3Aedicaodobrasil.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Moon BH': 'https://news.google.com/rss/search?q=site%3Amoonbh.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'G1 Minas': 'https://news.google.com/rss/search?q=site%3Ag1.globo.com%2Fmg+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Folha de S.Paulo': 'https://news.google.com/rss/search?q=site%3Afolha.uol.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'O Globo': 'https://news.google.com/rss/search?q=site%3Aoglobo.globo.com+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Correio Braziliense': 'https://news.google.com/rss/search?q=site%3Acorreiobraziliense.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Poder360': 'https://news.google.com/rss/search?q=site%3Apoder360.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'O Antagonista': 'https://news.google.com/rss/search?q=site%3Aoantagonista.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Brasil de Fato': 'https://news.google.com/rss/search?q=site%3Abrasildefato.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'revista piauí': 'https://news.google.com/rss/search?q=site%3Apiaui.folha.uol.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'JOTA': 'https://news.google.com/rss/search?q=site%3Ajota.info+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Migalhas': 'https://news.google.com/rss/search?q=site%3Amigalhas.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'O Bastidor': 'https://news.google.com/rss/search?q=site%3Aobastidor.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Intercept Brasil': 'https://news.google.com/rss/search?q=site%3Aintercept.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Bem Minas': 'https://news.google.com/rss/search?q=site%3Abemminas.com.br+%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'TCE-MG': 'https://news.google.com/rss/search?q=%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'TCE MG': 'https://news.google.com/rss/search?q=%22TCE%20MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Tribunal de Contas MG': 'https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22+%22Minas%20Gerais%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Atricon': 'https://news.google.com/rss/search?q=%22Atricon%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'IRB': 'https://news.google.com/rss/search?q=%22Instituto%20Rui%20Barbosa%22+OR+%22IRB%22+%22Tribunais%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Tribunais de Contas': 'https://news.google.com/rss/search?q=%22Tribunais%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Tribunal de Contas': 'https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Presidentes de Tribunais de Contas': 'https://news.google.com/rss/search?q=%22presidente%20do%20Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Conselheiros de Tribunais de Contas': 'https://news.google.com/rss/search?q=%22conselheiro%22+%22Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'TCEs': 'https://news.google.com/rss/search?q=%22TCE%22+%22Tribunal%20de%20Contas%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Durval Ângelo': 'https://news.google.com/rss/search?q=%22Durval%20Ângelo%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Agostinho Patrus': 'https://news.google.com/rss/search?q=%22Agostinho%20Patrus%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Gilberto Diniz': 'https://news.google.com/rss/search?q=%22Gilberto%20Diniz%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Alencar da Silveira': 'https://news.google.com/rss/search?q=%22Alencar%20da%20Silveira%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Ione Pinheiro': 'https://news.google.com/rss/search?q=%22Ione%20Pinheiro%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Tadeu Martins Leite / Tadeuzinho': 'https://news.google.com/rss/search?q=%22Tadeu%20Martins%20Leite%22+OR+%22Tadeuzinho%22&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Licurgo Mourão': 'https://news.google.com/rss/search?q=%22Licurgo%20Mourão%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Hamilton Coelho': 'https://news.google.com/rss/search?q=%22Hamilton%20Coelho%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Adonias Fernandes': 'https://news.google.com/rss/search?q=%22Adonias%20Fernandes%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419', 'Telmo Passareli': 'https://news.google.com/rss/search?q=%22Telmo%20Passareli%22+TCE&hl=pt-BR&gl=BR&ceid=BR:pt-419'}

# As referências de imprensa permanecem cadastradas acima para identificação
# da origem. A coleta, porém, NÃO faz uma chamada por jornal: agrupa os veículos
# em poucas consultas do Google News para manter o Radar rápido.

BUSCAS_RADAR = [
    ("TCE-MG", 'site:tce.mg.gov.br/noticia'),
    ("Tribunais de Contas", '("TCE-MG" OR "Tribunal de Contas de Minas Gerais" OR "Agostinho Patrus" OR "Durval Ângelo" OR TCU OR "Tribunal de Contas")'),
    ("Imprensa de Minas", f'({mg_sites}) ("TCE-MG" OR "Tribunal de Contas" OR TCU OR conselheiro OR "controle externo" OR fiscalização OR auditoria OR conciliação OR "mesa de conciliação" OR acórdão OR processo)'),
    ("Imprensa nacional", f'({nat_sites}) ("TCE-MG" OR "Tribunal de Contas" OR TCU OR "Tribunal de Contas" OR conselheiro OR "controle externo" OR fiscalização OR auditoria OR conciliação OR acórdão OR processo)'),
    ("Órgãos complementares", '(site:almg.gov.br OR site:mpmg.mp.br OR site:tjmg.jus.br) ("TCE-MG" OR "Tribunal de Contas" OR TCU OR conselheiro OR "controle externo" OR acórdão OR processo)'),
]

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
        "infraestrutura",
        "construção"
    ],

    "📚 Obras literárias": [
        "obra literária", "obras literárias", "literatura",
        "literário", "literária", "livro", "livros",
        "romance", "poesia", "poema", "poemas",
        "escritor", "escritora"
    ],

    "🤝 Conciliação": [
        "conciliação",
        "mesa de conciliação",
        "mesa de negociação",
        "solução consensual",
        "consensualidade",
        "consenso",
        "mediação",
        "prevenção e resolução de conflitos",
        "acordo"
    ],

    "📣 Comunicação": [
        "comunicação pública",
        "comunicação institucional",
        "comunicação pública digital",
        "linguagem simples",
        "transparência",
        "redes sociais",
        "imprensa",
        "comunicação"
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

    "🏛️ Institucional": [
        "institucional",
        "órgão público",
        "órgãos públicos",
        "poder público",
        "administração pública",
        "gestão pública",
        "entidade pública",
        "entidades públicas",
        "serviço público",
        "serviços públicos",
        "governança pública",
        "governança",
        "política pública",
        "políticas públicas",
        "prestação de contas",
        "responsabilidade fiscal",
        "controle interno",
        "transparência pública",
        "gestão municipal",
        "gestão estadual"
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
    """Obtém a data mais recente disponível no feed, em horário de Brasília."""
    try:
        # Google News/RSS pode informar uma atualização mais recente que
        # a publicação original. Para o filtro de período, a atualização
        # é o momento correto para considerar a notícia como nova.
        partes_data = None

        if getattr(item, "updated_parsed", None):
            partes_data = item.updated_parsed
        elif getattr(item, "published_parsed", None):
            partes_data = item.published_parsed

        if partes_data:
            data_utc = datetime(
                *partes_data[:6],
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
    texto = (str(titulo or "") + " " + str(resumo or "")).lower()
    encontrados = []

    # Literatura tem prioridade semântica: "obra literária" nunca deve ser
    # confundida com obra pública. Evitamos também o uso de "obra" isolado.
    termos_literarios = (
        "obra literária", "obras literárias", "literatura",
        "literário", "literária", "livro", "livros",
        "romance", "poesia", "poema", "poemas", "escritor", "escritora"
    )
    eh_literatura = any(t in texto for t in termos_literarios)

    for tema, palavras in TEMAS.items():
        if tema == "🏗️ Obras públicas" and eh_literatura:
            continue
        for palavra in palavras:
            p = palavra.lower().strip()
            if not p:
                continue
            # Para termos curtos, exige fronteira de palavra; para frases,
            # a ocorrência literal é suficiente.
            if " " not in p:
                if re.search(r"(?<![\wáàâãéêíóôõúçü])" + re.escape(p) + r"(?![\wáàâãéêíóôõúçü])", texto):
                    encontrados.append(tema)
                    break
            elif p in texto:
                encontrados.append(tema)
                break

    # Garante a nova tag mesmo se uma variação de literatura não estiver
    # cadastrada em TEMAS por alguma versão antiga do arquivo.
    if eh_literatura and "📚 Obras literárias" not in encontrados:
        encontrados.append("📚 Obras literárias")

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
        "TCE-MG": [
            "tce-mg", "tce mg", "tribunal de contas de minas gerais",
            "tribunal de contas do estado de minas gerais"
        ],
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
        "Outros Tribunais de Contas": [
            "tce-ac", "tce-al", "tce-ap", "tce-am", "tce-ba",
            "tce-ce", "tce-df", "tce-es", "tce-go", "tce-ma",
            "tce-mt", "tce-ms", "tce-pa", "tce-pb", "tce-pr",
            "tce-pe", "tce-pi", "tce-rj", "tce-rn", "tce-rs",
            "tce-ro", "tce-rr", "tce-sc", "tce-sp", "tce-se",
            "tce-to", "tribunal de contas do maranhão",
            "tribunal de contas de são paulo",
            "tribunal de contas do paraná",
            "tribunal de contas do rio de janeiro",
            "tribunal de contas do rio grande do sul",
            "tribunal de contas do estado do maranhão",
            "tribunal de contas do estado de goiás",
            "tribunal de contas do estado de são paulo",
            "tribunal de contas do estado do paraná",
            "tribunal de contas do estado do rio de janeiro"
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

    # Relevância institucional básica.
    if "tce-mg" in texto:
        score += 35
    elif "tce mg" in texto:
        score += 30
    elif "tribunal de contas" in texto:
        score += 25

    if "tcu" in texto or "tribunal de contas da união" in texto:
        score += 10

    if "atricon" in texto or "instituto rui barbosa" in texto or " irb" in texto:
        score += 8

    # Conteúdo institucional é relevante mesmo quando a matéria não cita
    # diretamente TCE-MG. Isso captura notícias sobre órgãos públicos,
    # administração, governança e políticas públicas.
    termos_institucionais = [
        "órgãos públicos", "órgão público", "administração pública",
        "poder público", "gestão pública", "entidades públicas",
        "entidade pública", "serviço público", "serviços públicos",
        "governança pública", "governança", "políticas públicas",
        "política pública", "prestação de contas", "responsabilidade fiscal",
        "controle interno", "transparência pública", "gestão municipal",
        "gestão estadual"
    ]
    score += min(sum(1 for t in termos_institucionais if t in texto) * 4, 16)

    # Autoridades de Tribunais de Contas.
    termos_autoridade = [
        "presidente do tce",
        "presidente do tribunal de contas",
        "conselheiro do tce",
        "conselheira do tce",
        "conselheiro do tribunal de contas",
        "conselheira do tribunal de contas",
        "ministro do tcu",
        "ministra do tcu",
        "presidente do tcu",
    ]

    autoridade_tc = any(t in texto for t in termos_autoridade)

    if autoridade_tc:
        score += 15

    # STF só ganha peso quando há relação com o universo do Radar.
    contexto_controle = any(t in texto for t in [
        "tce",
        "tcu",
        "tribunal de contas",
        "atricon",
        "irb",
        "controle externo",
        "fiscalização de contas",
    ])

    if ("stf" in texto or "supremo tribunal federal" in texto) and contexto_controle:
        score += 15

    score += len(pessoas) * 12
    score += len(temas) * 5

    # Fatos graves: não podem ficar escondidos como notícia média
    # quando envolvem autoridades/órgãos do controle externo.
    termos_graves = [
        "afastado", "afastada", "afastamento",
        "preso", "presa", "prisão",
        "denúncia", "denunciado", "denunciada",
        "investigação", "investigado", "investigada",
        "operação", "busca e apreensão",
        "cassado", "cassada", "cassação",
        "corrupção", "fraude", "improbidade", "crime",
    ]

    gravidade = any(t in texto for t in termos_graves)
    contexto_institucional = any(t in texto for t in [
        "tce", "tcu", "tribunal de contas",
        "conselheiro", "conselheira",
        "presidente do tce", "presidente do tribunal de contas",
        "ministro do tcu", "ministra do tcu",
        "atricon", "irb",
    ])

    if gravidade and contexto_institucional:
        # Piso de ALTA para fato grave envolvendo controle externo.
        score = max(score, 75)

        # Casos de maior gravidade: prisão, operação, busca e apreensão
        # ou corrupção/crime envolvendo autoridade/TC.
        gravidade_maxima = any(t in texto for t in [
            "prisão", "preso", "presa",
            "operação", "busca e apreensão",
            "corrupção", "crime",
        ])

        if gravidade_maxima and (autoridade_tc or "tcu" in texto or "tce" in texto or "tribunal de contas" in texto):
            score = max(score, 85)

    # Regra explícita para casos como presidente/conselheiro de TCE afastado,
    # mesmo quando o RSS entrega um título/resumo com formulação diferente.
    autoridade_ou_tc = (
        autoridade_tc
        or "tce" in texto
        or "tcu" in texto
        or "tribunal de contas" in texto
    )
    fato_grave_forte = any(t in texto for t in [
        "afastado", "afastada", "afastamento",
        "prisão", "preso", "presa",
        "operação", "busca e apreensão",
        "corrupção", "fraude", "improbidade", "crime",
        "denúncia", "denunciado", "denunciada",
        "investigação", "investigado", "investigada",
    ])
    if autoridade_ou_tc and fato_grave_forte:
        score = max(score, 85)

    # Ações institucionais relevantes.
    termos_acao = [
        "determina", "decide", "suspende", "condena", "multa",
        "auditoria", "fiscalização", "julgamento", "acórdão",
        "irregularidade", "recomenda", "processo", "ressarcimento",
        "contas",
    ]

    for termo in termos_acao:
        if termo in texto:
            score += 5

    if "r$" in texto:
        score += 5

    return min(score, 100)


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
    "G1 - Tribunais de Contas",
    "O Globo - Tribunais de Contas",
    "STF - Tribunais de Contas",
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
    "TCE-MG",
    "ALMG",
    "MPMG",
    "TJMG",
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
    "acre", "alagoas", "amapá", "amazonas", "bahia", "ceará", "distrito federal",
    "espírito santo", "goiás", "maranhão", "mato grosso", "mato grosso do sul",
    "pará", "paraíba", "paraná", "pernambuco", "piauí", "rio de janeiro",
    "rio grande do norte", "rio grande do sul", "rondônia", "roraima", "santa catarina",
    "são paulo", "sergipe", "tocantins",
    "tce-ac", "tce-al", "tce-ap", "tce-am", "tce-ba", "tce-ce", "tce-df", "tce-es",
    "tce-go", "tce-ma", "tce-mt", "tce-ms", "tce-pa", "tce-pb", "tce-pr", "tce-pe",
    "tce-pi", "tce-rj", "tce-rn", "tce-rs", "tce-ro", "tce-rr", "tce-sc", "tce-sp",
    "tce-se", "tce-to",
)

def classificar_abrangencia(veiculo, titulo="", resumo=""):
    texto = " ".join([
        str(titulo or ""),
        str(resumo or ""),
        str(veiculo or "")
    ]).lower()

    # Primeiro verificamos o conteúdo da notícia. Uma fonte mineira (como
    # O TEMPO) também publica matérias sobre outros estados; nesse caso,
    # a matéria NÃO pode ser tratada como mineira só por causa do veículo.
    if any(termo in texto for termo in OUTROS_ESTADOS):
        return "Nacional"

    # Só depois usamos a origem mineira do veículo como sinal de MG.
    if any(f.lower() in str(veiculo or "").lower() for f in FONTES_MINAS):
        return "Minas Gerais"

    # Só reconhecer MG com expressões explícitas. Não usar "mg" solto,
    # pois isso gera falsos positivos em palavras comuns.
    termos_mg = (
        "tce-mg", "tce mg", "tce de minas gerais",
        "tribunal de contas de minas gerais",
        "tribunal de contas do estado de minas gerais",
        "tribunal de contas de mg",
        "minas gerais", "governo de minas", "estado de minas gerais",
        "belo horizonte", "minas gerais"
    )

    if any(termo in texto for termo in termos_mg):
        return "Minas Gerais"

    return "Nacional"



def normalizar_titulo_dedupe(titulo):
    texto = limpar_texto(titulo).lower()
    texto = re.sub(r"[^a-z0-9áàâãéêíóôõúçü ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def titulo_duplicado(titulo, titulos_existentes):
    chave = normalizar_titulo_dedupe(titulo)
    if not chave:
        return False
    for existente in titulos_existentes:
        if chave == existente:
            return True
        if len(chave) >= 35 and len(existente) >= 35:
            if SequenceMatcher(None, chave, existente).ratio() >= 0.91:
                return True
    return False



# ============================================================
# COLETA
# ============================================================
@st.cache_data(ttl=300, show_spinner=False)
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
        
# Instituições disponíveis para classificação e filtro.
# Deve ser definido antes de buscar_noticias(), pois a coleta o utiliza.
INSTITUICOES_FILTRO = {
    "TCE-MG": "TCE-MG",
    "MPMG": "MPMG",
    "ALMG": "ALMG",
    "Procuradoria": "Procuradoria",
    "TJMG": "TJMG",
    "Órgãos complementares": "Órgãos complementares",
    "Atricon": "Atricon",
    "IRB": "IRB",
    "TCU": "TCU",
    "Outros Tribunais de Contas": "Outros Tribunais de Contas",
}

# Buscas temáticas nos portais oficiais. O Radar NÃO varre os portais inteiros:
# procura apenas assuntos que fazem parte do monitoramento.
# Consultas no Google News. O TCE-MG recebe várias buscas independentes:
# uma busca ampla garante que uma matéria relevante não dependa de uma única
# combinação de palavras; as demais refinam conciliação, comunicação, controle etc.
# ALMG/MPMG/TJMG continuam como fontes complementares via Google News.
BUSCAS_OFICIAIS = [
    ("TCE-MG", 'site:tce.mg.gov.br/noticia'),
    ("TCE-MG", 'site:tce.mg.gov.br/noticia ("Agostinho Patrus" OR "Durval Ângelo" OR conciliação OR "controle externo" OR fiscalização OR auditoria)'),
    ("TCE-MG", 'site:tce.mg.gov.br/noticia (conselheiro OR acórdão OR processo OR decisão OR licitação OR concessão OR comunicação)'),
    ("Órgãos complementares", '(site:almg.gov.br OR site:mpmg.mp.br OR site:tjmg.jus.br) ("TCE-MG" OR "Tribunal de Contas" OR TCU OR conselheiro OR "controle externo" OR "processo do TCE" OR "decisão do TCE")'),
]



# ============================================================
# REGRA-MÃE DO RADAR
# ============================================================
# O Radar é focado em Tribunais de Contas. Órgãos como ALMG, MPMG e TJMG
# só entram quando a notícia tem conexão explícita com TCE/TCU/Tribunais de
# Contas, conselheiros, processos, decisões ou atuação de controle externo.
TERMOS_CONEXAO_TC = (
    "tce-mg", "tce mg", "tribunal de contas de minas gerais",
    "tribunal de contas", "tribunais de contas", "tcu",
    "conselheiro do tce", "conselheira do tce",
    "conselheiro do tribunal de contas", "conselheira do tribunal de contas",
    "ministro do tcu", "ministra do tcu", "presidente do tce",
    "presidente do tribunal de contas", "presidente do tcu",
    "acórdão do tce", "acordao do tce", "processo no tce",
    "processo do tce", "processo no tribunal de contas",
    "processo do tribunal de contas", "decisão do tce", "decisao do tce",
    "decisão do tribunal de contas", "decisao do tribunal de contas",
    "auditoria do tce", "fiscalização do tce", "fiscalizacao do tce",
    "denúncia ao tce", "denuncia ao tce", "representação no tce",
    "representacao no tce", "mesa de conciliação do tce",
    "mesa de conciliacao do tce", "conciliação no tce",
    "conciliacao no tce", "controle externo"
)


def noticia_tem_conexao_tc(titulo, resumo, veiculo=""):
    texto = " ".join([str(titulo or ""), str(resumo or ""), str(veiculo or "")]).lower()
    return any(t in texto for t in TERMOS_CONEXAO_TC)


def rss_url_para_busca(q):
    return 'https://news.google.com/rss/search?q=' + quote(q) + '&hl=pt-BR&gl=BR&ceid=BR:pt-419'


def baixar_feed(args):
    nome, url = args
    try:
        request = Request(url, headers={"User-Agent": "Radar-TCE-MG/2.0"})
        with urlopen(request, timeout=2) as resposta:
            return nome, feedparser.parse(resposta.read())
    except Exception:
        return nome, None


@st.cache_data(ttl=600, show_spinner=False)
def buscar_noticias():
    noticias = []
    links = set()
    titulos = []
    limite = datetime.now(FUSO_BRASIL) - timedelta(days=7)

    def adicionar(reg, monitoramento):
        link = reg.get("link", "")
        titulo = reg.get("titulo", "Sem título")
        if not link or titulo_duplicado(titulo, titulos):
            return False

        data = reg.get("data")
        if data and data < limite:
            return False

        resumo = limpar_texto(reg.get("resumo", ""))
        veiculo = reg.get("veiculo") or monitoramento

        # ALMG, MPMG e TJMG são fontes complementares. Não queremos
        # notícias desses órgãos por si só: elas só entram quando há conexão
        # com Tribunal de Contas/TCE/TCU/processo/decisão/controle externo.
        if monitoramento in {"ALMG", "MPMG", "TJMG"} and not noticia_tem_conexao_tc(titulo, resumo, veiculo):
            return False

        pessoas = identificar_pessoas(titulo, resumo)
        temas = identificar_temas(titulo, resumo)
        instituicoes = identificar_instituicoes(titulo, resumo)

        pessoa_fonte = MAPA_FONTE_PESSOA.get(monitoramento)
        if pessoa_fonte and pessoa_fonte not in pessoas:
            pessoas.append(pessoa_fonte)

        if monitoramento in INSTITUICOES_FILTRO and monitoramento not in instituicoes:
            instituicoes.append(monitoramento)

        score = calcular_relevancia(titulo, resumo, monitoramento, temas, pessoas)
        abr = classificar_abrangencia(veiculo, titulo, resumo)

        noticias.append({
            "titulo": titulo,
            "resumo": resumo,
            "link": link,
            "monitoramento": monitoramento,
            "veiculo": veiculo,
            "abrangencia": abr,
            "data": data,
            "score": score,
            "bolinha": classificar(score),
            "temas": temas,
            "pessoas": pessoas,
            "instituicoes": instituicoes,
        })
        links.add(link)
        titulos.append(normalizar_titulo_dedupe(titulo))
        return True

    # IMPORTANTE: não fazemos scraping direto dos quatro portais.
    # Cada portal entra como fonte de referência, mas somente para os assuntos
    # que interessam ao Radar. As quatro buscas rodam em paralelo.
    # Cada consulta recebe uma chave própria. Isso é importante: se fizermos
    # várias buscas do TCE-MG com o mesmo nome, um resultado não pode sobrescrever
    # o outro no dicionário.
    tarefas = [
        (f"{nome}__{i}", rss_url_para_busca(query))
        for i, (nome, query) in enumerate(BUSCAS_RADAR)
    ]
    tarefas_oficiais = tarefas
    resultados = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(baixar_feed, tarefa) for tarefa in tarefas]
        for future in as_completed(futures):
            chave, feed = future.result()
            if feed is not None:
                resultados[chave] = feed

    # Primeiro as buscas oficiais. A busca ampla do TCE-MG é intencional:
    # ela permite encontrar matérias que não tenham uma palavra-chave óbvia
    # no título. Depois as buscas temáticas ampliam a cobertura.
    for chave, _ in tarefas_oficiais:
        feed = resultados.get(chave)
        if not feed:
            continue

        nome = chave.split("__", 1)[0]

        for item in feed.entries:
            data = obter_data(item)
            adicionar({
                "titulo": limpar_texto(item.get("title", "")),
                "resumo": limpar_texto(item.get("summary", "")),
                "link": item.get("link", ""),
                "veiculo": (
                    (item.get("source", {}) or {}).get("title")
                    or nome
                ),
                "data": data,
            }, nome)

    # As cinco consultas acima já cobrem TCE-MG, imprensa e órgãos complementares.

    noticias.sort(
        key=lambda x: (
            x["score"],
            x["data"] or datetime.min.replace(tzinfo=FUSO_BRASIL)
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
    text-align: center !important;
    align-items: center !important;
}
.st-key-metricas-centralizadas [data-testid="stMetricLabel"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    text-align: center !important;
    font-weight: 800 !important;
}
.st-key-metricas-centralizadas [data-testid="stMetricLabel"] p {
    font-weight: 800 !important;
    text-align: center !important;
    width: 100%;
}
.st-key-metricas-centralizadas [data-testid="stMetricValue"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    text-align: center !important;
}
.st-key-metricas-centralizadas [data-testid="stMetricValue"] > div {
    width: 100% !important;
    text-align: center !important;
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
.st-key-abrangencia-total button {
    background: #667085 !important;
    color: white !important;
    border: 1px solid #667085 !important;
}
.st-key-abrangencia-total button:hover {
    background: #475467 !important;
    color: white !important;
    border-color: #475467 !important;
}

.st-key-filtros-centralizados [data-testid="stWidgetLabel"] {
    justify-content: center;
    width: 100%;
    text-align: center;
}
.st-key-filtros-centralizados [data-testid="stWidgetLabel"] p {
    text-align: center !important;
    width: 100%;
}
.st-key-filtros-centralizados [data-testid="stCheckbox"] {
    justify-content: center;
    width: 100%;
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
    font-size:12px;
    line-height:1.4;
    color:#667085;
    margin-top:3px;
    max-width:850px;
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

.news-count-caption {
    color:#98a2b3;
    font-size:14px;
    font-weight:800;
    margin-top:2px;
    margin-bottom:12px;
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
# ATUALIZAÇÃO AUTOMÁTICA
# ============================================================

st_autorefresh(interval=5 * 60 * 1000, key="radar_auto_refresh")

# ============================================================
# CABEÇALHO
# ============================================================

import base64
from pathlib import Path

radar_icon_path = Path(__file__).with_name("radar.png")
try:
    radar_icon_b64 = base64.b64encode(radar_icon_path.read_bytes()).decode("utf-8")
except Exception:
    radar_icon_b64 = ""

agora = datetime.now(FUSO_BRASIL)

st.markdown(
    f"""
    <div class="radar-header">
        <div class="radar-brand">
            <div class="radar-icon"><img src="data:image/png;base64,{radar_icon_b64}" style="width:78px;height:78px;object-fit:contain;"></div>
            <div>
                <div class="radar-title">Radar TCE-MG</div>
                <div class="radar-subtitle">
                    Monitoramento inteligente do Gab. Agostinho Patrus sobre notícias<br>
                    relacionadas ao Tribunal de Contas de Minas Gerais
                </div>
            </div>
        </div>
        <div class="radar-update">
            Última atualização: <strong>{agora.strftime("%d/%m/%Y %H:%M")}</strong><br>
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



def normalizar_titulo_dedupe(titulo):
    texto = limpar_texto(titulo).lower()
    texto = re.sub(r"[^a-z0-9áàâãéêíóôõúçü ]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def titulo_duplicado(titulo, titulos_existentes):
    chave = normalizar_titulo_dedupe(titulo)
    if not chave:
        return False
    for existente in titulos_existentes:
        if chave == existente:
            return True
        if len(chave) >= 35 and len(existente) >= 35:
            if SequenceMatcher(None, chave, existente).ratio() >= 0.91:
                return True
    return False



# ============================================================
# COLETA

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
# DUAS MATÉRIAS MAIS IMPORTANTES DOS ÚLTIMOS 7 DIAS — MINAS GERAIS
# ============================================================

limite_destaque_7d = datetime.now(FUSO_BRASIL) - timedelta(days=7)

# O destaque é EXCLUSIVO de Minas Gerais e somente para notícias críticas.
# Isso evita, por exemplo, que uma matéria do O TEMPO sobre o Maranhão
# apareça aqui apenas porque o veículo é mineiro.
criticas_mg_7d = [
    n for n in noticias
    if (
        n.get("data")
        and n["data"] >= limite_destaque_7d
        and n.get("abrangencia") == "Minas Gerais"
        and n.get("score", 0) >= 85
    )
]

criticas_mg_7d.sort(
    key=lambda n: (
        n.get("score", 0),
        n.get("data") or datetime.min.replace(tzinfo=FUSO_BRASIL)
    ),
    reverse=True
)

criticas_mg_7d = criticas_mg_7d[:2]

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
            ⭐ Matérias mais importantes dos últimos 7 dias em Minas Gerais
        </div>
        """,
        unsafe_allow_html=True
    )

    if criticas_mg_7d:
        cards = ""

        for noticia in criticas_mg_7d:
            titulo = esc_html(noticia.get("titulo", "Sem título"))
            veiculo = esc_html(noticia.get("veiculo", "Fonte não identificada"))
            data = esc_html(formatar_horario_noticia(noticia.get("data")))
            resumo = esc_html((noticia.get("resumo") or "").strip())
            if len(resumo) > 260:
                resumo = resumo[:260].rstrip() + "..."
            link = esc_html(noticia.get("link", ""))

            cards += f"""
            <article style="
                flex:0 0 min(78vw, 760px);
                scroll-snap-align:start;
                box-sizing:border-box;
                border:1px solid rgba(100,116,139,.16);
                border-radius:12px;
                padding:18px 20px;
                background:#fff;
            ">
                <div style="
                    font-size:14px;
                    font-weight:700;
                    color:#b42318;
                    margin-bottom:10px;
                ">🔴 Crítica • 📰 {veiculo} • 📅 {data}</div>

                <div style="
                    font-size:25px;
                    line-height:1.18;
                    font-weight:800;
                    color:#27324a;
                    margin-bottom:12px;
                ">{titulo}</div>

                {f'<div style="font-size:15px;line-height:1.45;color:#475467;margin-bottom:14px;">{resumo}</div>' if resumo else ''}

                <a href="{link}" target="_blank" style="
                    display:inline-block;
                    padding:9px 14px;
                    border:1px solid rgba(16,24,40,.18);
                    border-radius:8px;
                    text-decoration:none;
                    color:#27324a;
                    font-weight:700;
                    background:#fff;
                ">Ler matéria ↗</a>
            </article>
            """

        st.markdown(
            f"""
            <div style="
                display:flex;
                gap:14px;
                overflow-x:auto;
                overflow-y:hidden;
                padding:2px 2px 12px 2px;
                scroll-snap-type:x mandatory;
                -webkit-overflow-scrolling:touch;
            ">
                {cards}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="color:#98a2b3;padding:10px 2px;">Nenhuma matéria crítica de Minas Gerais nos últimos 7 dias.</div>',
            unsafe_allow_html=True
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
    filtro_instituicao = st.selectbox(
        "🏛️ Instituição",
        ["Todas"] + list(INSTITUICOES_FILTRO.keys())
    )

with st.container(key="filtros-centralizados"):
    f5, f6 = st.columns(2, gap="medium")

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
col_titulo, col_total, col_estadual, col_nacional = st.columns([3.4, 1.4, 1.4, 1.4], gap="medium")

# Contagem dinâmica da lista atualmente filtrada.
qtd_criticas_filtradas = sum(
    1 for n in filtradas if n.get("score", 0) >= 85
)
qtd_altas_filtradas = sum(
    1 for n in filtradas if 65 <= n.get("score", 0) < 85
)

with col_titulo:
    st.markdown(
        "### 📰 **Notícias monitoradas**"
    )

with col_total:
    with st.container(key="abrangencia-total"):
        if st.button(
            "Abrangência Total",
            key="btn_abrangencia_total",
            use_container_width=True
        ):
            st.session_state["abrangencia_botao"] = "Todas"
            st.rerun()

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

st.markdown(
    f'<div class="news-count-caption">{len(filtradas)} notícias encontradas ({qtd_criticas_filtradas} críticas, {qtd_altas_filtradas} altas)</div>',
    unsafe_allow_html=True
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
