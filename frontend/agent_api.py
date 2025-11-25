import requests

# À mettre à jour avec les vraies endpoints
BACKEND_URL_AUDIO = "http://localhost:8000/meeting/audio"
BACKEND_URL_TEXT = "http://localhost:8000/meeting/text"


def send_to_agents_audio(audio_path):
    """
    Envoie un fichier audio au backend /meeting/audio
    """
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": f}
            response = requests.post(BACKEND_URL_AUDIO, files=files)

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def send_to_agents_text(text):
    """
    Envoie un texte brut au backend /meeting/text
    """
    try:
        payload = {"text": text}
        response = requests.post(BACKEND_URL_TEXT, json=payload)

        return response.json()

    except Exception as e:
        return {"error": str(e)}
