import json
from typing import Dict
import google.generativeai as genai

class LLMParserAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key="Enter_your_gemini_api_key")
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def parse(self, user_input: str) -> Dict:
        prompt = f"""
Extract the following information from the user input and return ONLY a valid JSON object:
- investments: list of {{"symbol": string, "amount": float}}
- current_portfolio_value: float
- sector_interest: string

User input: '''{user_input}'''

Return ONLY a JSON object with keys: investments, current_portfolio_value, sector_interest.
If some info is missing, use null.
Do not include any explanation or additional text, just the JSON.
"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    max_output_tokens=300
                )
            )
            
            text = response.text.strip()
            
            # Clean up the response to extract JSON
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].strip()
            
            # Try to find JSON object in the text
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                text = text[start_idx:end_idx]
            
            parsed = json.loads(text)
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"LLM parsing error: {e}")
            parsed = {"investments": [], "current_portfolio_value": None, "sector_interest": None}
            
        return parsed
