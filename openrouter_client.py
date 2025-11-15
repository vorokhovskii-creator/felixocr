import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""

    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-r1:free')
        self.base_url = 'https://openrouter.ai/api/v1'
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

    def send_image_for_ocr(self, image_base64: str, system_prompt: str, user_prompt: str) -> str:
        """
        Send an image to OpenRouter for OCR processing.
        
        Args:
            image_base64: Base64 encoded image string
            system_prompt: System prompt for the model
            user_prompt: User prompt for the model
            
        Returns:
            Response text from the model
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': user_prompt
                        },
                        {
                            'type': 'image',
                            'image': image_base64
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise ValueError("Unexpected response format from OpenRouter API")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error communicating with OpenRouter API: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing OpenRouter API response: {str(e)}")
