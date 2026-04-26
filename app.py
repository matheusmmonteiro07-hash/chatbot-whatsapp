from flask import Flask, request, jsonify
from google import genai
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
import os

load_dotenv() 

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("API KEY não encontrada. Configure no Render.")

client = genai.Client(api_key=api_key)

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
    
    # 🔥 Corrigido: agora funciona com Twilio (WhatsApp)
    fala_do_cliente = request.form.get("Body", "").strip()

    if not fala_do_cliente:
        return "Mensagem vazia"

    # 🔥 SUA RESPOSTA ORIGINAL (mantida)
    if any(palavra in fala_do_cliente.lower() for palavra in ["seguro", "seguros", "cota", "cotar", "orçamento"]):
        frase_pronta = "Claro! Trabalhamos com Seguro de Carro, Moto, Veículos Pesados, Residencial, Vida e Proteção Veicular. Quer fazer uma cotação? Posso te ajudar agora mesmo!"
        resposta = frase_pronta
    else:
        try:
            response = chat.send_message(fala_do_cliente)
            resposta = response.text.strip()
        except Exception as e:
            if "429" in str(e):
                resposta = "Limite atingido. Aguarde um momento..."
            else:
                resposta = "Erro ao processar sua mensagem."

    # 🔥 Corrigido: resposta no formato do Twilio
    resp = MessagingResponse()
    resp.message(resposta)

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))