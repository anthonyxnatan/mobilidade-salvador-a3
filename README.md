# Mobilidade urbana: transporte público e o crescimento da população em Salvador-BA

Projeto A3 da UC **Análise de Dados e Big Data** da **UNIFACS**.
Professor: **Eduardo Sidney da Silva Xavier**. Entrega final: 03/12/2026.

| Entrega | Link |
|---|---|
| Dashboard interativo (Streamlit) | https://mobilidade-salvador.streamlit.app |
| Vídeo de apresentação (YouTube) | [https://youtu.be/loBg9GbHmdU](https://youtu.be/loBg9GbHmdU) |
| Relatório final (ETL, EDA, diagnóstico, previsões e prescrições) | [PDF](relatorios/Relatorio_Final_A3.pdf) · [Word](relatorios/Relatorio_Final_A3.docx) |
| Notebook de ETL | [notebooks/01_ETL.ipynb](notebooks/01_ETL.ipynb) |
| Notebook de análises | [notebooks/02_Analises.ipynb](notebooks/02_Analises.ipynb) |

## Equipe

| Nome | RA |
|---|---|
| Anthony Natan Santos Pereira | 12725158136 |
| Caio Branco Marques | 12725131949 |
| Clara Gil Moreira de Alencar Santiago | 12725138774 |
| Lukas Carneiro Rocha | 12725157428 |
| Pedro Henrique Almeida Chaves | 12722120616 |

## O que o projeto investiga

O tema aprovado fala em crescimento da população, mas os dados oficiais mostram o contrário: Salvador perdeu 9,6% dos
moradores entre os Censos de 2010 e 2022, enquanto a frota de automóveis e motocicletas cresceu. O projeto responde a
quatro perguntas:

1. A oferta de transporte público acompanhou a população? A frota por habitante aumentou, porque a população caiu,
   mas a oferta efetiva piorou: entre 2022 e 2025 a velocidade dos ônibus no pico passou de 21,5 para 16,5 km/h e as
   viagens não completadas subiram de 5% para 16,2%.
2. Por que a demanda por ônibus caiu? Entre 2019 e 2024 o sistema perdeu cerca de 250 mil passageiros por dia
   (−16,7%). A queda da população explica cerca de 17% dessa perda e o metrô, no máximo, 11%; os 72% restantes
   associam-se a outros fatores, como o crescimento da frota de automóveis e motocicletas e a perda de qualidade do serviço.
3. Mais ônibus significariam mais congestionamento? Não necessariamente: entre 2014 e 2025 a cidade ganhou cerca de
   166 mil automóveis e 110 mil motocicletas, enquanto o sistema municipal opera cerca de 1.840 ônibus. Com prioridade
   viária, a oferta pode crescer sem prejuízo ao trânsito.
4. Qual é a tendência até 2030? No cenário tendencial, o ônibus chegaria a cerca de 1,04 milhão de passageiros por dia,
   o metrô a cerca de 123 milhões por ano e a motorização ficaria entre 494 e 521 veículos por mil habitantes.

## Fontes de dados (apenas oficiais)

| Fonte | Dados | Forma de extração |
|---|---|---|
| IBGE: Censos 2010 e 2022, Estimativas, IPCA | população, densidade, deslocamento casa-trabalho, inflação | API SIDRA (JSON) |
| SENATRAN / Ministério dos Transportes | frota por município e tipo (dez/2014 a dez/2025) | download de planilhas (xls, xlsx, rar) |
| Ministério das Cidades: PEMOB 2023 e 2026 | oferta e operação do transporte (anos-base 2022 e 2025) | download de planilhas |
| SEI-BA: IMEC | passageiros de ônibus urbanos por mês | leitura de PDF |
| CTB e Cia. do Metrô da Bahia | passageiros do metrô (mensal e anual) | demonstrativo oficial e demonstrações financeiras |
| Prefeitura de Salvador (SEMOB, Casa Civil) e ARSAL | tarifas, linhas, frota e passageiros do STCO | documentos oficiais (valores registrados com página e link) |
| Integra Salvador (concessionárias) | retrato atual do sistema (linhas, viagens, km) | site oficial, usado só como referência |

A lista completa, com URL e data de acesso de cada valor, está em
[`data/raw/documentos/fontes_documentais.csv`](data/raw/documentos/fontes_documentais.csv) e no `log_coleta` dos downloads.

## Estrutura do repositório

```
├── app/
│   ├── streamlit_app.py          # dashboard interativo
│   ├── ui.py                     # componentes visuais do dashboard
│   └── assets/                   # logo e contornos do mapa
├── data/
│   ├── raw/                      # arquivos originais, como foram baixados (com hash SHA-256)
│   ├── processed/                # tabelas tratadas em CSV (saída do ETL e das análises)
│   └── db/mobilidade_salvador.sqlite   # banco SQLite com todas as tabelas tratadas
├── figuras/                      # gráficos do relatório e capturas do dashboard
├── notebooks/
│   ├── 01_ETL.ipynb              # extração, transformação, carga e testes de qualidade
│   └── 02_Analises.ipynb         # EDA, diagnóstico, previsões e prescrições
├── relatorios/                   # relatório final em Word e PDF (normas ABNT)
├── scripts/
│   ├── coleta_dados_brutos.py    # baixa os dados brutos das fontes oficiais
│   └── coleta_colab.ipynb        # a mesma coleta, pronta para o Google Colab
├── src/estilo.py                 # paleta de cores e funções de gráfico
├── requirements.txt              # pacotes do dashboard
└── requirements-notebooks.txt    # pacotes da coleta, do ETL e das análises
```

## Principais números

| Indicador | Valor | Fonte |
|---|---|---|
| População (Censo 2010 → 2022) | 2.675.656 → 2.417.678 (−9,6%) | IBGE |
| Autos e motos por mil habitantes (2014 → 2025) | 300 → 437 | SENATRAN e IBGE |
| Passageiros de ônibus por dia (2019 → 2024) | 1,5 mi → 1,25 mi | Prefeitura (SEMOB) |
| Velocidade do ônibus no pico (2022 → 2025) | 21,5 → 16,5 km/h | PEMOB |
| Passageiros do metrô (2025) | 117,5 milhões | CTB |
| Trabalhadores que vão de ônibus (2022) | 44,7%, maior entre as capitais | IBGE, Censo 2022 |
| Tempo médio casa-trabalho: ônibus × carro (2022) | 59,2 × 32,5 min | IBGE, Censo 2022 |

## Uso

Trabalho acadêmico. Os dados são públicos e pertencem aos órgãos citados em cada tabela.
