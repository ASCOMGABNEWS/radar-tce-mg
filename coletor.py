import feedparser
from datetime import datetime

FONTES = {
    "Google News - TCE-MG": "https://news.google.com/rss/search?q=%22TCE-MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Google News - TCE MG": "https://news.google.com/rss/search?q=%22TCE%20MG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Google News - TCEMG": "https://news.google.com/rss/search?q=%22TCEMG%22&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "Google News - Tribunal de Contas MG": "https://news.google.com/rss/search?q=%22Tribunal%20de%20Contas%22%20%22Minas%20Gerais%22&hl=pt-BR&gl=BR&ceid=BR:pt-419",
}

def coletar_noticias():
    noticias = []

    for fonte, url in FONTES.items():
        feed = feedparser.parse(url)

        for item in feed.entries:
            noticias.append({
                "titulo": item.get("title", ""),
                "link": item.get("link", ""),
                "fonte": fonte,
                "data": item.get("published", datetime.now().isoformat()),
            })

    return noticias


if __name__ == "__main__":
    noticias = coletar_noticias()

    print(f"Foram encontradas {len(noticias)} notícias.")

    for noticia in noticias[:20]:
        print("\n" + noticia["titulo"])
        print(noticia["link"])
