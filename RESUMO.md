# Resumo do projeto

**Riqueza, Educação e PISA — um Índice de Eficiência Educacional**

Este projeto investiga, em corte transversal de 57 países com dados completos
para 2022, **quanto do desempenho escolar é explicado pelos fundamentos
econômicos e institucionais de cada país** e quanto fica por conta de fatores
não diretamente observáveis. A medida-síntese é o **Índice de Eficiência
Educacional**, definido como o resíduo padronizado de uma função de produção
educacional do tipo Hanushek aumentada por um termo de governança.

A especificação preferida (M3) é log-linear em quatro insumos e estimada por
mínimos quadrados ordinários com erros-padrão robustos HC1:

ln(PISA) = θ·ln(Gasto) + β·ln(PIB) + γ·ln(MYS) + η·GovEff + δ + ε

onde **Gasto** é o gasto governamental anual por aluno do ensino secundário
(USD PPC, fonte World Bank/UNESCO UIS), **PIB** é o PIB per capita PPC (World
Bank), **MYS** são os anos médios de escolaridade do PNUD HDR e **GovEff** é o
índice de Eficácia Governamental dos Worldwide Governance Indicators (Banco
Mundial). A variável dependente é a média 2022 das três áreas do PISA. A
inclusão da governança segue o argumento institucionalista de Acemoglu, Johnson
e Robinson (Prêmio Nobel de 2024): a capacidade do setor público de converter
orçamento em serviço educacional é uma covariável de primeira ordem para o
desempenho de longo prazo. M3 atinge R² ajustado de 0,720; o gasto total em
educação como percentual do PIB não foi estatisticamente significativo em
nenhuma especificação testada — em linha com o resultado central de Hanushek
(2020) de que o tamanho do esforço fiscal não prediz a aprendizagem uma vez
controlados outros insumos.

A robustez foi verificada por mínimos quadrados em dois estágios (2SLS),
instrumentando o gasto corrente pelo gasto defasado (2005–2014). A estatística
F do primeiro estágio é 128, bem acima do limiar convencional de 10. O
coeficiente IV sobre ln(Gasto) é moderadamente superior ao OLS, consistente
com o viés para baixo previsto em Dee (2005). A escolha pelo OLS no painel
final segue da motivação de previsão (e não de identificação causal estrita) e
da maior interpretabilidade dos coeficientes.

Como complemento metodológico, comparei a especificação log-linear com
alternativas não-lineares — regressão **polinomial de grau 2 com regularização
Ridge** e uma **rede neural MLP** com uma camada oculta de quatro neurônios
(tanh, α = 1) — sob a sugestão da orientadora. A avaliação foi feita por R² em
**5-fold cross-validation**, reportando portanto desempenho fora da amostra. O
OLS log-linear obtém CV R² ≈ 0,52, a regressão polinomial Ridge alcança ≈ 0,65
e o MLP alcança ≈ 0,62. A diferença, embora consistente, ainda está dentro do
desvio-padrão de validação (≈ 0,2) que é o esperado para N = 57. Existe sinal
não-linear residual, mas não justifica abandonar a especificação interpretável
para a construção do índice publicado.

A entrega é um **dashboard Streamlit** com cinco abas: (i) painel histórico
animado de PIB per capita versus anos médios de escolaridade, com filtro por
grupo de países; (ii) ranking de eficiência com intervalos de confiança por
bootstrap; (iii) correlações bivariadas entre o PISA e cada motor candidato;
(iv) simulador "what-if" baseado nos coeficientes do M3, com botão de
restauração ao baseline do país escolhido; (v) metodologia completa, incluindo
a busca de especificação, o teste de robustez 2SLS, os diagnósticos do modelo
e a comparação com os métodos não-lineares. O código está disponível em
`app.py`; a estimação reprodutível encontra-se em `efficiency_index.ipynb`.

**Limitações.** Corte transversal de 57 países dá poder estatístico modesto;
PISA 2022 captura uma única coorte e três disciplinas; os dados de gasto são
de 2015–2018, não de 2022; a Eficácia Governamental é um composto baseado em
percepção. A identificação causal estrita exigiria painel intra-país com
variação suficiente, deixada para pesquisas posteriores.
