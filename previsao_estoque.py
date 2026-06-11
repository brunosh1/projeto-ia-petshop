# ============================================================
# PREVISÃO DE ESTOQUE PARA COMÉRCIO LOCAL (Pet Shop - Itaquera)
# Tema 3 - Sistemas de Aprendizado de Máquina
# Projeto de Extensão - IA para Devs
# ------------------------------------------------------------
# O que este script faz:
#   1) Lê a base de dados (star schema) em Excel
#   2) Junta a tabela de fatos (vendas) com as dimensões
#   3) Agrega a demanda por mês e por categoria/produto
#   4) Cria features simples (mês, lags, média móvel)
#   5) Treina um modelo de Machine Learning (RandomForest)
#   6) Avalia o modelo (MAE, RMSE)
#   7) Prevê a demanda do próximo mês (sugestão de estoque)
#   8) Gera gráficos para o relatório
# ============================================================

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ------------------------------------------------------------
# CONFIGURAÇÃO: ajuste o nome do arquivo se necessário
# ------------------------------------------------------------
ARQUIVO = "modelo_star_schema_vendas_petshop (1).xlsx"

# ============================================================
# 1) LEITURA DA BASE DE DADOS (STAR SCHEMA)
# ============================================================
print("== 1) Lendo a base de dados...")

fato = pd.read_excel(ARQUIVO, sheet_name="Fato_Vendas")
dim_produtos = pd.read_excel(ARQUIVO, sheet_name="Dim_Produtos")

# Remove linhas totalmente vazias que possam existir nas abas
fato = fato.dropna(subset=["ID_Produto_SKU", "Data_Venda", "Quantidade"])
dim_produtos = dim_produtos.dropna(subset=["ID_Produto_SKU"])

# Limpeza básica de tipos (os IDs vieram como float, ex.: 9807.0)
fato["ID_Produto_SKU"] = fato["ID_Produto_SKU"].astype("Int64")
dim_produtos["ID_Produto_SKU"] = dim_produtos["ID_Produto_SKU"].astype("Int64")
fato["Data_Venda"] = pd.to_datetime(fato["Data_Venda"])
fato["Quantidade"] = fato["Quantidade"].astype(float)

# ============================================================
# 2) JUNÇÃO FATO + DIMENSÃO (modelo estrela)
# ============================================================
print("== 2) Juntando tabela de fatos com a dimensão de produtos...")

df = fato.merge(
    dim_produtos[["ID_Produto_SKU", "Descricao", "Categoria"]],
    on="ID_Produto_SKU",
    how="left",
)

# Garante que só ficam vendas com categoria válida
df = df.dropna(subset=["Categoria"])

# ============================================================
# 3) AGREGAÇÃO DA DEMANDA POR MÊS E CATEGORIA
#    (poderia ser por produto, mas por categoria há mais
#     histórico, o que ajuda um modelo simples a aprender)
# ============================================================
print("== 3) Agregando a demanda mensal por categoria...")

df["AnoMes"] = df["Data_Venda"].dt.to_period("M").dt.to_timestamp()

demanda = (
    df.groupby(["Categoria", "AnoMes"], as_index=False)["Quantidade"]
    .sum()
    .rename(columns={"Quantidade": "Demanda"})
    .sort_values(["Categoria", "AnoMes"])
    .reset_index(drop=True)
)

print("\nDemanda mensal agregada (amostra):")
print(demanda.head(12))

# ============================================================
# 4) ENGENHARIA DE FEATURES
#    Variáveis que ajudam o modelo a prever:
#       - mês do ano (sazonalidade)
#       - índice temporal (tendência)
#       - lag 1 (demanda do mês anterior)
#       - média móvel de 3 meses
# ------------------------------------------------------------
#  >>> CORREÇÃO DO ERRO <<<
#  Antes usávamos groupby(...).apply(criar_features), o que
#  transformava "Categoria" em ÍNDICE e quebrava o get_dummies.
#  Agora usamos groupby + transform/shift, que MANTÉM a coluna
#  "Categoria" no DataFrame. Assim o erro KeyError não acontece.
# ============================================================
print("== 4) Criando features para o modelo...")

# Ordena para os cálculos temporais ficarem corretos
demanda = demanda.sort_values(["Categoria", "AnoMes"]).reset_index(drop=True)

# Features de calendário e tendência
demanda["mes"] = demanda["AnoMes"].dt.month
demanda["indice_tempo"] = demanda.groupby("Categoria").cumcount()

# Lag 1 (demanda do mês anterior) e média móvel de 3 meses
demanda["lag_1"] = demanda.groupby("Categoria")["Demanda"].shift(1)
demanda["media_movel_3"] = (
    demanda.groupby("Categoria")["Demanda"]
    .transform(lambda s: s.rolling(3).mean())
    .groupby(demanda["Categoria"]).shift(0)  # mantém alinhado por categoria
)
# A média móvel deve usar apenas dados passados -> desloca 1 mês
demanda["media_movel_3"] = demanda.groupby("Categoria")["media_movel_3"].shift(1)

