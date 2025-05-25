
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11435/api/generate"
MODEL_NAME = "llama3:latest"

@app.route("/generate", methods=["POST"])
def generate_flashcards():
    try:
        data = request.get_json()
        topic = data.get("text", "").strip()
        if not topic:
            return jsonify({"error": "El tema no puede estar vacío"}), 400

        prompt = f"""Eres un asistente educativo. Genera 3 flashcards sobre '{topic}' con:
        - Preguntas claras (1 línea)
        - Respuestas simples (1 línea)
        - Formato JSON estricto:
        {{
            "flashcards": [
                {{"pregunta": "...", "respuesta": "..."}}
            ]
        }}"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300
                }
            },
            timeout=30
        )

        if response.status_code != 200:
            return jsonify({
                "error": f"Error en Ollama (Código {response.status_code})",
                "details": response.text[:200] + "..."
            }), 502

        generated_text = response.json().get("response", "")
        start = generated_text.find("{")
        end = generated_text.rfind("}") + 1
        json_response = generated_text[start:end]
        flashcards_data = jsonify(eval(json_response))  # Usar eval para convertir texto a dict

        return flashcards_data

    except requests.exceptions.Timeout:
        return jsonify({"error": "Ollama tardó demasiado en responder"}), 504
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000)
