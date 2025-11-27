import os
from dotenv import load_dotenv
from groq import Groq
import uuid

def t2s(text, output_dir=None):
    """
    Convertit du texte en audio en utilisant l'API Groq TTS
    
    Args:
        text: Texte à convertir en audio
        output_dir: Répertoire où sauvegarder le fichier audio (optionnel)
        
    Returns:
        Chemin vers le fichier audio créé
    """
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY:
        raise RuntimeError("Clé api groq non définie")

    client = Groq(api_key=GROQ_API_KEY)

    # Déterminer le répertoire de sortie
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'temp_audio')
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Générer un nom de fichier unique
    filename = f"response_{uuid.uuid4()}.wav"
    speech_file_path = os.path.join(output_dir, filename)
    
    model = "playai-tts"
    voice = "Aaliyah-PlayAI"
    response_format = "wav"

    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )

    response.write_to_file(speech_file_path)
    print(f"Fichier vocal créé: {speech_file_path}")
    
    return speech_file_path

if __name__ == '__main__':
    text = "Bonjour, ceci est un test de synthèse vocale avec l'API Groq."
    audio_path = t2s(text)
    print(f"Audio généré: {audio_path}")
