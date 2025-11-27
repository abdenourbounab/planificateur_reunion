import requests

# URLs des endpoints backend
BACKEND_URL_AUDIO = "http://localhost:8000/api/orchestrator/meeting/audio"
BACKEND_URL_TEXT = "http://localhost:8000/api/orchestrator/meeting/text"


def send_to_agents_audio(audio_path):
    """
    Envoie un fichier audio au backend /meeting/audio
    Le backend convertira l'audio en texte avec s2t puis appellera l'orchestrateur
    
    Args:
        audio_path: Chemin vers le fichier audio
        
    Returns:
        Résultat de la planification avec message texte et chemin audio
    """
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": (audio_path.split('/')[-1], f, "audio/wav")}
            response = requests.post(BACKEND_URL_AUDIO, files=files, timeout=120)
            response.raise_for_status()
            return response.json()

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Erreur de connexion: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_to_agents_text(text):
    """
    Envoie un texte brut au backend /meeting/text
    Le backend appellera directement l'orchestrateur avec le texte
    
    Args:
        text: Texte de la demande de réunion
        
    Returns:
        Résultat de la planification avec message texte et chemin audio
    """
    try:
        payload = {"text": text}
        response = requests.post(BACKEND_URL_TEXT, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Erreur de connexion: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
