import json
import re


class TextExtractor:
    """Module for processing OCR results and extracting normalized text."""

    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the extractor with configuration.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.replace_rules = self.config.get('replace_rules', {})
        self.specific_replacements = self.config.get('specific_replacements', {})

    def normalize_text(self, text: str) -> str:
        """
        Normalize text according to extraction rules.
        
        Args:
            text: Raw text to normalize
            
        Returns:
            Normalized text
        """
        normalized = text
        
        for char_from, char_to in self.replace_rules.items():
            normalized = normalized.replace(char_from, char_to)
        
        for pattern, replacement in self.specific_replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        
        normalized = normalized.upper()
        
        return normalized

    def extract_from_response(self, response_text: str) -> dict:
        """
        Extract and process OCR results from model response.
        
        Args:
            response_text: Raw response text from the model
            
        Returns:
            Dictionary with processed results
        """
        try:
            response_json = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    response_json = json.loads(json_match.group())
                except json.JSONDecodeError:
                    raise ValueError("Could not extract valid JSON from model response")
            else:
                raise ValueError("No valid JSON found in model response")

        raw_text = response_json.get('raw_text', '')
        numbers = response_json.get('numbers', [])

        processed_results = []
        for item in numbers:
            raw = item.get('raw', '')
            normalized_raw = self.normalize_text(raw)
            processed_results.append({
                'raw': raw,
                'normalized': normalized_raw
            })

        return {
            'raw_text': raw_text,
            'numbers': processed_results
        }
