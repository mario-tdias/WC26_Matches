import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÃO ---
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard"
ARQUIVO_BASE = "copa_base.html"
ARQUIVO_JSON = "jogos.json"
ARQUIVO_HTML = "index.html"
FUSO = timezone(timedelta(hours=-3))

NOMES_PT = {
    "Mexico": "México",
    "South Africa": "África do Sul",
    "Brazil": "Brasil",
    "Argentina": "Argentina",
    "Germany": "Alemanha",
    "France": "França",
    "Spain": "Espanha",
    "Portugal": "Portugal",
    "England": "Inglaterra",
    "United States": "Estados Unidos",
    "USA": "Estados Unidos",
    "Canada": "Canadá",
    "Japan": "Japão",
    "South Korea": "Coreia do Sul",
    "Netherlands": "Holanda",
    "Belgium": "Bélgica",
    "Croatia": "Croácia",
    "Uruguay": "Uruguai",
    "Colombia": "Colômbia",
    "Ecuador": "Equador",
    "Chile": "Chile",
    "Peru": "Peru",
    "Paraguay": "Paraguai",
    "Switzerland": "Suíça",
    "Poland": "Polônia",
    "Serbia": "Sérvia",
    "Denmark": "Dinamarca",
    "Sweden": "Suécia",
    "Morocco": "Marrocos",
    "Senegal": "Senegal",
    "Nigeria": "Nigéria",
    "Cameroon": "Camarões",
    "Ghana": "Gana",
    "Tunisia": "Tunísia",
    "Saudi Arabia": "Arábia Saudita",
    "Iran": "Irã",
    "Australia": "Austrália",
    "Costa Rica": "Costa Rica",
    "Panama": "Panamá",
    "Jamaica": "Jamaica",
    "Haiti": "Haiti",
    "Qatar": "Catar",
    "Wales": "País de Gales",
    "Scotland": "Escócia",
    "Italy": "Itália",
    "Ukraine": "Ucrânia",
    "Austria": "Áustria",
    "Turkey": "Turquia",
    "Czech Republic": "República Tcheca",
    "Czechia": "República Tcheca",
    "Hungary": "Hungria",
    "Romania": "Romênia",
    "Slovakia": "Eslováquia",
    "Slovenia": "Eslovênia",
    "Algeria": "Argélia",
    "Egypt": "Egito",
    "Ivory Coast": "Costa do Marfim",
    "New Zealand": "Nova Zelândia",
    "China": "China",
    "Iraq": "Iraque",
    "Jordan": "Jordânia",
    "Uzbekistan": "Uzbequistão",
    "Bolivia": "Bolívia",
    "Venezuela": "Venezuela",
    "Honduras": "Honduras",
    "El Salvador": "El Salvador",
    "Guatemala": "Guatemala",
    "Curaçao": "Curaçao",
    "Trinidad and Tobago": "Trinidad e Tobago",
    "Republic of Ireland": "Irlanda",
    "Northern Ireland": "Irlanda do Norte",
    "Greece": "Grécia",
    "Norway": "Noruega",
    "Finland": "Finlândia",
    "Iceland": "Islândia",
    "Bosnia and Herzegovina": "Bósnia e Herzegovina",
    "North Macedonia": "Macedônia do Norte",
    "Montenegro": "Montenegro",
    "Albania": "Albânia",
    "Georgia": "Geórgia",
    "Armenia": "Armênia",
    "Israel": "Israel",
    "Palestine": "Palestina",
    "Oman": "Omã",
    "UAE": "Emirados Árabes",
    "United Arab Emirates": "Emirados Árabes",
    "Kuwait": "Kuwait",
    "Bahrain": "Bahrein",
    "Thailand": "Tailândia",
    "Vietnam": "Vietnã",
    "Indonesia": "Indonésia",
    "India": "Índia",
    "Cape Verde": "Cabo Verde",
    "DR Congo": "RD Congo",
    "Zambia": "Zâmbia",
    "Angola": "Angola",
    "Mozambique": "Moçambique",
    "Kenya": "Quênia",
    "Uganda": "Uganda",
    "Benin": "Benin",
    "Burkina Faso": "Burkina Faso",
    "Mali": "Mali",
    "Guinea": "Guiné",
    "Togo": "Togo",
    "Gabon": "Gabão",
    "Congo": "Congo",
    "Equatorial Guinea": "Guiné Equatorial",
    "Libya": "Líbia",
    "Sudan": "Sudão",
    "Zimbabwe": "Zimbábue",
    "Namibia": "Namíbia",
    "Botswana": "Botsuana",
    "Madagascar": "Madagascar",
    "Mauritania": "Mauritânia",
    "Gambia": "Gâmbia",
    "Sierra Leone": "Serra Leoa",
    "Liberia": "Libéria",
    "Ethiopia": "Etiópia",
    "Rwanda": "Ruanda",
    "Tanzania": "Tanzânia",
    "Malawi": "Malawi",
    "Lesotho": "Lesoto",
    "Eswatini": "Essuatíni",
    "Comoros": "Comores",
    "Niger": "Níger",
    "Chad": "Chade",
    "Central African Republic": "República Centro-Africana",
    "South Sudan": "Sudão do Sul",
    "Somalia": "Somália",
    "Djibouti": "Djibuti",
    "Eritrea": "Eritreia",
    "Burundi": "Burundi",
    "Mauritius": "Maurício",
    "Seychelles": "Seicheles",
    "Korea Republic": "Coreia do Sul",
    "Korea DPR": "Coreia do Norte",
}


