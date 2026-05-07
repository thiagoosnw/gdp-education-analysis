# Resumo do projeto

Riqueza, Educação e PISA: visualização interativa para democratização de
dados sobre educação e desenvolvimento econômico.

A pesquisa empírica em educação comparada esbarra em uma assimetria
conhecida. A literatura mais consolidada sobre os determinantes da
aprendizagem usa dados microeconômicos e regionalizados (Hanushek, 1986;
Hanushek, 2020; Dee, 2005), ao passo que comparações entre países, embora
frequentes em jornalismo de dados, raramente sobrevivem ao escrutínio
metodológico. Em vez de tentar estimar relações causais a partir de um
corte transversal de poucas dezenas de países, esforço que reconhecidamente
carece de poder estatístico e de instrumentos críveis, este projeto adota um
objetivo distinto e mais modesto. A meta é tornar acessíveis, por meio de
visualização interativa, os indicadores macro de educação, riqueza e
governança que estão disponíveis em fontes públicas mas dispersos em
planilhas pouco navegáveis para o público não especialista.

A motivação metodológica vem de duas literaturas. A primeira é a pesquisa em
visualização relacional da comunidade de bancos de dados, que documenta
sistematicamente como gráficos bem desenhados reduzem o custo cognitivo de
explorar bases multivariadas e ampliam o público capaz de extrair insight a
partir delas (Tang, Wu e Li, 2019). A segunda é a literatura brasileira
sobre visualização de dados como prática de comunicação científica (Silva,
2019), que enfatiza a articulação entre infografia, narrativa e
democratização do conhecimento.

A entrega é um painel Streamlit bilíngue (português e inglês) que combina,
em três abas, três cruzamentos elementares de variáveis sobre mais de 200
países:

1. PIB per capita versus anos médios de escolaridade, com animação temporal
   de 1990 a 2024 e bolhas dimensionadas pela população, no estilo
   Gapminder. O eixo do PIB usa valores constantes de 2021 em paridade de
   poder de compra (World Bank `NY.GDP.PCAP.PP.KD`), evitando distorções de
   inflação ao comparar décadas.
2. PIB per capita versus pontuação no PISA, com recorte transversal de 2022
   e trajetórias longitudinais para os países com pelo menos três
   aplicações do PISA. A escolha pelo recorte estático de 2022 é
   justificada pelo fato de 38 dos 84 países só terem ingressado no PISA
   naquela onda, o que tornaria uma animação contínua enganosa.
3. Pontuação do PISA versus dois indicadores de governança do Worldwide
   Governance Indicators do Banco Mundial, a saber, Eficácia Governamental
   e Controle de Corrupção. O Controle de Corrupção do WGI é amplamente
   utilizado como alternativa pública e gratuita ao Corruption Perceptions
   Index da Transparency International, com correlação histórica elevada
   nas séries comparadas pela própria metodologia do WGI.

Todas as fontes são oficiais e gratuitas: World Bank Open Data (PIB,
população, governança), UNDP Human Development Report (anos médios de
escolaridade) e OECD PISA (pontuações). Cada aba inclui filtro por grupo de
países (G7, G20, União Europeia, BRICS+, América Latina, Tigres Asiáticos,
Lusófonos, entre outros), destaque opcional de países, ajuste linear (OLS)
por referência visual quando cabível, e botão de download do recorte
filtrado em CSV. Idioma, tema e grupo selecionado são persistidos na URL,
de modo que visualizações específicas podem ser compartilhadas como link.

A contribuição principal não está, portanto, em uma nova estimação
econométrica, mas em infraestrutura de visualização. Trata-se de um
pipeline em Python que ingere as APIs oficiais, normaliza ISO3, junta os
indicadores em um painel longitudinal limpo, e os apresenta em poucos
cliques a um leitor sem domínio técnico de bases de dados. O código é
aberto, totalmente reproduzível em ambiente local com um único comando
(`install.cmd` no Windows, `pip install -r requirements.txt` em Linux e
macOS), e usa apenas bibliotecas livres (Streamlit, Plotly, pandas).

Limitações. O dashboard apresenta correlações simples; nenhum esforço de
identificação causal é feito. A metodologia robusta de comparação entre
países demandaria desenhos quase experimentais ou painel intra-país com
variação suficiente, deixados para trabalhos posteriores. As perguntas
substantivas sobre eficiência educacional, retorno do gasto público e papel
das instituições, discutidas pela literatura clássica de Hanushek e pela
linha institucionalista de Acemoglu, Johnson e Robinson, continuam abertas.
A intenção aqui é mais elementar: abrir uma porta de entrada visual para
quem queira começar a investigá-las.
