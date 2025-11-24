import os
from dotenv import load_dotenv
from groq import Groq
#from s2t import s2t

#filename = "./audio/mon_audio.wav"
#text = s2t(filename)
text = "Bonjour, ceci est un test de synthèse vocale avec l'API Groq."
def t2s(text):
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GROQ_API_KEY:
        raise RuntimeError("Clé api groq non defini")

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    SCOPES = ["https://api.groq.com/openai/v1/audio/speech"]

    speech_file_path = "audio/speech_groq.wav"
    model = "playai-tts"
    voice = "Fritz-PlayAI"

    response_format = "wav"

    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )

    response.write_to_file(speech_file_path)
    print("Fichier vocal speech_groq.wav crée dans audio folder.")

if __name__ == '__main__':
    t2s(text)