def traduzir_nome(nome: str) -> str:
    return NOMES_PT.get(nome, nome)


def status_em_portugues(status: dict) -> dict:
    state = status.get("type", {}).get("state", "pre")
    descricao = status.get("type", {}).get("description", "")
    relogio = status.get("displayClock", "")
    detalhe = status.get("type", {}).get("shortDetail", "")

    if state == "in":
        if "half" in descricao.lower() and "full" not in descricao.lower():
            texto = "Intervalo"
        else:
            texto = "AO VIVO"
    elif state == "post":
        texto = "Encerrado"
    else:
        texto = "Aguardando"

    return {
        "estado": state,
        "texto": texto,
        "relogio": relogio,
        "detalhe": detalhe,
    }


def buscar_jogos() -> list:
    agora_sp = datetime.now(FUSO)
    data_param = agora_sp.strftime("%Y%m%d")
    url = f"{ESPN_URL}?dates={data_param}"

    req = urllib.request.Request(url, headers={"User-Agent": "painel-copa-2026/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        dados = json.loads(response.read())

    jogos = []
    for evento in dados.get("events", []):
        competicao = evento.get("competitions", [{}])[0]
        status = competicao.get("status", {})
        status_pt = status_em_portugues(status)

        casa = None
        visitante = None
        for competidor in competicao.get("competitors", []):
            time = competidor.get("team", {})
            info = {
                "nome": traduzir_nome(time.get("displayName", "")),
                "sigla": time.get("abbreviation", ""),
                "logo": time.get("logo", ""),
                "gols": competidor.get("score", "-"),
            }
            if competidor.get("homeAway") == "home":
                casa = info
            else:
                visitante = info

        if not casa or not visitante:
            continue

        data_utc = datetime.fromisoformat(
            competicao.get("date", evento.get("date", "")).replace("Z", "+00:00")
        )
        data_local = data_utc.astimezone(FUSO)

        venue = competicao.get("venue", {})
        endereco = venue.get("address", {})

        jogos.append({
            "id": evento.get("id"),
            "hora": data_local.strftime("%H:%M"),
            "casa": casa,
            "visitante": visitante,
            "status": status_pt,
            "estadio": venue.get("fullName", ""),
            "cidade": endereco.get("city", ""),
            "fase": evento.get("season", {}).get("slug", "").replace("-", " ").title(),
        })

    jogos.sort(key=lambda j: j["hora"])
    return jogos


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_json = os.path.join(script_dir, ARQUIVO_JSON)
    caminho_base = os.path.join(script_dir, ARQUIVO_BASE)
    caminho_html = os.path.join(script_dir, ARQUIVO_HTML)

    jogos = buscar_jogos()
    agora = datetime.now(FUSO)

    payload = {
        "atualizado_em": agora.isoformat(),
        "data": agora.strftime("%Y-%m-%d"),
        "data_formatada": agora.strftime("%d/%m/%Y"),
        "total": len(jogos),
        "jogos": jogos,
    }

    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    with open(caminho_base, "r", encoding="utf-8") as f:
        html_base = f.read()

    json_embutido = json.dumps(payload, ensure_ascii=False)
    html_final = html_base.replace("{{JOGOS_JSON}}", json_embutido)

    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html_final)

    print(f"Sucesso! {len(jogos)} jogo(s) gerados em {ARQUIVO_JSON} e {ARQUIVO_HTML}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        exit(1)
