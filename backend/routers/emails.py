from fastapi import APIRouter, HTTPException
from typing import List
import logging

from ..services.email_service import email_service
from ..services.summarizer_service import summarizer_service
from ..models.schemas import EmailBase, EmailWithSummary

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/emails", response_model=List[EmailBase])
async def get_emails():
    """Fetch sent emails from Gmail"""
    try:
        emails = email_service.fetch_sent_emails(max_results=10)
        return emails
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summaries", response_model=List[dict])
async def get_email_summaries():
    """Fetch emails and generate summaries"""
    try:
        emails = email_service.fetch_sent_emails(max_results=10)
        results = []
        
        for email in emails:
            try:
                summary = summarizer_service.summarize_email(email.body)
                results.append({
                    "to": email.to,
                    "subject": email.subject,
                    "summary": summary.dict()
                })
            except Exception as e:
                logger.error(f"Error summarizing email: {str(e)}")
                results.append({
                    "to": email.to,
                    "subject": email.subject,
                    "summary": {"error": f"Failed to summarize: {str(e)}"}
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Error generating summaries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))