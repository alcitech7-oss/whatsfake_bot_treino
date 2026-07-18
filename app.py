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
INTERVALO_SEGUNDOS = 5
TEMPO_LOGIN = 5


# ============================================
# TIMELINE
# ============================================
def entregar_mensagem():
    global index_atual, mensagens_entregues
    if not LOGADO:
        return False
    if index_atual < len(mensagens_completas):
        msg = mensagens_completas[index_atual]
        mensagens_entregues.append(msg)
        index_atual += 1
        print(f"📩 Nova mensagem entregue: {msg['nome']} - {msg['mensagem'][:30]}...")
        return True
    return False


def timeline_loop():
    global LOGADO
    while True:
        if not LOGADO:
            print("⏳ Simulando login...")
            time.sleep(TEMPO_LOGIN)
            LOGADO = True
            print("✅ Login realizado! Iniciando timeline...")

        if index_atual < len(mensagens_completas):
            entregar_mensagem()
        else:
            print("✅ Todas as mensagens foram entregues!")
            break

        time.sleep(INTERVALO_SEGUNDOS)


threading.Thread(target=timeline_loop, daemon=True).start()


# ============================================
# ROTAS
# ============================================
@app.route("/")
def index():
    return render_template(
        "index.html",
        mensagens=mensagens_entregues,
        total=len(mensagens_completas),
        entregues=len(mensagens_entregues),
        logado=LOGADO,
    )


@app.route("/api/mensagens")
def api_mensagens():
    return jsonify(
        {
            "entregues": mensagens_entregues,
            "total": len(mensagens_completas),
            "pendentes": len(mensagens_completas) - len(mensagens_entregues),
            "logado": LOGADO,
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
        }
    )


@app.route("/api/reset", methods=["POST"])
def api_reset():
    global mensagens_entregues, index_atual, LOGADO
    mensagens_entregues = []
    index_atual = 0
    LOGADO = False
    return jsonify({"status": "resetado"})


# ============================================
# RODA O SERVIDOR
# ============================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"📱 Watfake rodando na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
