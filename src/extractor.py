"""AI - Minimax API integration for invoice data extraction."""

import json
import os
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Extractor:
    """AI extractor using Minimax API."""

    SYSTEM_PROMPT = """You are a data extraction specialist for Brazilian fiscal invoices.

Given the invoice text, extract the following structured information:
- cnpj: The CNPJ of the supplier (with or without formatting)
- fornecedor: The supplier/company name
- data_emissao: The emission date in DD/MM/YYYY format
- valor: The total value (as shown on the invoice, with R$ and separators)

Return ONLY a valid JSON object with these fields. No additional text.

Example output:
{"cnpj": "12.345.678/0001-90", "fornecedor": "Tech Solutions Ltda", "data_emissao": "15/03/2024", "valor": "R$ 4.500,00"}
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY is required")
        self.api_url = "https://api.minimax.io/v1/chat/completions"
        self.model = "MiniMax-M2.2"

    def extract(self, invoice_text: str) -> dict | None:
        """
        Extract structured data from invoice text using Minimax.

        Returns a dict with cnpj, fornecedor, data_emissao, valor or None on failure.
        """
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": f"{self.SYSTEM_PROMPT}\n\nInvoice text:\n{invoice_text}"
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 256,
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = httpx.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            # Extract content from response
            choices = data.get("choices", [])
            if not choices:
                print(f"[EXTRACTOR] No choices in response: {data}")
                return None

            message = choices[0].get("message", {})
            content = message.get("content", "").strip()

            if not content:
                print(f"[EXTRACTOR] Empty content in response")
                return None

            # Try to find JSON in the content (model may include thinking/reasoning)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                content = content[json_start:json_end]

            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content[:-3]

            extracted = json.loads(content)
            return extracted

        except httpx.HTTPStatusError as e:
            print(f"[EXTRACTOR] HTTP error: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except json.JSONDecodeError as e:
            print(f"[EXTRACTOR] JSON parsing error: {e}")
            print(f"[EXTRACTOR] Raw content: {content if 'content' in dir() else 'N/A'}")
            return None
        except Exception as e:
            print(f"[EXTRACTOR] Extraction failed: {e}")
            return None

    def extract_from_file(self, file_path: str | Path) -> dict | None:
        """Extract data from a .txt invoice file."""
        invoice_text = Path(file_path).read_text(encoding="utf-8")
        return self.extract(invoice_text)
