# Resumo para envio ao Congresso

> Versão de trabalho. Alinhar com a Profa. Martha antes do envio. Estrutura
> em uma única página, ~350 palavras, com título, palavras-chave e corpo. Em
> conformidade com a sugestão de tema do congresso de 2026 (uso da tecnologia
> para apresentação de dados relevantes ao público).

## Título

Visualização interativa como instrumento de democratização de dados sobre
educação e desenvolvimento econômico

## Palavras-chave

Visualização de dados; educação; desenvolvimento econômico; democratização do
conhecimento; Streamlit; PISA; governança.

## Resumo

A literatura empírica sobre os determinantes do desempenho educacional usa,
predominantemente, dados microeconômicos e regionalizados (Hanushek, 2020;
Dee, 2005). Comparações entre países, ainda que frequentes em jornalismo de
dados e em organismos multilaterais, esbarram em limitações conhecidas de
poder estatístico e identificação causal. Este trabalho adota objetivo
distinto. Em vez de estimar nova função de produção educacional ou propor
ranking macro entre países, constrói infraestrutura aberta de visualização
para tornar acessíveis ao público não especialista os indicadores
internacionais já disponíveis em fontes públicas, tais como World Bank Open
Data, UNDP Human Development Report e OECD PISA.

A motivação teórica vem de duas literaturas convergentes. A primeira é a
pesquisa em visualização relacional da comunidade de gestão de dados, que
documenta ganhos cognitivos da apresentação bem desenhada (Tang, Wu e Li,
2019; SIGMOD'19). A segunda é a literatura brasileira sobre visualização de
dados como prática de comunicação científica e de democratização do
conhecimento (Silva, 2019).

A entrega é um painel Streamlit bilíngue (português e inglês) que combina,
em três abas, três cruzamentos de variáveis para mais de 200 países: (i) PIB
per capita em paridade de poder de compra, em dólares constantes de 2021,
versus anos médios de escolaridade, com animação temporal de 1990 a 2024 no
estilo Gapminder; (ii) PIB per capita versus pontuação média no PISA, com
recorte transversal de 2022 e trajetórias longitudinais para países com pelo
menos três aplicações do exame; e (iii) pontuação do PISA versus dois
indicadores de governança do Worldwide Governance Indicators do Banco
Mundial, a saber, Eficácia Governamental e Controle de Corrupção. O segundo
é frequentemente utilizado como alternativa pública e gratuita ao Corruption
Perceptions Index da Transparency International, com correlação histórica
elevada (acima de 0,9 nas séries comparadas pela própria metodologia do
WGI). Todos os dados podem ser filtrados por grupos de países (G7, G20,
União Europeia, BRICS+, América Latina, Tigres Asiáticos, Lusófonos, entre
outros) e exportados em CSV. Idioma, tema e grupo selecionado são
persistidos na URL, viabilizando o compartilhamento de visualizações
específicas como link.

A contribuição é instrumental. Trata-se de pipeline reprodutível em Python
que ingere APIs oficiais, normaliza códigos ISO3, junta os indicadores em
painel limpo e os apresenta em poucos cliques. Limitações de identificação
causal são explicitamente reconhecidas; o painel apresenta correlações
descritivas e ajustes lineares apenas como referência visual.
