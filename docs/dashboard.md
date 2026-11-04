# Dashboard

`app.py` é a interface Streamlit. O título é “Brasileirão · Dashboard
histórico”; os dados são lidos por `painel.ler_tabelas_gold()` a partir do
banco `football.duckdb`, por meio de conexão somente leitura com Gold.

O dashboard apresenta cartões de indicadores e análises de campeões,
classificação, regiões, perfil dos clubes e relação entre posição e saldo. Os
gráficos são construídos por funções em `painel.py` com Plotly. Tabelas e
gráficos representam resultados materializados; o app não executa o pipeline.

## Filtros

As seleções de temporada são locais à análise. A Query 01 tem filtro; a
evolução de pontuação da Query 02 mostra o histórico completo. O ranking
(03), saldo (04) e aproveitamento (05) iniciam na temporada mais recente e não
oferecem “Todas as temporadas”. Desempenho regional (06) também seleciona
uma temporada. Comparativo regional (09) e relação entre posição e saldo
(10) oferecem a opção de todas as temporadas. As consultas 07 e 08 são
consolidadas e não têm filtro de temporada.

Use o botão “Recarregar dados” para limpar o cache e reler as tabelas Gold.
Se o banco, alguma tabela ou colunas esperadas estiverem ausentes, o app
apresenta uma mensagem em vez de executar o pipeline.

```bash
uv run streamlit run app.py
```
