from flask import Flask, render_template, request, jsonify
import requests
import os
import dotenv

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found!")
else:
    print("GEMINI_API_KEY loaded successfully")

SYSTEM_PROMPT = """You are a professional legal assistant for a U.S. law firm.

CORE RULES:
1. ONLY answer legal questions
2. Keep answers short (1-2 lines)
3. Never estimate penalties
4. Always suggest consulting an attorney
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    if not GEMINI_API_KEY:
        return jsonify({"response": "Server configuration error: API key missing."})

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a valid message."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"SYSTEM INSTRUCTION: {SYSTEM_PROMPT}"}]
            },
            {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 300,
            "topP": 0.8
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        reply = result["candidates"][0]["content"]["parts"][0]["text"]

    except requests.exceptions.Timeout:
        reply = "Request timed out. Please try again."

    except requests.exceptions.RequestException as e:
        print("HTTP ERROR:", e)
        reply = "Error connecting to AI service."

    except Exception as e:
        print("GENERAL ERROR:", e)
        reply = "Error processing request."

    return jsonify({"response": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)