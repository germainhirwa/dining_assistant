import streamlit as st
from typing import Dict
import asyncio
import logging
import random
from config import DEFAULT_URL, FUN_FACTS, HEALTH_FACTS
from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content
from parseOpenAi import parse_with_openai
from audiorecorder import audiorecorder
import speech_recognition as sr
from gtts import gTTS
import io
import tempfile
import wave
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_menu(url: str) -> str:
    try:
        result = await asyncio.to_thread(scrape_website, url)
        body_content = extract_body_content(result)
        return clean_body_content(body_content)
    except Exception as e:
        logger.error(f"Error fetching menu: {str(e)}")
        return ""

def get_user_preferences() -> Dict[str, bool]:
    return {
        "vegan": st.checkbox("Vegan"),
        "athlete": st.checkbox("Athlete"),
        "gluten_free": st.checkbox("Gluten-Free"),
        "allergies": st.checkbox("Allergies")
    }

# Function to randomly choose between FUN_FACTS and HEALTH_FACTS
def get_random_fact():
    category = random.choice(["fun", "health"])
    
    if category == "fun":
        fact = random.choice(FUN_FACTS)
        category_name = "🍎 Fun Food Fact"
    else:
        fact = random.choice(HEALTH_FACTS)
        category_name = "💡 Health Fact"
    
    return category_name, fact

def format_preferences(preferences: Dict[str, bool], allergy_list: str) -> str:
    pref_list = [key for key, value in preferences.items() if value]
    if preferences["allergies"]:
        pref_list.append(f"allergies: {allergy_list}")
    return ", ".join(pref_list)

async def get_meal_recommendations(dom_content: str, preferences: str) -> str:
    try:
        dom_chunks = split_dom_content(dom_content)
        result = await asyncio.to_thread(parse_with_openai, dom_chunks, preferences)
        return result
    except Exception as e:
        logger.error(f"Error getting meal recommendations: {str(e)}")
        return "Sorry, I couldn't process your request at this time."

def speech_to_text(audio_bytes):
    r = sr.Recognizer()
    
    # Save audio_bytes to a temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        # Write audio data to the temporary file
        with wave.open(temp_audio.name, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 2 bytes per sample
            wf.setframerate(44100)  # Sample rate (adjust if needed)
            wf.writeframes(audio_bytes)
    
    try:
        # Use the temporary file for speech recognition
        with sr.AudioFile(temp_audio.name) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Sorry, there was an error processing your speech."
    finally:
        # Clean up the temporary file
        os.unlink(temp_audio.name)


def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

def main():
    st.title("🍽️ GermAI Dining Assistant")
    st.write("Your friendly AI helper for meal planning!")

    preferences = get_user_preferences()
    allergy_list = st.text_input("Please list your allergies:") if preferences["allergies"] else ""

    if st.button("🔍 Fetch Today's Menu"):
        with st.spinner("Fetching the latest menu... This might take a moment!"):
            st.session_state.dom_content = asyncio.run(fetch_menu(DEFAULT_URL))
        st.success("Menu fetched successfully! 🎉")

    if "dom_content" in st.session_state:
        st.subheader("Customize Your Meal")
        
        input_method = st.radio("Choose input method:", ("Text", "Voice"))
        
        if input_method == "Text":
            additional_preferences = st.text_area("Any additional preferences or requests?")
        else:
            st.write("Record your preferences:")
            audio = audiorecorder("Click to record", "Recording...")
            if len(audio) > 0:
                st.audio(audio.export().read())
                audio_bytes = audio.export().read()
                additional_preferences = speech_to_text(audio_bytes)
                st.write(f"Transcribed text: {additional_preferences}")
            else:
                additional_preferences = ""

        if st.button("🍳 Get Meal Recommendations"):
            full_preferences = format_preferences(preferences, allergy_list)
            if full_preferences or additional_preferences:
                with st.spinner("Cooking up your personalized menu... 👨‍🍳"):
                    result = asyncio.run(get_meal_recommendations(
                        st.session_state.dom_content,
                        f"{full_preferences}. {additional_preferences}"
                    ))
                    st.subheader("🍽️ Your Personalized Menu")
                    st.write(result)
                    
                    # Text-to-speech conversion
                    audio_file = text_to_speech(result)
                    st.audio(audio_file)
                    os.unlink(audio_file)  # Delete the temporary file
            else:
                st.warning("Please select at least one preference or add a custom request.")
    
    # Display a random fact in the sidebar
    category_name, fact = get_random_fact()
    st.sidebar.title(category_name)
    st.sidebar.write(fact)

if __name__ == "__main__":
    main()
