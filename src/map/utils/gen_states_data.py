import json
import os

DIR = "static/data/geojson/mun"

UF_MAPPING = {
    11: "RO",  # Rondônia
    12: "AC",  # Acre
    13: "AM",  # Amazonas
    14: "RR",  # Roraima
    15: "PA",  # Pará
    16: "AP",  # Amapá
    17: "TO",  # Tocantins
    21: "MA",  # Maranhão
    22: "PI",  # Piauí
    23: "CE",  # Ceará
    24: "RN",  # Rio Grande do Norte
    25: "PB",  # Paraíba
    26: "PE",  # Pernambuco
    27: "AL",  # Alagoas
    28: "SE",  # Sergipe
    29: "BA",  # Bahia
    31: "MG",  # Minas Gerais
    32: "ES",  # Espírito Santo
    33: "RJ",  # Rio de Janeiro
    35: "SP",  # São Paulo
    41: "PR",  # Paraná
    42: "SC",  # Santa Catarina
    43: "RS",  # Rio Grande do Sul
    50: "MS",  # Mato Grosso do Sul
    51: "MT",  # Mato Grosso
    52: "GO",  # Goiás
    53: "DF",  # Distrito Federal
}

files = [os.path.join(DIR, arquivo) for arquivo in os.listdir(DIR)]

states = {}

for f in files:
    with open(f, "r", encoding="utf-8") as json_file:
        uf_code = f.split("-")[1].split(".")[0]
        state = UF_MAPPING[int(uf_code)]
        data = json.load(json_file)
        states[state] = [feature["properties"]["name"] for feature in data["features"]]


with open("states.json", "w", encoding="utf-8") as json_file:
    json.dump(states, json_file, ensure_ascii=False, indent=4)
