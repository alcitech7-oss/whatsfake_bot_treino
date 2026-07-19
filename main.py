# main.py - MODO TESTE (envia todas as mensagens de uma vez)
import os
from flask import Flask, render_template, jsonify
import json
import threading
import time

# ============================================
# CRIA O APP
# ============================================
app = Flask(__name__)


# ============================================
# CARREGA AS MENSAGENS
# ============================================
def carregar_mensagens():
    caminho = os.path.join("data", "mensagens_fake.json")
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


mensagens_completas = carregar_mensagens()
mensagens_entregues = []
index_atual = 0
LOGADO = False
TODAS_ENVIADAS = False

# ============================================
# CONFIGURAÇÃO DO TESTE
# ============================================
INTERVALO_SEGUNDOS = 3
TEMPO_LOGIN = 2


# ============================================
# TIMELINE (LOOP ÚNICO - ENVIA TODAS DE UMA VEZ)
# ============================================
def entregar_mensagem():
    global index_atual, mensagens_entregues
    if not LOGADO:
        return False
    if index_atual < len(mensagens_completas):
        msg = mensagens_completas[index_atual]
        mensagens_entregues.append(msg)
        index_atual += 1
        print(
            f"📩 [{index_atual}/{len(mensagens_completas)}] {msg['nome']} - {msg['mensagem'][:30]}..."
        )
        return True
    return False


def timeline_loop():
    global LOGADO, index_atual, mensagens_entregues, TODAS_ENVIADAS
    while True:
        if not LOGADO:
            print("⏳ Simulando login...")
            time.sleep(TEMPO_LOGIN)
            LOGADO = True
            print("✅ Login realizado! Iniciando envio...")

        if index_atual < len(mensagens_completas):
            entregar_mensagem()
        else:
            if not TODAS_ENVIADAS:
                TODAS_ENVIADAS = True
                print("\n" + "=" * 60)
                print(
                    f"✅ TODAS AS {len(mensagens_completas)} MENSAGENS FORAM ENVIADAS!"
                )
                print("=" * 60)
                print("🔄 Aguardando processamento do bot...")
                print("📊 Acesse: http://localhost:5000 para ver o progresso")
                print("=" * 60)
            time.sleep(1)

        time.sleep(INTERVALO_SEGUNDOS)


threading.Thread(target=timeline_loop, daemon=True).start()


# ============================================
# ROTAS
# ============================================
@app.route("/")
def index():
    # Converte para dicionário (caso seja objeto SQLAlchemy)
    mensagens_dict = []
    for msg in mensagens_entregues:
        if hasattr(msg, "_sa_instance_state"):
            mensagens_dict.append(
                {
                    "nome": msg.nome_contato,
                    "mensagem": msg.conteudo,
                    "horario": msg.horario,
                    "nao_lidas": 0,
                }
            )
        else:
            mensagens_dict.append(msg)

    return render_template(
        "index.html",
        mensagens=mensagens_dict,
        total=len(mensagens_completas),
        entregues=len(mensagens_entregues),
        logado=LOGADO,
        todas_enviadas=TODAS_ENVIADAS,
    )


@app.route("/api/mensagens")
def api_mensagens():
    return jsonify(
        {
            "entregues": mensagens_entregues,
            "total": len(mensagens_completas),
            "pendentes": len(mensagens_completas) - len(mensagens_entregues),
            "logado": LOGADO,
            "todas_enviadas": TODAS_ENVIADAS,
        }
    )


@app.route("/api/status")
def api_status():
    return jsonify(
        {
            "logado": LOGADO,
            "entregues": len(mensagens_entregues),
            "total": len(mensagens_completas),
            "pendentes": len(mensagens_completas) - len(mensagens_entregues),
            "index_atual": index_atual,
            "todas_enviadas": TODAS_ENVIADAS,
        }
    )


@app.route("/api/reset", methods=["POST"])
def api_reset():
    global mensagens_entregues, index_atual, LOGADO, TODAS_ENVIADAS
    mensagens_entregues = []
    index_atual = 0
    LOGADO = False
    TODAS_ENVIADAS = False
    print("🔄 Watfake resetado manualmente!")
    return jsonify({"status": "resetado"})


# ============================================
# RODA O SERVIDOR
# ============================================
if __name__ == "__main__":
    PORT = 5001
    print("=" * 60)
    print("🧪 MODO TESTE DE ACURÁCIA")
    print("=" * 60)
    print(f"📱 Watfake rodando em: http://localhost:{PORT}")
    print(f"📱 Dashboard do bot: http://localhost:5000")
    print(f"📊 Total de mensagens: {len(mensagens_completas)}")
    print(f"⚡ Intervalo: {INTERVALO_SEGUNDOS}s")
    print("=" * 60)
    app.run(host="0.0.0.0", port=PORT, debug=False)
