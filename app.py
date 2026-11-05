"""Almoxarifado da Manutenção — sistema de peças e ordens de serviço."""

import math
import os
import secrets
import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, url_for
from flask.cli import load_dotenv
from flask_wtf.csrf import CSRFProtect
from openai import OpenAI

PASTA_APP = Path(__file__).resolve().parent
load_dotenv(PASTA_APP / ".env")
BANCO_PADRAO = PASTA_APP / "almoxarifado.db"
MAX_INTEIRO_SQLITE = 2**63 - 1


def criar_app(caminho_banco=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
    banco = Path(caminho_banco) if caminho_banco is not None else BANCO_PADRAO
    if not banco.is_absolute():
        banco = PASTA_APP / banco
    app.config["BANCO"] = str(banco)
    CSRFProtect(app)

    def conexao():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["BANCO"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def fechar(_erro):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.route("/")
    def inicio():
        return redirect(url_for("listar_pecas"))

    @app.route("/pecas")
    def listar_pecas():
        busca = request.args.get("busca", "")
        pecas = conexao().execute(
            "SELECT * FROM pecas WHERE nome LIKE ? ORDER BY nome", (f"%{busca}%",)
        ).fetchall()
        return render_template("pecas.html", pecas=pecas, busca=busca)

    @app.route("/pecas/nova", methods=["GET", "POST"])
    def nova_peca():
        if request.method == "POST":
            f = request.form
            try:
                quantidade = int(f.get("quantidade", ""))
                minimo = int(f.get("minimo", ""))
                preco_decimal = Decimal(f.get("preco", "").replace(",", "."))
                preco = float(preco_decimal)
            except (ValueError, InvalidOperation, OverflowError):
                flash("Quantidade e mínimo devem ser inteiros; preço deve ser numérico.")
                return redirect(url_for("nova_peca"))

            if (
                quantidade < 0
                or minimo < 0
                or quantidade > MAX_INTEIRO_SQLITE
                or minimo > MAX_INTEIRO_SQLITE
                or not preco_decimal.is_finite()
                or not math.isfinite(preco)
                or preco_decimal < 0
            ):
                flash("Quantidade, mínimo e preço devem ser valores não negativos dentro do limite do banco.")
                return redirect(url_for("nova_peca"))

            campos = {nome: f.get(nome, "").strip() for nome in ("codigo", "nome", "localizacao")}
            if not all(campos.values()):
                flash("Código, nome e localização são obrigatórios.")
                return redirect(url_for("nova_peca"))

            try:
                conexao().execute(
                    "INSERT INTO pecas (codigo, nome, quantidade, minimo, preco, localizacao) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (campos["codigo"], campos["nome"], quantidade, minimo,
                     preco, campos["localizacao"]),
                )
                conexao().commit()
            except sqlite3.IntegrityError:
                conexao().rollback()
                flash("Já existe uma peça com esse código.")
                return redirect(url_for("nova_peca"))
            flash("Peça cadastrada.")
            return redirect(url_for("listar_pecas"))
        return render_template("nova_peca.html")

    @app.route("/pecas/<int:peca_id>/baixa", methods=["POST"])
    def dar_baixa(peca_id):
        try:
            quantidade = int(request.form.get("quantidade", ""))
        except ValueError:
            flash("Informe uma quantidade inteira para a baixa.")
            return redirect(url_for("listar_pecas"))
        if quantidade <= 0 or quantidade > MAX_INTEIRO_SQLITE:
            flash("A quantidade da baixa deve ser positiva e estar dentro do limite do banco.")
            return redirect(url_for("listar_pecas"))

        db = conexao()
        atualizada = db.execute(
            "UPDATE pecas SET quantidade = quantidade - ? "
            "WHERE id = ? AND quantidade >= ?",
            (quantidade, peca_id, quantidade),
        )
        if atualizada.rowcount == 0:
            peca = db.execute("SELECT id FROM pecas WHERE id = ?", (peca_id,)).fetchone()
            flash("Peça não encontrada." if peca is None else "Estoque insuficiente para essa baixa.")
            return redirect(url_for("listar_pecas"))
        db.commit()
        flash("Baixa registrada.")
        return redirect(url_for("listar_pecas"))

    @app.route("/pecas/<int:peca_id>/excluir", methods=["POST"])
    def excluir_peca(peca_id):
        db = conexao()
        excluida = db.execute("DELETE FROM pecas WHERE id = ?", (peca_id,))
        if excluida.rowcount == 0:
            flash("Peça não encontrada.")
            return redirect(url_for("listar_pecas"))
        db.commit()
        flash("Peça excluída.")
        return redirect(url_for("listar_pecas"))

    @app.route("/estoque-baixo")
    def estoque_baixo():
        pecas = conexao().execute(
            "SELECT * FROM pecas WHERE quantidade <= minimo ORDER BY nome"
        ).fetchall()
        return render_template("estoque_baixo.html", pecas=pecas)

    @app.route("/relatorio")
    def relatorio():
        pecas = conexao().execute("SELECT * FROM pecas").fetchall()
        valor_total = sum(
            (Decimal(str(p["preco"])) * p["quantidade"] for p in pecas), Decimal("0")
        )
        return render_template("relatorio.html", total_itens=len(pecas), valor_total=valor_total)

    @app.route("/ordens", methods=["GET", "POST"])
    def ordens():
        if request.method == "POST":
            equipamento = request.form.get("equipamento", "").strip()
            descricao = request.form.get("descricao", "").strip()
            if not equipamento or not descricao:
                flash("Equipamento e descrição são obrigatórios.")
                return redirect(url_for("ordens"))
            conexao().execute(
                "INSERT INTO ordens (equipamento, descricao, status, data) "
                "VALUES (?, ?, 'aberta', date('now'))",
                (equipamento, descricao),
            )
            conexao().commit()
            flash("Ordem de serviço aberta.")
            return redirect(url_for("ordens"))
        lista = conexao().execute("SELECT * FROM ordens ORDER BY data DESC").fetchall()
        return render_template("ordens.html", ordens=lista)

    @app.route("/ordens/<int:ordem_id>/resumir", methods=["POST"])
    def resumir_ordem(ordem_id):
        ordem = conexao().execute("SELECT * FROM ordens WHERE id = ?", (ordem_id,)).fetchone()
        if ordem is None:
            abort(404)
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            flash("Resumo com IA indisponível: configure OPENAI_API_KEY.")
            return redirect(url_for("ordens"))
        try:
            client = OpenAI(api_key=api_key)
            r = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Resuma em uma frase: {ordem['descricao']}"}],
            )
        except Exception:
            app.logger.exception("Falha ao resumir a ordem %s", ordem_id)
            flash("Não foi possível gerar o resumo agora.")
            return redirect(url_for("ordens"))
        flash(f"Resumo: {r.choices[0].message.content}")
        return redirect(url_for("ordens"))

    return app


if __name__ == "__main__":
    criar_app().run()
