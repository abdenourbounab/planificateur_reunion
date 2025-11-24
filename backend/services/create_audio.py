import sounddevice as sd
from scipy.io.wavfile import write

def generate_audio():
    fs = 44100  # Fréquence d'échantillonnage
    seconds = 10  # Durée de l'enregistrement

    print("Enregistrement...")
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1) #channels different en fonction du systems
    sd.wait()  # Attendre la fin de l'enregistrement
    write("audio/mon_audio.wav", fs, recording)
    print("Enregistrement terminé, fichier mon_audio.wav créé.")

if __name__ == '__main__':
    generate_audio()
