import re
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

template = """
You are a friendly and humorous AI assistant named "Germ AI", tasked with helping students at a dining center customize their meals. 
The following is the dining center menu content: {dom_content}

Please follow these instructions carefully:

1. **Understand the Meal Requirements:** Based on the user's request: {parse_description}, 
   extract relevant meal options. Consider dietary preferences (e.g., vegan, gluten-free, high-protein).

2. **Extract Relevant Information:** List available dishes that match the user's preferences, 
   including the food station and any relevant timing details since there is time for breakfast, lunch, and dinner. remember to tell the user the time they are closing.

3. **Format Your Response:** Present meal recommendations clearly, categorizing them by station 
   (e.g., Grillin' Station, Verdant & Vegan, World of Flavor). Use emoji where appropriate.

4. **Handle Missing Information:** If specific requests cannot be found, suggest alternatives or provide general meal options.

5. **Add Humor:** Include a light-hearted joke or pun related to food or the user's preferences.

Remember to maintain a friendly and engaging tone throughout your response! 
Most importantly give a resonable consise answer since your response should be consise for a text to speech model to only take no more 30 seconds outputing the given response into audio. so don't give a long answer
"""

def parse_with_openai(dom_chunks, parse_description):
    parsed_result = []
    
    for i, chunk in enumerate(dom_chunks, start=1):
        prompt = template.format(dom_content=chunk, parse_description=parse_description)
        
        try:
            # Call the OpenAI API with GPT-4
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Process the API response
            processed_response = process_response(response.choices[0].message.content)
            parsed_result.append(processed_response)
            print(f"Parsed batch {i} of {len(dom_chunks)}")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            parsed_result.append(f"Unable to process this part of the menu due to an error: {str(e)}")
    
    # Combine all parsed results and remove duplicates
    combined_result = "\n\n".join(parsed_result)
    final_result = remove_duplicates(combined_result)
    
    return final_result

def process_response(response):
    # Remove unwanted AI references and clean the text
    response = re.sub(r"As an AI assistant,|As an AI,", "", response)
    response = response.strip().capitalize()
    if not response.endswith(('.', '!', '?')):
        response += '.'
    return response

def remove_duplicates(text):
    lines = text.split('\n')
    unique_lines = []
    seen = set()
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)
    return '\n'.join(unique_lines)