from flask import Flask, render_template, request, jsonify
import wave
import sqlite3
import os
from openai import OpenAI
import time

app = Flask(__name__)
client = OpenAI(api_key='secretkey')

def transcribe_audio(audio_filename):
    audio_file1 = open(audio_filename, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file1
    )
    return transcription.text

def create_database(db_name='audio_transcriptions.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transcriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  audio_filename TEXT, 
                  transcription TEXT)''')
    conn.commit()
    conn.close()

def store_transcription(audio_filename, transcription, db_name='audio_transcriptions.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("INSERT INTO transcriptions (audio_filename, transcription) VALUES (?, ?)", 
              (audio_filename, transcription))
    conn.commit()
    conn.close()

def get_all_transcriptions(db_name='audio_transcriptions.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT audio_filename, transcription FROM transcriptions")
    results = c.fetchall()
    conn.close()
    return results

@app.route('/')
def index():
    create_database()
    transcriptions = get_all_transcriptions()
    return render_template('index.html', transcriptions=transcriptions)

@app.route('/save_audio', methods=['POST'])
def save_audio():
    if 'audio_data' not in request.files:
        return jsonify({"error": "No audio file"}), 400
    
    audio_file = request.files['audio_data']
    audio_filename = f"output_{int(time.time())}.wav"
    audio_file.save(audio_filename)
    
    transcription = transcribe_audio(audio_filename)
    store_transcription(audio_filename, transcription)
    
    return jsonify({"message": "Audio file saved successfully", "transcription": transcription}), 200

if __name__ == '__main__':
    app.run(debug=True)
