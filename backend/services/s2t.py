import os
from dotenv import load_dotenv
from create_audio import generate_audio
import json
from groq import Groq

#generation audio
generate_audio()
# Specify the path to the audio file
filename = os.path.dirname(__file__) + "audio/mon_audio.wav"# Replace with your audio file!

def s2t(filename):

    load_dotenv()

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise RuntimeError("Veuillez définir GROQ_API_KEY dans .env")

    SCOPES = ["https://api.groq.com/openai/v1/audio/transcriptions"]

    # Initialize the Groq client
    client = Groq()


    # Open the audio file
    with open(filename, "rb") as file:
        # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
        file=file, # Required audio file
        model="whisper-large-v3-turbo",# Required model to use for transcription
        prompt="Specify context or spelling",
        response_format="text",
        #timestamp_granularities = ["word", "segment"],
        language="fr",  # Optional
        temperature=0.0
        )
    response = json.dumps(transcription, indent=2, default=str)
    return response

if __name__ == '__main__':
    response = s2t()
    print(response.text)
