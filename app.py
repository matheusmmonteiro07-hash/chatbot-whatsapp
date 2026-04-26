from flask import Flask, request, jsonify
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))  

regras = """Você é um assistente virtual profissional da DL Feitosa Seguros.
Endereço: Rua Jockey Clube, 462 – Henrique Jorge, Fortaleza-CE
Telefone: (85)999417-8559
Trabalhamos com: Seguro de Carro, Moto, Veículos Pesados, Residencial, Vida e Proteção Veicular.
Coberturas principais:
Roubo e Furto + Assistência 24h,
Roubo, Furto e Terceiros + Assistência 24h,
Seguro completo (com franquia),

Seja direto, educado e sempre ofereça ajuda para fazer uma cotação.
"""

chat = client.chats.create(
    model="gemini-2.0-flash",
    config={"system_instruction": regras}
)

print("Chatbot da DL Feitosa Seguros iniciado!")

@app.route('/atendimento', methods=['POST'])
def atendimento_feitosa():
    informacao = request.json
    fala_do_cliente = informacao.get("mensagem", "").strip()

    if not fala_do_cliente:
        return jsonify({"erro": "Mensagem vazia!"}), 400

    if any(palavra in fala_do_cliente.lower() for palavra in ["seguro", "seguros", "cota", "cotar", "orçamento"]):
        frase_pronta = "DL Feitosa Bot: Claro! Trabalhamos com Seguro de Carro, Moto, Veículos Pesados, Residencial, Vida e Proteção Veicular. Quer fazer uma cotação? Posso te ajudar agora mesmo!"
        return jsonify({"bot": frase_pronta, "origem": "filtro_local"})

    try:
        response = chat.send_message(fala_do_cliente)
        return jsonify({"bot": response.text.strip(), "origem": "gemini"})

    except Exception as e:
        if "429" in str(e):
            return jsonify({"erro": "Limite atingido. Aguarde um momento..."}), 429
        return jsonify({"erro": str(e)}), 500

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))