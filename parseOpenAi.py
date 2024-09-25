import re
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

template = (
    "You are an AI assistant tasked with helping students at a dining center customize their meals. "
    "The following is the dining center menu content: {dom_content}\n\n"
    "Please follow these instructions carefully:\n\n"
    "1. **Understand the Meal Requirements:** Based on the user's request: {parse_description}, "
    "extract relevant meal options. Consider dietary preferences (e.g., vegan, gluten-free, high-protein).\n\n"
    "2. **Extract Relevant Information:** List available dishes that match the user's preferences, "
    "including the food station and any relevant timing details.\n\n"
    "3. **Format Your Response:** Present meal recommendations clearly, listing suitable dishes and where to find them.\n\n"
    "4. **Handle Missing Information:** If specific requests cannot be found, suggest alternatives or provide general meal options."
)

def parse_with_openai(dom_chunks, parse_description):
    parsed_result = []
    
    for i, chunk in enumerate(dom_chunks, start=1):
        prompt = template.format(dom_content=chunk, parse_description=parse_description)
        
        try:
            # Call the OpenAI API with GPT-3.5-turbo
            response = client.chat.completions.create(
                model="gpt-4",  # Changed from gpt-4 to gpt-3.5-turbo
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
            # You might want to add a fallback here, such as:
            parsed_result.append(f"Unable to process this part of the menu due to an error: {str(e)}")
    
    return "\n\n".join(parsed_result)

def process_response(response):
    # Remove unwanted AI references and clean the text
    response = re.sub(r"As an AI assistant,|As an AI,", "", response)
    response = response.strip().capitalize()
    if not response.endswith(('.', '!', '?')):
        response += '.'
    return response