import os
from flask import Flask, render_template, jsonify
import json
import threading
import time

app = Flask(__name__)

# ... (resto do código)

if __name__ == "__main__":
    # ============================================
    # USA A PORTA DO RENDER (ou 5001 localmente)
    # ============================================
    port = int(os.environ.get("PORT", 5001))
    print(f"📱 Watfake rodando na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
