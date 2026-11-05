"""Cria o banco almoxarifado.db com dados de exemplo. Rodar: python criar_banco.py"""

import sqlite3
import sys
from pathlib import Path

PASTA_APP = Path(__file__).resolve().parent
BANCO_PADRAO = PASTA_APP / "almoxarifado.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS pecas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
    minimo INTEGER NOT NULL CHECK (minimo >= 0),
    preco REAL NOT NULL CHECK (preco >= 0),
    localizacao TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ordens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipamento TEXT NOT NULL,
    descricao TEXT NOT NULL,
    status TEXT NOT NULL,
    data TEXT NOT NULL
);
"""
PECAS = [
    ("ROL-6205", "Rolamento 6205", 2, 2, 85.50, "A-01-03"),
    ("PAS-CNMG", "Pastilha de desbaste", 15, 10, 42.00, "B-02-01"),
    ("PAS-VNMG", "Pastilha de acabamento", 8, 10, 47.90, "B-02-02"),
    ("FRE-12", "Fresa de topo 12 mm", 4, 2, 210.00, "B-03-01"),
    ("FIL-AR75", "Filtro de ar", 0, 1, 380.00, "C-01-01"),
    ("FIL-OL75", "Filtro de óleo", 3, 3, 156.00, "C-01-02"),
    ("OL-VG68", "Óleo ISO VG 68 (litro)", 40, 20, 28.00, "D-01-01"),
    ("CON-40A", "Contator 40 A", 5, 2, 310.00, "E-02-02"),
]
ORDENS = [
    ("Torno 3", "Vibração no desbaste; pastilha trocada e continua.", "aberta", "2026-10-28"),
    ("Compressor 2", "Alarme CP-01 de alta temperatura no fim do turno.", "em andamento", "2026-10-30"),
    ("Fresadora 1", "Marcas no acabamento das peças de alumínio.", "fechada", "2026-10-15"),
]


def criar(caminho=None):
    banco = Path(caminho) if caminho is not None else BANCO_PADRAO
    if not banco.is_absolute():
        banco = PASTA_APP / banco
    with sqlite3.connect(banco) as con:
        con.executescript(SCHEMA)
        if con.execute("SELECT COUNT(*) FROM pecas").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO pecas (codigo, nome, quantidade, minimo, preco, localizacao) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                PECAS,
            )
        if con.execute("SELECT COUNT(*) FROM ordens").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO ordens (equipamento, descricao, status, data) VALUES (?, ?, ?, ?)",
                ORDENS,
            )


if __name__ == "__main__":
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else BANCO_PADRAO
    if not destino.is_absolute():
        destino = PASTA_APP / destino
    criar(destino)
    print("Banco inicializado em", destino)
    print("Dados de exemplo disponíveis:", len(PECAS), "peças e", len(ORDENS), "ordens de serviço.")
