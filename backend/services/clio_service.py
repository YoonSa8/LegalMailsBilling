import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from ..config import settings
from ..models.schemas import EmailSummary, ClioActivityResponse, TokenData

logger = logging.getLogger(__name__)

class ClioService:
    def __init__(self):
        self.client_id = settings.clio_client_id
        self.client_secret = settings.clio_client_secret
        self.redirect_uri = settings.clio_redirect_uri
        self.base_url = settings.clio_base_url
        self.user_sessions = {}  # In production, use Redis or database
    
    def get_auth_url(self) -> str:
        return (
            f"{self.base_url}/oauth/authorize"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=all"
        )
    
    async def exchange_code_for_token(self, code: str) -> TokenData:
        token_url = f"{self.base_url}/oauth/token"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    token_url,
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri
                    },
                    timeout=30
                )
                
                response.raise_for_status()
                token_data = response.json()
                
                # Store token for demo user (in production, use proper user management)
                user_id = "demo_user"
                token = TokenData(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token")
                )
                
                self.user_sessions[user_id] = token
                return token
                
            except httpx.HTTPError as e:
                logger.error(f"Token exchange failed: {str(e)}")
                raise Exception(f"Failed to exchange code for token: {str(e)}")
    
    def get_user_token(self, user_id: str = "demo_user") -> Optional[TokenData]:
        return self.user_sessions.get(user_id)
    
    async def create_activities(self, summaries: List[EmailSummary]) -> ClioActivityResponse:
        user_id = "demo_user"
        token = self.get_user_token(user_id)
        
        if not token:
            raise Exception("User not authenticated with Clio")
        
        api_url = f"{self.base_url}/api/v4/activities"
        responses = []
        errors = []
        
        async with httpx.AsyncClient() as client:
            for summary in summaries:
                try:
                    payload = self._create_activity_payload(summary)
                    print(payload)
                    response = await client.post(
                        api_url,
                        headers={
                            "Authorization": f"Bearer {token.access_token}",
                            "Content-Type": "application/json"
                        },
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code in [200, 201]:
                        try:
                            responses.append(response.json())
                        except:
                            responses.append({"status": "created", "code": response.status_code})
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                
                except Exception as e:
                    error_msg = f"Error creating activity: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
        
        return ClioActivityResponse(
            status="success" if responses else "error",
            activities_created=responses,
            errors=errors if errors else None
        )
    
    # def _create_activity_payload(self, summary: EmailSummary) -> Dict[str, Any]:
    #     today = date.today().isoformat()
    #     now_time = datetime.now().strftime("%H:%M")
        
    #     if summary.type == "TimeEntry":
    #         return {
    #             "data": {
    #                 "type": "TimeEntry",
    #                 "attributes": {
    #                     "description": summary.summary,
    #                     "date": today,
    #                     "time": now_time,
    #                     "billable": True,
    #                     "rate": summary.rate or 200,
    #                     "quantity": summary.duration or 1.0,
    #                     "matter_id": 123456789  # Replace with actual matter ID
    #                 }
    #             }
    #         }
    #     else:  # ExpenseEntry
    #         return {
    #             "data": {
    #                 "type": "ExpenseEntry",
    #                 "attributes": {
    #                     "description": summary.summary,
    #                     "date": today,
    #                     "time": now_time,
    #                     "billable": True,
    #                     "price": summary.price or 100,
    #                     "quantity": summary.quantity or 1,
    #                     "expense_type": summary.expense_type or "Disbursement",
    #                     "matter_id": 123456789  # Replace with actual matter ID
    #                 }
    #             }
    #         }
    def _create_activity_payload(self, summary: EmailSummary) -> Dict[str, Any]:
        today = date.today().isoformat()
        
        if summary.type == "TimeEntry":
            return {
                "data": {
                    "type": "TimeEntry",
                    "attributes": {
                        "description": summary.summary,
                        "date": today,
                        "billable": True,
                        "rate": summary.rate or 200,
                        "quantity": summary.duration or 1.0,
                        "matter_id": summary.matter_id
                    }
                }
            }
        else:  # ExpenseEntry
            return {
                "data": {
                    "type": "ExpenseEntry",
                    "attributes": {
                        "description": summary.summary,
                        "date": today,
                        "billable": True,
                        "price": summary.price or 100,
                        "quantity": summary.quantity or 1,
                        "expense_type": summary.expense_type or "Disbursement",
                        "matter_id":summary.matter_id
                    }
                }
            }
        

clio_service = ClioService()