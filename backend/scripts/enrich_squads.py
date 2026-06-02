"""Aplica enriquecimiento (fifa_rating + market_value_eur) a squads.json por nombre.

- market_value_eur: valor Transfermarkt (exacto, en EUR).
- fifa_rating: overall EA SPORTS FC 26 (aprox. para algunos; exacto donde se confirmo).

Editar el dict ENRICH y correr:
    python scripts/enrich_squads.py
Reporta jugadores no encontrados (por si hay diferencias de tilde/nombre).
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "app" / "data"

M = 1_000_000
K = 1_000

# team_id -> { player_name: (fifa_rating|None, market_value_eur|None) }
ENRICH: dict[str, dict[str, tuple]] = {
    "ARG": {
        "Gerónimo Rulli": (79, 6 * M),
        "Juan Musso": (78, 3 * M),
        "Emiliano Martínez": (85, 15 * M),
        "Leonardo Balerdi": (80, 18 * M),
        "Nicolás Tagliafico": (78, 4 * M),
        "Gonzalo Montiel": (78, int(4.5 * M)),
        "Lisandro Martínez": (82, 40 * M),
        "Cristian Romero": (84, 50 * M),
        "Nicolás Otamendi": (79, 1 * M),
        "Facundo Medina": (79, 18 * M),
        "Nahuel Molina": (80, 15 * M),
        "Leandro Paredes": (80, 5 * M),
        "Rodrigo De Paul": (82, 15 * M),
        "Valentín Barco": (75, 40 * M),
        "Giovani Lo Celso": (81, 10 * M),
        "Exequiel Palacios": (80, 25 * M),
        "Alexis Mac Allister": (85, 80 * M),
        "Enzo Fernández": (84, 90 * M),
        "Julián Álvarez": (86, 90 * M),
        "Lionel Messi": (88, 15 * M),
        "Nicolás González": (81, 24 * M),
        "Thiago Almada": (82, 20 * M),
        "Giuliano Simeone": (78, 40 * M),
        "Nicolás Paz": (79, 80 * M),
        "José Manuel López": (75, 25 * M),
        "Lautaro Martínez": (87, 85 * M),
    },
    "FRA": {
        "Mike Maignan": (87, 20 * M),
        "Robin Risser": (70, 30 * M),
        "Brice Samba": (82, 7 * M),
        "Lucas Digne": (79, 8 * M),
        "Malo Gusto": (79, 35 * M),
        "Lucas Hernández": (82, 18 * M),
        "Theo Hernández": (84, 28 * M),
        "Ibrahima Konaté": (85, 50 * M),
        "Jules Koundé": (84, 65 * M),
        "Maxence Lacroix": (80, 40 * M),
        "William Saliba": (86, 90 * M),
        "Dayot Upamecano": (85, 70 * M),
        "N'Golo Kanté": (84, 4 * M),
        "Manu Koné": (81, 50 * M),
        "Adrien Rabiot": (84, 18 * M),
        "Aurélien Tchouaméni": (85, 75 * M),
        "Warren Zaïre-Emery": (81, 80 * M),
        "Rayan Cherki": (82, 65 * M),
        "Maghnes Akliouche": (79, 50 * M),
        "Bradley Barcola": (82, 70 * M),
        "Ousmane Dembélé": (89, 100 * M),
        "Désiré Doué": (82, 120 * M),
        "Jean-Philippe Mateta": (81, 35 * M),
        "Kylian Mbappé": (91, 200 * M),
        "Michael Olise": (84, 150 * M),
        "Marcus Thuram": (84, 50 * M),
    },
    "ESP": {
        "Unai Simón": (85, 25 * M),
        "David Raya": (85, 35 * M),
        "Joan García": (82, 40 * M),
        "Marcos Llorente": (82, 22 * M),
        "Pedro Porro": (83, 40 * M),
        "Eric García": (80, 35 * M),
        "Marc Pubill": (76, 28 * M),
        "Aymeric Laporte": (83, 9 * M),
        "Pau Cubarsí": (82, 80 * M),
        "Marc Cucurella": (83, 50 * M),
        "Alejandro Grimaldo": (84, 20 * M),
        "Pedri": (89, 150 * M),
        "Fabián Ruiz": (85, 30 * M),
        "Martín Zubimendi": (85, 80 * M),
        "Gavi": (84, 30 * M),
        "Rodri": (90, 65 * M),
        "Alex Baena": (82, 45 * M),
        "Mikel Merino": (84, 30 * M),
        "Mikel Oyarzabal": (84, 25 * M),
        "Dani Olmo": (85, 60 * M),
        "Nico Williams": (85, 50 * M),
        "Yéremy Pino": (80, 35 * M),
        "Ferran Torres": (83, 50 * M),
        "Borja Iglesias": (78, 3 * M),
        "Víctor Muñoz": (72, 20 * M),
        "Lamine Yamal": (89, 200 * M),
    },
    "BRA": {
        "Alisson": (88, 17 * M),
        "Ederson": (86, 10 * M),
        "Weverton": (78, 700 * K),
        "Alex Sandro": (79, 1 * M),
        "Bremer": (84, 35 * M),
        "Danilo": (80, 2 * M),
        "Douglas Santos": (80, int(7.5 * M)),
        "Gabriel Magalhaes": (84, 75 * M),
        "Ibañez": (79, 17 * M),
        "Léo Pereira": (79, 12 * M),
        "Marquinhos": (85, 28 * M),
        "Wesley": (79, 40 * M),
        "Bruno Guimaraes": (85, 75 * M),
        "Casemiro": (84, 8 * M),
        "Danilo Santos": (76, 32 * M),
        "Fabinho": (82, 13 * M),
        "Lucas Paquetá": (83, 32 * M),
        "Endrick": (79, 40 * M),
        "Gabriel Martinelli": (82, 45 * M),
        "Igor Thiago": (78, 50 * M),
        "Luiz Henrique": (80, 24 * M),
        "Matheus Cunha": (83, 70 * M),
        "Neymar": (84, 8 * M),
        "Raphinha": (87, 80 * M),
        "Rayan": (75, 40 * M),
        "Vinícius Jr": (90, 150 * M),
    },
    "ENG": {
        "Dean Henderson": (80, 28 * M),
        "Jordan Pickford": (85, 15 * M),
        "James Trafford": (78, 25 * M),
        "Dan Burn": (79, 5 * M),
        "Marc Guéhi": (83, 65 * M),
        "Reece James": (83, 60 * M),
        "Ezri Konsa": (81, 40 * M),
        "Tino Livramento": (79, 40 * M),
        "Nico O'Reilly": (75, 50 * M),
        "Jarell Quansah": (78, 45 * M),
        "Djed Spence": (78, 30 * M),
        "John Stones": (84, 15 * M),
        "Elliot Anderson": (79, 60 * M),
        "Jude Bellingham": (90, 140 * M),
        "Eberechi Eze": (84, 60 * M),
        "Jordan Henderson": (79, 2 * M),
        "Kobbie Mainoo": (80, 50 * M),
        "Declan Rice": (89, 120 * M),
        "Morgan Rogers": (81, 80 * M),
        "Anthony Gordon": (83, 60 * M),
        "Harry Kane": (90, 60 * M),
        "Noni Madueke": (80, 50 * M),
        "Marcus Rashford": (84, 40 * M),
        "Bukayo Saka": (89, 120 * M),
        "Ivan Toney": (81, 20 * M),
        "Ollie Watkins": (84, 30 * M),
    },
    "POR": {
        "Diogo Costa": (85, 40 * M),
        "José Sá": (80, 5 * M),
        "Rui Silva": (79, 7 * M),
        "Diogo Dalot": (83, 30 * M),
        "Matheus Nunes": (82, 45 * M),
        "Nélson Semedo": (80, 6 * M),
        "Joao Cancelo": (84, 9 * M),
        "Nuno Mendes": (85, 80 * M),
        "Goncalo Inácio": (82, 40 * M),
        "Renato Veiga": (80, 25 * M),
        "Rúben Dias": (88, 60 * M),
        "Tomás Araújo": (79, 30 * M),
        "Rúben Neves": (83, 25 * M),
        "Samú Costa": (79, 15 * M),
        "Joao Neves": (84, 140 * M),
        "Vitinha": (87, 140 * M),
        "Bruno Fernandes": (88, 40 * M),
        "Bernardo Silva": (87, 27 * M),
        "João Félix": (82, 25 * M),
        "Francisco Trincao": (80, 40 * M),
        "Francisco Conceicao": (81, 30 * M),
        "Pedro Neto": (83, 60 * M),
        "Rafael Leao": (86, 50 * M),
        "Goncalo Guedes": (79, 6 * M),
        "Goncalo Ramos": (82, 30 * M),
        "Cristiano Ronaldo": (88, 12 * M),
    },
    "GER": {
        "Oliver Baumann": (80, int(2.5 * M)),
        "Manuel Neuer": (87, 4 * M),
        "Alexander Nübel": (81, 12 * M),
        "Waldemar Anton": (79, 18 * M),
        "Nathaniel Brown": (75, 40 * M),
        "Joshua Kimmich": (87, 35 * M),
        "David Raum": (81, 25 * M),
        "Antonio Rüdiger": (86, 9 * M),
        "Nico Schlotterbeck": (83, 55 * M),
        "Jonathan Tah": (84, 28 * M),
        "Malick Thiaw": (81, 45 * M),
        "Pascal Grob": (80, int(3.5 * M)),
        "Felix Nmecha": (79, 50 * M),
        "Aleksandar Pavlović": (81, 90 * M),
        "Angelo Stiller": (81, 45 * M),
        "Nadiem Amiri": (79, 17 * M),
        "Leon Goretzka": (83, 12 * M),
        "Jamal Musiala": (88, 100 * M),
        "Florian Wirtz": (88, 110 * M),
        "Maximilian Beier": (80, 40 * M),
        "Kai Havertz": (84, 50 * M),
        "Lennart Karl": (74, 60 * M),
        "Jamie Leweling": (78, 40 * M),
        "Leroy Sané": (84, 20 * M),
        "Deniz Undav": (82, 22 * M),
        "Nick Woltemade": (80, 65 * M),
    },
}


def main():
    path = DATA / "squads.json"
    squads = json.loads(path.read_text(encoding="utf-8"))

    total, missing = 0, []
    for tid, players in ENRICH.items():
        team = squads.get(tid)
        if not team:
            print(f"[WARN] equipo {tid} no existe en squads.json")
            continue
        by_name = {p["name"]: p for p in team["players"]}
        for name, (fifa, value) in players.items():
            p = by_name.get(name)
            if not p:
                missing.append(f"{tid}:{name}")
                continue
            if fifa is not None:
                p["fifa_rating"] = fifa
            if value is not None:
                p["market_value_eur"] = value
            total += 1

    path.write_text(json.dumps(squads, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Jugadores enriquecidos: {total}")
    if missing:
        print("NO encontrados (revisar nombre):")
        for m in missing:
            print("  -", m)


if __name__ == "__main__":
    main()
