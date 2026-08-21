from zoneinfo import ZoneInfo
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen
from openai import OpenAI
import re
import html
from html.parser import HTMLParser
from difflib import SequenceMatcher
from collections import Counter
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from zoneinfo import ZoneInfo
import streamlit as st
from datetime import datetime, timedelta

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")
agora = datetime.now(FUSO_BRASIL)

# ============================================================
# RADAR EM ABAS
# ============================================================

aba_midias, aba_redes = st.tabs([
    "📰 Mídias / Jornais",
    "𝕏 Redes Sociais",
])

with aba_midias:
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

    atencao = [n for n in noticias_periodo if n["score"] >= 85]
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

    atencao = [
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

                st.markdown("🔴 **Atenção**")

                st.markdown(
                    f"""
                    <div style="
                        font-size:44px;
                        font-weight:800;
                        line-height:1;
                        margin:0;
                        color:#2f3340;
                    ">{len(atencao)}</div>
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
    # MATÉRIA MAIS IMPORTANTE — MINAS GERAIS + TCE-MG
    # ============================================================

    limite_destaque_7d = datetime.now(FUSO_BRASIL) - timedelta(days=7)

    def destaque_tce_mg(n):
        """Seleciona somente destaque de MG com relação explícita ao TCE-MG."""
        if not n.get("data") or n["data"] < limite_destaque_7d:
            return False

        # O destaque é exclusivamente mineiro.
        if n.get("abrangencia") != "Minas Gerais":
            return False

        # Só entram Atenção ou Alta.
        score = n.get("score", 0)
        if score < 65:
            return False

        titulo = str(n.get("titulo") or "").lower()
        resumo = str(n.get("resumo") or "").lower()
        veiculo = str(n.get("veiculo") or "").lower()
        monitoramento = str(n.get("monitoramento") or "").lower()
        texto = " ".join([titulo, resumo, veiculo, monitoramento])

        # O destaque NÃO pode ser uma notícia apenas sobre TCU, outro TCE ou
        # controle externo genérico. Precisa haver vínculo com o TCE de Minas.
        termos_tce_mg = (
            "tce-mg",
            "tce mg",
            "tcemg",
            "tce de minas gerais",
            "tce de mg",
            "tribunal de contas de minas gerais",
            "tribunal de contas do estado de minas gerais",
            "tribunal de contas de mg",
            "tribunal de contas mineiro",
        )

        tem_tce_mg = (
            any(t in texto for t in termos_tce_mg)
            or "tce-mg" in [str(x).lower() for x in (n.get("instituicoes") or [])]
            or monitoramento == "tce-mg"
            or veiculo == "tce-mg"
        )

        return tem_tce_mg

    # Primeiro a maior nota. Em empate, a notícia mais recente.
    atencao_tce_mg_7d = [n for n in noticias if destaque_tce_mg(n)]
    atencao_tce_mg_7d.sort(
        key=lambda n: (
            n.get("score", 0),
            n.get("data") or datetime.min.replace(tzinfo=FUSO_BRASIL)
        ),
        reverse=True
    )

    with st.container(border=True):
        st.markdown(
            """
            <div style="background:rgba(100,116,139,.07);border:1px solid rgba(100,116,139,.10);border-radius:9px;padding:8px 12px;margin:-4px -4px 12px -8px;font-size:17px;font-weight:750;color:#27324a;">
                ⭐ Matéria mais importante dos últimos 7 dias em Minas Gerais
            </div>
            """,
            unsafe_allow_html=True
        )

        if atencao_tce_mg_7d:
            n = atencao_tce_mg_7d[0]
            resumo_n = (n.get("resumo") or "").strip()
            if len(resumo_n) > 320:
                resumo_n = resumo_n[:320] + "..."
            bolinha = n.get("bolinha", "🔴")
            nivel = {"🔴": "Atenção", "🟠": "Alta", "🟡": "Média", "⚪": "Menção"}.get(bolinha, "Relevante")
            st.markdown(
                f"""
                <div style="border:1px solid rgba(100,116,139,.16);border-radius:12px;padding:18px 20px 16px;background:#fff;margin-top:4px;margin-bottom:12px;">
                    <div style="font-size:14px;font-weight:700;color:#b42318;margin-bottom:12px;">
                        {bolinha} {esc_html(nivel)} &nbsp;•&nbsp; 📰 {esc_html(nome_fonte_exibicao(n.get('veiculo')))} &nbsp;•&nbsp; 📅 {esc_html(formatar_horario_noticia(n.get('data')))}
                    </div>
                    <div style="font-size:23px;line-height:1.22;font-weight:800;color:#27324a;margin-bottom:13px;">
                        {esc_html(n.get('titulo', 'Sem título'))}
                    </div>
                    {f'<div style="font-size:15px;line-height:1.5;color:#475467;margin-bottom:4px;">{esc_html(resumo_n)}</div>' if resumo_n else ''}
                </div>
                """,
                unsafe_allow_html=True
            )
            col_ler, col_whatsapp = st.columns([1, 1], gap="medium")
            with col_ler:
                st.link_button("**Ler matéria ↗**", n.get("link", ""), key=f"ler_destaque_{hash(n.get('link', ''))}")
            titulo_whatsapp = str(n.get("titulo") or "").replace("*", "").strip()
            texto_whatsapp = f"*{titulo_whatsapp}*\n\n{n.get('link', '')}"
            whatsapp_url = "https://wa.me/?text=" + quote(texto_whatsapp)
            with col_whatsapp:
                st.link_button("📲 Compartilhar no WhatsApp", whatsapp_url, key=f"whatsapp_destaque_{hash(n.get('link', ''))}")
        else:
            st.markdown('<div style="color:#98a2b3;padding:10px 2px;">Nenhuma matéria relacionada ao TCE-MG em Minas Gerais nos últimos 7 dias.</div>', unsafe_allow_html=True)


    # ============================================================
    # BARRA DE NOTÍCIAS — MINAS GERAIS
    # ============================================================

    noticias_ticker = [
        n for n in noticias_periodo
        if n.get("abrangencia") == "Minas Gerais"
        and n.get("link")
        and n.get("titulo")
    ]

    noticias_ticker.sort(
        key=lambda n: n.get("data") or datetime.min.replace(tzinfo=FUSO_BRASIL),
        reverse=True
    )

    _titulos_ticker = set()
    _ticker_final = []
    for n in noticias_ticker:
        chave = normalizar_titulo_dedupe(n.get("titulo", ""))
        if not chave or chave in _titulos_ticker:
            continue
        _titulos_ticker.add(chave)
        _ticker_final.append(n)
        if len(_ticker_final) >= 18:
            break

    if _ticker_final:
        itens_ticker = []

        for n in _ticker_final:
            titulo_ticker = esc_html(str(n.get("titulo") or "Sem título").strip())
            fonte_ticker = esc_html(nome_fonte_exibicao(n.get("veiculo")))
            link_ticker = esc_html(str(n.get("link") or ""))
            bolinha_ticker = esc_html(n.get("bolinha", "🔵"))

            itens_ticker.append(
                f"<a href=\"{link_ticker}\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"radar-ticker-item\">"
                f"<span class=\"radar-ticker-dot\">{bolinha_ticker}</span>"
                f"<span class=\"radar-ticker-title\">{titulo_ticker}</span>"
                f"<span class=\"radar-ticker-source\">{fonte_ticker}</span>"
                f"</a>"
            )

        itens_html = "".join(itens_ticker)

        st.markdown(
            f"""
            <style>
                .radar-ticker-wrap {{
                    width: 100%;
                    overflow: hidden;
                    border: 1px solid rgba(100,116,139,.16);
                    border-radius: 10px;
                    background: #27324a;
                    display: flex;
                    align-items: center;
                    margin: 12px 0 16px 0;
                    height: 46px;
                    box-sizing: border-box;
                }}
                .radar-ticker-label {{
                    flex: 0 0 auto;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    padding: 0 16px;
                    background: #1d2638;
                    color: #fff;
                    font-size: 13px;
                    font-weight: 800;
                    z-index: 3;
                    box-shadow: 5px 0 12px rgba(0,0,0,.12);
                }}
                .radar-ticker-window {{
                    overflow: hidden;
                    flex: 1;
                    height: 100%;
                    display: flex;
                    align-items: center;
                }}
                .radar-ticker-track {{
                    display: flex;
                    align-items: center;
                    width: max-content;
                    animation: radarTickerMove 145s linear infinite;
                    will-change: transform;
                }}
                .radar-ticker-item {{
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    color: #fff !important;
                    text-decoration: none !important;
                    white-space: nowrap;
                    padding: 0 24px;
                    font-size: 14px;
                    line-height: 1;
                }}
                .radar-ticker-item:hover .radar-ticker-title {{
                    text-decoration: underline !important;
                }}
                .radar-ticker-dot {{ font-size: 11px; }}
                .radar-ticker-title {{ font-weight: 700; }}
                .radar-ticker-source {{
                    opacity: .68;
                    font-size: 12px;
                    font-weight: 600;
                }}
                @keyframes radarTickerMove {{
                    from {{ transform: translateX(0); }}
                    to {{ transform: translateX(-50%); }}
                }}
                .radar-ticker-wrap:hover .radar-ticker-track {{
                    animation-play-state: paused;
                }}
            </style>
            <div class="radar-ticker-wrap">
                <div class="radar-ticker-label">📰 ÚLTIMAS NOS PARTAIS DE MG</div>
                <div class="radar-ticker-window">
                    <div class="radar-ticker-track">
                        {itens_html}{itens_html}
                    </div>
                </div>
            </div>
            """,
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
                "🔴 Atenção",
                len(atencao)
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
                ["Todas", "🔴 Atenção", "🟠 Alta", "🟡 Média", "⚪ Menção"]
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
            "🔴 Atenção": "🔴",
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
        atencao_pdf = [
            n for n in noticias_clipping
            if n["score"] >= 85
        ]
        altas_pdf = [
            n for n in noticias_clipping
            if 65 <= n["score"] < 85
        ]

        if atencao_pdf or altas_pdf:
            story.append(Paragraph("DESTAQUES", secao))

            for noticia in (atencao_pdf[:5] + altas_pdf[:5]):
                story.append(
                    Paragraph(
                        f"{noticia['bolinha']} {noticia['titulo']}",
                        manchete,
                    )
                )
                story.append(
                    Paragraph(
                        f"<b>{nome_fonte_exibicao(noticia['veiculo'])}</b>",
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
                    f"{nome_fonte_exibicao(noticia['veiculo'])} • {data}",
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
    qtd_atencao_filtradas = sum(
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
        f'<div class="news-count-caption">{len(filtradas)} notícias encontradas ({qtd_atencao_filtradas} atenção, {qtd_altas_filtradas} altas)</div>',
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

                    meta = f"📰 {nome_fonte_exibicao(noticia['veiculo'])}"

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
        "As notícias são classificadas automaticamente com base em relevância para o TCE-MG.Uso exclusivo do Gabinete."
    )

with aba_redes:
    st.markdown(
        """
        <div style="
            background:rgba(100,116,139,.07);
            border:1px solid rgba(100,116,139,.12);
            border-radius:12px;
            padding:14px 16px;
            margin-bottom:14px;
        ">
            <div style="
                font-size:20px;
                font-weight:800;
                color:#27324a;
                margin-bottom:3px;
            ">
                𝕏 Radar de Redes Sociais
            </div>
            <div style="
                font-size:13px;
                color:#667085;
            ">
                Menções relacionadas ao TCE-MG nos últimos 3 dias.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    x_resultado = buscar_posts_x_ultimos_3_dias()

    if not x_resultado.get("ok"):
        st.info(
            "Para ativar o monitoramento do X, configure "
            "`X_BEARER_TOKEN` nos Secrets do Streamlit."
        )
        st.caption(
            "A aba já está pronta para a API oficial do X; "
            "sem o Bearer Token ela não faz nenhuma busca externa."
        )
    else:
        posts_x = x_resultado.get("posts", [])
        contador_x, contador_nomes_x = analisar_posts_x(posts_x)

        # ========================================================
        # PAINÉIS TRANSLÚCIDOS — ÚLTIMOS 3 DIAS
        # ========================================================

        x1, x2 = st.columns(2, gap="medium")

        with x1:
            st.markdown(
                """
                <div style="
                    background:rgba(100,116,139,.07);
                    border:1px solid rgba(100,116,139,.12);
                    border-radius:12px;
                    padding:12px 14px;
                    margin-bottom:8px;
                    font-size:17px;
                    font-weight:800;
                    color:#27324a;
                ">
                    🔥 Maiores menções
                    <span style="
                        font-size:12px;
                        font-weight:500;
                        color:#98a2b3;
                    "> · últimos 3 dias</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if contador_x:
                linhas = ""
                for termo, quantidade in contador_x.most_common(10):
                    linhas += f"""
                    <div style="
                        display:flex;
                        justify-content:space-between;
                        padding:7px 3px;
                        color:#27324a;
                        font-size:14px;
                    ">
                        <span>{esc_html(termo)}</span>
                        <strong>{quantidade}</strong>
                    </div>
                    """

                st.markdown(
                    f"""
                    <div style="
                        background:rgba(255,255,255,.32);
                        border-radius:9px;
                        padding:4px 8px;
                    ">
                        {linhas}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.caption("Nenhum termo identificado.")

        with x2:
            st.markdown(
                """
                <div style="
                    background:rgba(100,116,139,.07);
                    border:1px solid rgba(100,116,139,.12);
                    border-radius:12px;
                    padding:12px 14px;
                    margin-bottom:8px;
                    font-size:17px;
                    font-weight:800;
                    color:#27324a;
                ">
                    👥 Nomes mais mencionados
                    <span style="
                        font-size:12px;
                        font-weight:500;
                        color:#98a2b3;
                    "> · últimos 3 dias</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if contador_nomes_x:
                linhas = ""
                for nome, quantidade in contador_nomes_x.most_common(10):
                    linhas += f"""
                    <div style="
                        display:flex;
                        justify-content:space-between;
                        padding:7px 3px;
                        color:#27324a;
                        font-size:14px;
                    ">
                        <span>{esc_html(nome)}</span>
                        <strong>{quantidade}</strong>
                    </div>
                    """

                st.markdown(
                    f"""
                    <div style="
                        background:rgba(255,255,255,.32);
                        border-radius:9px;
                        padding:4px 8px;
                    ">
                        {linhas}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.caption("Nenhum nome monitorado identificado.")

        st.markdown("### 𝕏 Últimas 20 menções")

        if not posts_x:
            st.info(
                "Nenhuma publicação relacionada ao TCE-MG foi encontrada "
                "nos últimos 3 dias."
            )
        else:
            for i, post in enumerate(posts_x[:20]):
                data_x = post.get("data", "")
                if data_x:
                    try:
                        dt_x = datetime.fromisoformat(
                            data_x.replace("Z", "+00:00")
                        ).astimezone(FUSO_BRASIL)
                        data_x = dt_x.strftime("%d/%m/%Y %H:%M")
                    except Exception:
                        pass

                metricas = post.get("metricas", {})
                likes = metricas.get("like_count", 0)
                reposts = metricas.get("retweet_count", 0)
                replies = metricas.get("reply_count", 0)

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="
                            font-size:14px;
                            color:#667085;
                            margin-bottom:6px;
                        ">
                            <strong style="color:#27324a;">
                                @{esc_html(post.get("username") or "usuario")}
                            </strong>
                            &nbsp; · &nbsp;
                            {esc_html(data_x)}
                        </div>
                        <div style="
                            font-size:15px;
                            line-height:1.45;
                            color:#27324a;
                        ">
                            {esc_html(post.get("texto", ""))}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    c1, c2 = st.columns([1, 5])

                    with c1:
                        st.link_button(
                            "Ver no X ↗",
                            post["link"],
                            key=f"x_post_{i}_{post['id']}"
                        )

                    with c2:
                        st.caption(
                            f"❤️ {likes}   •   🔁 {reposts}   •   💬 {replies}"
                        )

        st.caption(
            "Monitoramento baseado na API oficial do X. "
            "A busca considera publicações dos últimos 3 dias e "
            "é limitada aos termos de conexão definidos pelo Radar."
        )