# Garante que "Categoria" é coluna (segurança extra contra KeyError)
if "Categoria" not in demanda.columns:
    demanda = demanda.reset_index()

# Codifica a categoria em número (one-hot)
demanda = pd.get_dummies(demanda, columns=["Categoria"], prefix="cat")

# Remove linhas iniciais sem histórico (lag/média móvel vazios)
dados_modelo = demanda.dropna().reset_index(drop=True)

features = [c for c in dados_modelo.columns
            if c not in ["AnoMes", "Demanda"]]
X = dados_modelo[features]
y = dados_modelo["Demanda"]

# ============================================================
# 5) TREINAMENTO DO MODELO DE MACHINE LEARNING
# ============================================================
print("== 5) Treinando o modelo (RandomForestRegressor)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

modelo = RandomForestRegressor(n_estimators=200, random_state=42)
modelo.fit(X_train, y_train)

# ============================================================
# 6) AVALIAÇÃO DO MODELO
# ============================================================
print("== 6) Avaliando o modelo...")

y_pred = modelo.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"\n   MAE  (erro médio absoluto):  {mae:.2f} unidades")
print(f"   RMSE (raiz do erro quadrático): {rmse:.2f} unidades")
print("   -> Em média, a previsão erra cerca de "
      f"{mae:.1f} unidades por categoria/mês.")

# ============================================================
# 7) PREVISÃO DO PRÓXIMO MÊS (sugestão de estoque)
# ============================================================
print("\n== 7) Prevendo a demanda do PRÓXIMO mês por categoria...")

previsoes = []
for categoria in df["Categoria"].dropna().unique():
    # Histórico mensal somado dessa categoria
    hist = (
        df[df["Categoria"] == categoria]
        .groupby("AnoMes")["Quantidade"].sum()
        .sort_index()
    )

    if len(hist) == 0:
        continue

    # Reconstrói as features para o próximo mês
    ultimo_mes = hist.index.max()
    proximo_mes = ultimo_mes + pd.offsets.MonthBegin(1)

    lag_1 = hist.iloc[-1]
    media_movel_3 = hist.iloc[-3:].mean()
    indice_tempo = len(hist)
    mes = proximo_mes.month

    linha = {
        "mes": mes,
        "indice_tempo": indice_tempo,
        "lag_1": lag_1,
        "media_movel_3": media_movel_3,
        "cat_CACHORRO": 1 if categoria == "CACHORRO" else 0,
        "cat_GATO": 1 if categoria == "GATO" else 0,
    }
    # Garante exatamente as mesmas colunas usadas no treino
    linha_df = pd.DataFrame([linha]).reindex(columns=features, fill_value=0)
    pred = modelo.predict(linha_df)[0]

    previsoes.append({
        "Categoria": categoria,
        "Mes_Previsto": proximo_mes.strftime("%Y-%m"),
        "Demanda_Prevista": round(pred),
        "Sugestao_Estoque_+10%": int(np.ceil(pred * 1.10)),
    })

resultado = pd.DataFrame(previsoes)
print("\n>>> SUGESTÃO DE ESTOQUE PARA O PRÓXIMO MÊS <<<")
print(resultado.to_string(index=False))

resultado.to_csv("previsao_estoque_proximo_mes.csv", index=False)
print("\n(arquivo 'previsao_estoque_proximo_mes.csv' salvo)")

# ============================================================
# 8) GRÁFICOS PARA O RELATÓRIO
# ============================================================
print("\n== 8) Gerando gráficos...")

# Gráfico 1: histórico de demanda por categoria
plt.figure(figsize=(10, 5))
for categoria in df["Categoria"].dropna().unique():
    serie = (df[df["Categoria"] == categoria]
             .groupby("AnoMes")["Quantidade"].sum())
    plt.plot(serie.index, serie.values, marker="o", label=categoria)
plt.title("Histórico de Demanda Mensal por Categoria")
plt.xlabel("Mês")
plt.ylabel("Unidades vendidas")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("grafico_historico_demanda.png", dpi=120)

# Gráfico 2: valores reais x previstos (qualidade do modelo)
plt.figure(figsize=(6, 6))
plt.scatter(y_test, y_pred)
lim = [0, max(y_test.max(), y_pred.max()) + 5]
plt.plot(lim, lim, "--", color="red")
plt.title("Valores Reais x Previstos")
plt.xlabel("Demanda real")
plt.ylabel("Demanda prevista")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("grafico_real_x_previsto.png", dpi=120)

print("Gráficos salvos: grafico_historico_demanda.png e grafico_real_x_previsto.png")
print("\n== FIM ==")
