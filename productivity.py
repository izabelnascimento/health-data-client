import requests
import pandas as pd
import matplotlib.pyplot as plt

# URL do endpoint
url = "http://localhost:8080/api/dea/indicators/first-semester?year=2023"

# Fazendo a requisição GET
response = requests.get(url)
response.raise_for_status()  # lança erro se não for 200

# Converte JSON em DataFrame
data = response.json()
df = pd.DataFrame(data)

# Exibe primeiras linhas no terminal (debug)
print(df.head())

# ------------------------------
# Gráfico de exemplo:
#   - eixo X: nome da cidade
#   - eixo Y: produtividade
# ------------------------------
plt.figure(figsize=(14, 7))
plt.bar(df["cityName"], df["productivity"], color="steelblue")

plt.xticks(rotation=90)  # gira os nomes das cidades
plt.xlabel("Cidades")
plt.ylabel("Produtividade")
plt.title("Produtividade por Cidade - 1º Semestre 2023")

plt.tight_layout()
plt.savefig("indicadores_produtividade.png", dpi=300)

print("✅ Gráfico salvo em indicadores_produtividade.png")
