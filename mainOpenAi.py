import streamlit as st
from streamlit_toggle import toggle
from typing import List, Dict
import asyncio
import logging
import random
from config import DEFAULT_URL, FUN_FACTS
from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content
from parseOpenAi import parse_with_openai

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

# def get_user_preferences() -> Dict[str, bool]:
#     return {
#         "vegan": toggle("Vegan"),
#         "athlete": toggle("Athlete"),
#         "gluten_free": toggle("Gluten-Free"),
#         "allergies": toggle("Allergies")
#     }
def get_user_preferences() -> Dict[str, bool]:
    return {
        "vegan": st.checkbox("Vegan"),
        "athlete": st.checkbox("Athlete"),
        "gluten_free": st.checkbox("Gluten-Free"),
        "allergies": st.checkbox("Allergies")
    }


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
        additional_preferences = st.text_area("Any additional preferences or requests?")

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
            else:
                st.warning("Please select at least one preference or add a custom request.")

    # Fun food fact
    st.sidebar.title("🍎 Fun Food Fact")
    st.sidebar.write(random.choice(FUN_FACTS))

if __name__ == "__main__":
    main()