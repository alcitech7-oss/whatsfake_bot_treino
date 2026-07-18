from flask import Flask, render_template, jsonify
import json
import os
import threading
import time

app = Flask(__name__)


# ============================================
# CARREGA AS MENSAGENS
# ============================================
def carregar_mensagens():
    caminho = os.path.join("data", "mensagens_fake.json")
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


mensagens_completas = carregar_mensagens()

# ============================================
# ESTADO DO WATFAKE
# ============================================
mensagens_entregues = []
index_atual = 0
LOGADO = False
TIMELINE_ATIVO = True
INTERVALO_SEGUNDOS = 5
TEMPO_LOGIN = 5


# ============================================
# FUNÇÃO QUE "ENTREGA" UMA MENSAGEM NOVA
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


# ============================================
# LOOP DE TIMELINE
# ============================================
def timeline_loop():
    global LOGADO
    while TIMELINE_ATIVO:
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


# Inicia a timeline em uma thread separada
thread_timeline = threading.Thread(target=timeline_loop, daemon=True)
thread_timeline.start()


# ============================================
# ROTAS DO FLASK
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


@app.route("/api/status")
def api_status():
    return jsonify(
        {
            "logado": LOGADO,
            "entregues": len(mensagens_entregues),
            "total": len(mensagens_completas),
            "pendentes": len(mensagens_completas) - len(mensagens_entregues),
            "index_atual": index_atual,
            "tempo_login": TEMPO_LOGIN,
        }
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


@app.route("/api/reset", methods=["POST"])
def api_reset():
    global mensagens_entregues, index_atual, LOGADO
    mensagens_entregues = []
    index_atual = 0
    LOGADO = False
    return jsonify({"status": "resetado"})


if __name__ == "__main__":
    print("📱 Watfake rodando em http://127.0.0.1:5001")
    print(f"⏱️  Login simulado em: {TEMPO_LOGIN} segundos")
    print(f"⏱️  Timeline: {INTERVALO_SEGUNDOS} segundos entre mensagens")
    print(f"📦 Total de mensagens: {len(mensagens_completas)}")
    app.run(debug=True, port=5001, use_reloader=False)
