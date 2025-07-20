from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import logging

from ..services.clio_service import clio_service
from ..services.email_service import email_service
from ..services.summarizer_service import summarizer_service
from ..models.schemas import ClioActivityResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/clio/login")
async def clio_login():
    """Redirect to Clio OAuth authorization"""
    auth_url = clio_service.get_auth_url()
    return RedirectResponse(url=auth_url)

@router.get("/clio/callback")
async def clio_callback(request: Request):
    """Handle Clio OAuth callback"""
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    
    if error:
        raise HTTPException(status_code=400, detail=f"Authorization error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    try:
        await clio_service.exchange_code_for_token(code)
        return RedirectResponse(url="/")
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.post("/clio/push-summary", response_model=ClioActivityResponse)
async def push_summary_to_clio():
    """Push email summaries to Clio as activities"""
    try:
        # Fetch and summarize emails
        emails = email_service.fetch_sent_emails(max_results=10)
        summaries = []
        
        for email in emails:
            try:
                summary = summarizer_service.summarize_email(email.body)
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Error summarizing email: {str(e)}")
                continue
        
        if not summaries:
            return ClioActivityResponse(
                status="error",
                activities_created=[],
                errors=["No summaries generated"]
            )
        
        # Push to Clio
        result = await clio_service.create_activities(summaries)
        
        return result
        
    except Exception as e:
        logger.error(f"Error pushing to Clio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clio/status")
async def clio_status():
    """Check Clio authentication status"""
    token = clio_service.get_user_token()
    return {
        "authenticated": token is not None,
        "has_access_token": token.access_token is not None if token else False
    }
