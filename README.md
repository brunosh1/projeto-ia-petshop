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
   git clone https://github.com/SEU-USUARIO/projeto-ia-petshop.git
   cd projeto-ia-petshop
