# 🐾 Previsão de Estoque para Comércio Local — Tchucoo

Projeto de extensão da disciplina **Inteligência Artificial para Devs**, com foco em **Sistemas de Aprendizado de Máquina (Tema 3)**. O objetivo é ajudar um pequeno comércio do ramo pet a prever a demanda de estoque a partir do seu histórico de vendas, usando um modelo preditivo simples.

## 📌 Sobre o projeto

A loja **Tchucoo Comércio de Acessórios Pet** (acessórios para cães e gatos) fazia a reposição de estoque de forma intuitiva, "no feeling". Isso causava dois problemas: falta de produto em meses de alta procura (venda perdida) e excesso de mercadoria parada (capital de giro travado).

Este projeto resolve essa dor treinando um modelo de Machine Learning com o histórico de vendas e gerando uma **sugestão de compra mensal por categoria de produto**.

## 🧠 Como funciona

| Etapa | O que acontece |
|-------|----------------|
| 1. Leitura | Lê a base de dados (modelo *star schema*) em Excel |
| 2. Junção | Liga a tabela de vendas às dimensões de produtos |
| 3. Agregação | Soma a demanda por mês e por categoria (GATO / CACHORRO) |
| 4. Features | Cria variáveis: mês, tendência, *lag* e média móvel |
| 5. Modelo | Treina um **RandomForestRegressor** (aprendizado supervisionado) |
| 6. Avaliação | Mede o erro com **MAE** e **RMSE** |
| 7. Previsão | Estima a demanda do próximo mês + 10% de margem de segurança |
| 8. Gráficos | Gera imagens para o relatório |

## 🗂️ Estrutura da base de dados (Star Schema)

- **Fato_Vendas** — registros de vendas (data, produto, cliente, quantidade, preços, valor total)
- **Dim_Produtos** — catálogo de produtos (SKU, descrição, categoria, fornecedor)
- **Dim_Clientes** — cadastro de clientes (ID, razão social, CNPJ, cidade, UF)

## 🛠️ Tecnologias utilizadas

- **Python 3**
- **pandas** — manipulação de dados
- **scikit-learn** — modelo de Machine Learning (RandomForest)
- **matplotlib** — geração de gráficos
- **openpyxl** — leitura de arquivos Excel

## ▶️ Como executar

1. Clone este repositório:
   ```bash
   git clone  https://github.com/brunosh1/projeto-ia-petshop.git
   cd projeto-ia-petshop

2. (Opcional) Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1   # Windows

3. Instale as dependências:
   ```bash
   pip install pandas numpy scikit-learn matplotlib openpyxl

4. Execute o programa:
   ```bash
   python previsao_estoque.py


📊 Resultados obtidos
Avaliação do modelo:

MAE (erro médio absoluto): 6,17 unidades
RMSE (raiz do erro quadrático médio): 8,03 unidades
Sugestão de estoque para o próximo mês:

<img width="683" height="119" alt="image" src="https://github.com/user-attachments/assets/689824da-e51a-47ee-b7ee-fbf51766f85a" />

Categoria	Demanda Prevista	Sugestão de Estoque (+10%)
GATO	16	18
CACHORRO	15	17
📁 Arquivos gerados pelo programa
previsao_estoque_proximo_mes.csv — tabela com a previsão de estoque
grafico_historico_demanda.png — evolução das vendas mensais por categoria
grafico_real_x_previsto.png — comparação entre valores reais e previstos
💡 Considerações
O histórico de vendas utilizado é curto e irregular, o que limita a precisão do modelo. Com a continuidade da coleta de dados pela loja, a tendência é que as previsões fiquem cada vez mais assertivas. O projeto demonstra que mesmo um modelo simples de IA pode gerar valor real para a gestão de um pequeno comércio.

👤 Autor
Bruno dos Santos Hermínio — Análise e Desenvolvimento de Sistemas
Disciplina: Inteligência Artificial para Devs — 2026.1
