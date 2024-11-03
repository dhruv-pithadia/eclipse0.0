from flask import Flask, render_template, request, redirect, jsonify, url_for, session
import mysql.connector
from mysql.connector import Error
import re
import random
import string
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash
from audio.audioManager import AudioManager
from audio.audioTranscriber import AudioTranscriber
from utlis.ttsService import textToSpeech, saveAudioToFile
from scripts.fact_extract import extract_fact
from scripts.ollama_response import generate_response_with_ollama
import logger
import time
import threading
import os
import json


# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'secret_key'  # Replace with a strong secret key for production

audio_manager = AudioManager()
audio_transcriber = AudioTranscriber()
# MySQL connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='dhruv1104',  # Replace with your actual password
            database='EclipseLatest'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

# Generate unique user ID
def generate_user_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def store_conversation(connection, user_id, user_input, bot_response):
    try:
        cursor = connection.cursor()

        # Fetch the existing conversation for the user
        cursor.execute("SELECT interactions FROM user_interactions WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            # Parse the existing JSON and append the new interaction
            interactions = json.loads(result[0])
            interactions.append({"type": "user", "text": user_input})
            interactions.append({"type": "bot", "text": bot_response})

            # Update the interactions column with the new JSON
            query = "UPDATE user_interactions SET interactions = %s, timestamp = NOW() WHERE user_id = %s"
            cursor.execute(query, (json.dumps(interactions), user_id))
        else:
            # Create a new JSON object if none exists
            interactions = [
                {"type": "user", "text": user_input},
                {"type": "bot", "text": bot_response}
            ]
            query = """
            INSERT INTO user_interactions (user_id, interactions, timestamp)
            VALUES (%s, %s, NOW())
            """
            cursor.execute(query, (user_id, json.dumps(interactions)))

        connection.commit()
    except Error as e:
        print(f"Error storing conversation: '{e}'")
    finally:
        cursor.close()

# Store information in memory
def store_memory(connection, user_id, entity, fact, pattern_reference):
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO user_facts (user_id, category, fact_text, pattern_reference)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE fact_text = %s
        """
        cursor.execute(query, (user_id, entity, fact, pattern_reference, fact))
        connection.commit()
    except Error as e:
        print(f"Error storing memory: '{e}'")
    finally:
        cursor.close()



@app.route('/')
def home():
    return render_template('splash.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT user_id, password_hash FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                if user and check_password_hash(user[1], password):
                    user_id = user[0]
                    session['user_id'] = user_id  # Store user ID in the session

                    # Fetch and store user facts and patterns in the session
                    cursor.execute("SELECT fact_text FROM user_facts WHERE user_id = %s", (user_id,))
                    user_facts = cursor.fetchall()
                    session['user_facts'] = [fact[0] for fact in user_facts]  # Store as a list

                    return redirect('/chat')
                else:
                    return "Invalid username or password", 401
            except Error as e:
                print(f"Error during login: {e}")
            finally:
                cursor.close()
                connection.close()

    return render_template('login.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user_id = session.get('user_id')  # Get user_id from session
    if not user_id:
        return redirect('/')

    response = None
    if request.method == 'POST':
        user_input = request.form['user_input']
        connection = create_connection()
        if connection:
            try:
                response = generate_response_with_ollama(connection, user_id, user_input)
                print(response)

                entity, fact, pattern = extract_fact(user_input)
                if entity and fact:
                    store_memory(connection, user_id, entity, fact, pattern)

                store_conversation(connection, user_id, user_input, response)

                return jsonify({"response": response})
            except Exception as e:
                print(f"Error during chat: {e}")
                return jsonify({"response": "Error generating response"}), 500
            finally:
                connection.close()
    else:
        return render_template('chat.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
                connection.commit()
            except Error as e:
                print(f"Error during signup: {e}")
            finally:
                cursor.close()
                connection.close()
            return redirect('/login')  # Redirect to login page after successful signup

    return render_template('signup.html')

@app.route('/start_listening', methods=['POST'])
def start_listening():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"response": "User not logged in"}), 401

    try:
        audio_manager.startStream()
        audio_data = audio_manager.readAudio()
        connection = create_connection()

        if not audio_data:
            logger.warning("No audio data captured.")
            return jsonify({"response": "No audio data detected"}), 400

        if audio_manager.isSpeech(audio_data):
            transcriptions = audio_transcriber.transcribeAudio(audio_data)
            if not transcriptions:
                logger.warning("No transcriptions available.")
                return jsonify({"response": "Unable to transcribe audio"}), 400

            for response in transcriptions:
                for result in response.results:
                    if result.alternatives:
                        user_input = result.alternatives[0].transcript
                        logger.info(f"Transcribed text: {user_input}")

                        response_text = generate_response_with_ollama(connection, user_id, user_input)
                        if response_text:
                            logger.info("Response generated successfully.")
                        else:
                            logger.warning("No response generated from Ollama.")

                        return jsonify({"user_input": user_input, "response": response_text})

        return jsonify({"response": "No speech detected or unable to transcribe"}), 400

    except Exception as e:
        logger.error(f"Error during listening process: {e}")
        return jsonify({"response": "An error occurred while processing audio"}), 500

    finally:
        audio_manager.stopStream()


@app.route('/logout')
def logout():
    return redirect('/')

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True, port=5000)