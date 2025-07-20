import requests
import json
import logging
from typing import Dict, Any
from ..config import settings
from ..models.schemas import EmailSummary

logger = logging.getLogger(__name__)

class SummarizerService:
    def __init__(self):
        self.api_key = settings.together_api_key
        self.model = settings.together_model
        self.url = "https://api.together.xyz/v1/chat/completions"
    
    def summarize_email(self, email_body: str) -> EmailSummary:
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY not configured")
        
        prompt = self._create_prompt(email_body)
        
        try:
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful legal assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            response.raise_for_status()
            output = response.json()["choices"][0]["message"]["content"].strip()
            
            # Clean and parse JSON response
            output = self._clean_json_response(output)
            summary_data = json.loads(output)
            
            return EmailSummary(**summary_data)
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise Exception(f"Failed to summarize email: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {output}")
            raise ValueError(f"Invalid response format: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def _create_prompt(self, email_body: str) -> str:
        return f"""
You are a helpful legal assistant. Given the email below, return a JSON object with the following fields:
- summary: a professional billing summary of the email.
- type: either "TimeEntry" or "ExpenseEntry".
  - Use "ExpenseEntry" if the email discusses client expenses (e.g. court fees, postage, etc.).
  - Use "TimeEntry" if the email is about legal work, client communication, or tasks performed.
- rate (only for TimeEntry): hourly rate or per-task rate if mentioned, default 200.
- duration (only for TimeEntry): estimated time in hours (e.g. 0.5 for 30 minutes), default 1.0.
- price (only for ExpenseEntry): the cost of the expense.
- quantity (only for ExpenseEntry): number of items or units billed, default to 1.
- expense_type (only for ExpenseEntry): choose either "Disbursement" or "Expense Recovery".
- matter_id : the id of the case if not defualt 12060094

Email:
{email_body}

Return only valid JSON:
"""
    
    def _clean_json_response(self, output: str) -> str:
        """Clean the response to extract valid JSON"""
        # Remove markdown formatting if present
        if "```json" in output:
            start = output.find("```json") + 7
            end = output.find("```", start)
            output = output[start:end].strip()
        elif "```" in output:
            start = output.find("```") + 3
            end = output.find("```", start)
            output = output[start:end].strip()
        
        # Find JSON object boundaries
        start = output.find("{")
        end = output.rfind("}") + 1
        
        if start != -1 and end != -1:
            output = output[start:end]
        
        return output

summarizer_service = SummarizerService()