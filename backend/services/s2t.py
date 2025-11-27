import os
from dotenv import load_dotenv
import json
from groq import Groq

def s2t(filename):
    """
    Convertit un fichier audio en texte en utilisant l'API Groq Whisper
    
    Args:
        filename: Chemin vers le fichier audio à transcrire
        
    Returns:
        Texte transcrit
    """
    load_dotenv()

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise RuntimeError("Veuillez définir GROQ_API_KEY dans .env")

    # Initialize the Groq client
    client = Groq(api_key=GROQ_API_KEY)

    # Open the audio file
    with open(filename, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(filename), file.read()),
            model="whisper-large-v3-turbo",
            prompt="Transcription d'une demande de planification de réunion",
            response_format="json",
            language="fr",
            temperature=0.0
        )
    
    # Retourner le texte transcrit
    return transcription.text

if __name__ == '__main__':
    # Test avec un fichier audio
    from create_audio import generate_audio
    generate_audio()
    filename = os.path.join(os.path.dirname(__file__), "audio", "mon_audio.wav")
    response = s2t(filename)
    print(response)
