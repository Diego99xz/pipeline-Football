"""Inicia a DuckDB Local UI com acesso ao arquivo football.duckdb.

``uv run python ui.py`` abre a DuckDB Local UI em ``http://localhost:4213``.
O catálogo da interface é mantido em memória e o banco do projeto é anexado
em modo somente leitura, pois a UI oficial precisa gravar seus próprios dados.
"""

import sys
import time
import webbrowser
from pathlib import Path

import duckdb

CAMINHO_BANCO = Path(__file__).resolve().parent / "football.duckdb"
URL_UI = "http://localhost:4213"


def _literal_sql(valor: str) -> str:
    return "'" + valor.replace("'", "''") + "'"


def main() -> int:
    if not CAMINHO_BANCO.is_file():
        print(f"Arquivo DuckDB não encontrado: {CAMINHO_BANCO}", file=sys.stderr)
        return 1

    con = None
    servidor_iniciado = False
    codigo_saida = 0
    try:
        con = duckdb.connect(":memory:")
        con.execute("INSTALL ui")
        con.execute("LOAD ui")
        con.execute(
            f"ATTACH {_literal_sql(str(CAMINHO_BANCO))} "
            "AS football (READ_ONLY)"
        )
        con.execute("USE football.bronze")

        resultado = con.execute("CALL start_ui_server()").fetchone()
        if resultado is None:
            raise RuntimeError("DuckDB não confirmou a inicialização da Local UI.")
        servidor_iniciado = True
        print(f"DuckDB Local UI disponível em {URL_UI}")
        if not webbrowser.open(URL_UI, new=2):
            print("Abra o endereço acima no navegador.")

        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\nEncerrando a DuckDB Local UI.")
    except (duckdb.Error, OSError, RuntimeError) as erro:
        print(f"Erro ao iniciar ou executar a DuckDB Local UI: {erro}", file=sys.stderr)
        codigo_saida = 1
    finally:
        if con is not None:
            if servidor_iniciado:
                try:
                    con.execute("CALL stop_ui_server()").fetchall()
                except duckdb.Error as erro:
                    print(f"Erro ao encerrar a DuckDB Local UI: {erro}", file=sys.stderr)
                    codigo_saida = 1
            con.close()

    return codigo_saida


if __name__ == "__main__":
    raise SystemExit(main())
