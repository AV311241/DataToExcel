import os
import json
import re
from typing import Dict, Any, Optional

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI


class AIForDataFill:
    """Class wrapper for product copy generation using a chat LLM + agent.

    Usage:
        ai = AIForDataFill(api_key_env='GOOGLE_API_KEY')
        out = ai.get_response(product_json)

    The class avoids hard-coding API keys. If the required LLM packages are not
    available or the API key is missing, `get_response` will fall back to a
    deterministic `fake_response` useful for offline testing.
    """

    def __init__(self, model: str = "gemini-2.0-flash-lite", api_key: str = "GOOGLE_API_KEY",include_column_ai_response:list = None ):
        self.model = model
        self.api_key = "AIzaSyCmX2C84RaXYnisvzd3n94cEFMMUjMmdqo"
        self.agent = None
        self.include_column_ai_response = include_column_ai_response

        # Build a clear system prompt used by the agent
        self.system_prompt = (
            "You are a product copywriter. Given the exact product JSON below, "
            "produce a JSON object with ONLY these keys: `Short Description`, `Description`, and `Tag`."
            "Rules (must follow exactly):"
            "1) Output must be valid JSON and contain exactly the three keys (no extra keys)."
            "2) `Short Description` should be 1-2 short sentences (around 10-25 words)."
            "3) `Description` should be 2-4 short paragraphs (detailed, marketing-friendly)."
            "4) `Tag` should be a comma-separated list of short tags (no sentence)."
            "5) Do not output any explanatory text, markdown, or metadata — only the JSON object."
            "Return the JSON now."
        )

        # Initialize the LLM/agent if possible
        if ChatGoogleGenerativeAI is not None and create_agent is not None and self.api_key:
            print("Initializing agent...")
            print(self.include_column_ai_response)
            try:
                llm = ChatGoogleGenerativeAI(model=self.model, api_key=self.api_key)
                self.agent = create_agent(system_prompt=self.system_prompt, model=llm)
            except Exception as e:
                print(f"Error initializing agent: {e}")
                # If initialization fails, keep agent as None and use fallback
                self.agent = None

    @staticmethod
    def fake_response(_input: Dict[str, Any]) -> Dict[str, str]:
        """A deterministic fallback response useful for testing without a live LLM."""
        return {
            "Short Description": "Gentle, tear-free body wash and shampoo combo for babies with natural ingredients.",
            "Description": (
                "Mamaearth’s deeply nourishing body wash and gentle cleansing shampoo combo is designed for "
                "your baby’s delicate skin and hair. This tear-free formula ensures a happy bath time experience "
                "without irritation.\n\nEnriched with Aloe Vera, coconut-based cleansers, and Calendula, it hydrates, "
                "soothes, and protects while maintaining skin moisture and improving hair texture."
            ),
            "Tag": "Mamaearth Baby Wash, Baby Shampoo, Tear Free, Natural Baby Care"
        }

    def build_prompt(self, product: Dict[str, Any]) -> str:
        """Create the single large prompt text sent to the agent/LLM."""
        return f"{str(input)}"



    
    def extract_json(self,result) -> dict:

        try:
            if hasattr(result, "content"):
                ai_content = result.content
            elif isinstance(result, dict) and "messages" in result:
                ai_content = result["messages"][1].content
            else:
                ai_content = str(result)

            # Clean markdown fences
            if ai_content.startswith("```json"):
                ai_content = ai_content.replace("```json", "").replace("```", "").strip()

            # Parse JSON
            data = json.loads(ai_content)
            extrated_response = {}
            for key in self.include_column_ai_response:
                extrated_response[key]=data.get(key,"Not_Found in AI reaponse")
            # Return only required fields
            return extrated_response

        except Exception as e:
            print(f"Error extracting AI message: {e}")
            return {}


    def get_response(self, product: Dict[str, Any], use_agent: Optional[bool] = True) -> dict:
        """Return the model/agent response for the provided product JSON.
        """
        prompt = self.build_prompt(product)

        if use_agent and self.agent is not None:
            try:
                # The agent is expected to accept a dict with messages similar to chat APIs
                result = self.agent.invoke({"messages": [{"role": "user", "content": prompt}]})
                return self.extract_json(result)
            except Exception as e:
                print("ai call Failed.")
                print(e)
        else :
            print("somtheng went wrong token expire")
            return {}

# if __name__ == "__main__":
# #     # Small demo showing how to use the class. Replace env var or set GOOGLE_API_KEY
#     # in your environment if you want to use a real model.
#     sample_product = {
#     'Product Name': 'Mamaearth Charcoal Black Long Stay Kajal with Vitamin C & Chamomile for 11-Hour Smudge-free Stay',
#     'Brand Name': 'Mamaearth',
#     'Category': 'Beauty,Makeup',

# }

    

#     ai = AIForDataFill()
#     print("Using agent:", ai.agent is not None)
#     out = ai.get_response(sample_product)
#     print(out)

