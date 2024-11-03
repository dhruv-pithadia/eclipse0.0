import random
from mysql.connector import Error
import re
import random
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash
from audio.audioManager import AudioManager
from audio.audioTranscriber import AudioTranscriber
from utlis.ttsService import textToSpeech, saveAudioToFile
from scripts.fact_extract import extract_fact

def generate_response_with_ollama(connection, user_id, user_input):
    cursor = None  # Initialize cursor to avoid uninitialized variable reference
    try:
        if not connection:
            raise Exception("Database connection is not available.")

        # Check for specific queries with varied responses
        if re.match(r'^(what is|what\'s) (your|the bot\'s) name\??', user_input, re.IGNORECASE):
            name_responses = [
                "My name is E-C-L-I-P-S-E, Eclipse.",
                "You can call me E-C-L-I-P-S-E, Eclipse.",
                "I'm known as E-C-L-I-P-S-E, or just Eclipse.",
                "They call me E-C-L-I-P-S-E, Eclipse.",
                "I go by E-C-L-I-P-S-E, Eclipse."
            ]
            return random.choice(name_responses)

        elif re.match(r'^(what does|what\'s) (eclipse|e-c-l-i-p-s-e) stand for\??', user_input, re.IGNORECASE) or \
             re.match(r'^explain (the|your) full form of (eclipse|e-c-l-i-p-s-e)\??', user_input, re.IGNORECASE):
            acronym_responses = [
                "It stands for Enhanced Cognitive Linguistic Interactive Personal Support Engine.",
                "Eclipse is short for Enhanced Cognitive Linguistic Interactive Personal Support Engine.",
                "E-C-L-I-P-S-E means Enhanced Cognitive Linguistic Interactive Personal Support Engine.",
                "The full form of Eclipse is Enhanced Cognitive Linguistic Interactive Personal Support Engine.",
                "Enhanced Cognitive Linguistic Interactive Personal Support Engine, that’s what E-C-L-I-P-S-E stands for."
            ]
            return random.choice(acronym_responses)

        # Fetch user facts
        cursor = connection.cursor()
        cursor.execute("SELECT fact_text FROM user_facts WHERE user_id = %s", (user_id,))
        user_facts = cursor.fetchall()
        user_facts_str = ' '.join([fact[0] for fact in user_facts])

        # Fetch recent conversation history
        cursor.execute("SELECT conversation_text FROM user_conversations WHERE user_id = %s ORDER BY timestamp DESC LIMIT 3", (user_id,))
        recent_conversations = cursor.fetchall()
        recent_conversation_str = ' '.join([conv[0] for conv in recent_conversations])

        # Create prompt with user facts and conversation context
        prompt_prefix = f"Given this user data: {user_facts_str} and the recent conversation: {recent_conversation_str}\nAnswer the following prompt: '{user_input}'.\n If none is provided then answer like you are a personalised bot, keep it friendly and to the point"

        # Generate response using the Ollama model
        result = subprocess.run(
            ["ollama", "run", "llama3.1", prompt_prefix],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            if result.stdout:
                print(f"Llama response: {result.stdout.strip()}")
                return result.stdout.strip()
            else:
                print("Empty response received from Ollama.")
                return "No response received from the model."
        else:
            print(f"Error from subprocess: {result.stderr}")
            return "Error generating response."
    except Exception as e:
        print(f"Exception occurred while generating response: {e}")
        return "I'm sorry, I couldn't generate a response at this time."
    finally:
        if cursor is not None:
            cursor.close()