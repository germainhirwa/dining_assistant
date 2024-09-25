import re
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

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

model = OllamaLLM(model="llama3.1")

def parse_with_ollama(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_result = []
    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "parse_description": parse_description}
        )
        
        processed_response = process_response(response)
        parsed_result.append(processed_response)
        print(f"Parsed batch {i} of {len(dom_chunks)}")

    return "\n\n".join(parsed_result)

def process_response(response):
    response = re.sub(r"As an AI assistant,|As an AI,", "", response)
    response = response.strip().capitalize()
    if not response.endswith(('.', '!', '?')):
        response += '.'
    return response
