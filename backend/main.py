"""
LLM Analysis Quiz - Main FastAPI Application
Handles quiz submission, processing, and chaining
"""
import os
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from solver.browser import BrowserManager
from solver.parser import QuizParser
from solver.downloader import DataDownloader
from solver.analyzer import DataAnalyzer
from solver.visualizer import DataVisualizer
from solver.submitter import AnswerSubmitter
from solver.utils import setup_logging, TimeoutManager

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="LLM Analysis Quiz Bot",
    description="Automated quiz solver with data analysis capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
QUIZ_SECRET = os.getenv("QUIZ_SECRET", "default-secret-change-me")
MAX_QUIZ_TIME = int(os.getenv("MAX_QUIZ_TIME", "180"))  # 3 minutes

# Global state for dashboard
quiz_history = []


class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str


class QuizResponse(BaseModel):
    status: str
    steps: list
    final_url: str
    final_answer: Any
    time_taken: float
    quizzes_solved: int = 1
    chain_complete: bool = True
    message: Optional[str] = None


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid JSON format", "errors": exc.errors()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "LLM Analysis Quiz Bot",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/history")
async def get_history():
    """Get quiz history for dashboard"""
    return {"history": quiz_history[-50:]}  # Last 50 entries


@app.post("/quiz", response_model=QuizResponse)
async def solve_quiz(quiz_request: QuizRequest):
    """
    Main quiz solving endpoint
    
    Process:
    1. Validate secret
    2. Load quiz URL with Playwright
    3. Parse question and data
    4. Download required files
    5. Analyze data
    6. Compute answer
    7. Submit answer
    8. Handle chaining (next quiz)
    9. Return results
    """
    start_time = time.time()
    steps = []
    browser_manager = None
    
    try:
        # Validate secret
        if quiz_request.secret != QUIZ_SECRET:
            logger.warning(f"Invalid secret attempt from {quiz_request.email}")
            raise HTTPException(status_code=403, detail="Invalid secret")
        
        logger.info(f"Starting quiz for {quiz_request.email}: {quiz_request.url}")
        steps.append({"step": "validate_secret", "status": "success", "time": time.time() - start_time})
        
        # Initialize timeout manager
        timeout_mgr = TimeoutManager(MAX_QUIZ_TIME)
        
        # Initialize browser manager
        browser_manager = BrowserManager()
        await browser_manager.start()
        steps.append({"step": "start_browser", "status": "success", "time": time.time() - start_time})
        
        # Process quiz chain
        current_url = quiz_request.url
        final_answer = None
        final_url = None
        quiz_count = 0
        max_quizzes = 10  # Safety limit
        
        while current_url and quiz_count < max_quizzes:
            quiz_count += 1
            
            # Check timeout
            if timeout_mgr.is_expired():
                logger.warning("Approaching timeout limit, stopping")
                break
            
            logger.info(f"Processing quiz {quiz_count}: {current_url}")
            
            # Load quiz page
            page_content = await browser_manager.load_page(current_url)
            steps.append({
                "step": f"load_quiz_{quiz_count}",
                "url": current_url,
                "status": "success",
                "time": time.time() - start_time
            })
            
            # Parse quiz content
            parser = QuizParser(page_content)
            quiz_data = parser.parse()
            
            if not quiz_data:
                logger.error("Failed to parse quiz data")
                steps.append({"step": f"parse_quiz_{quiz_count}", "status": "failed", "time": time.time() - start_time})
                break
            
            steps.append({
                "step": f"parse_quiz_{quiz_count}",
                "question": quiz_data.get("question", "")[:100],
                "status": "success",
                "time": time.time() - start_time
            })
            
            # Download required data
            downloader = DataDownloader()
            downloaded_data = await downloader.download_all(quiz_data)
            steps.append({
                "step": f"download_data_{quiz_count}",
                "files": len(downloaded_data),
                "status": "success",
                "time": time.time() - start_time
            })
            
            # Analyze data
            analyzer = DataAnalyzer()
            analysis_result = analyzer.analyze(quiz_data, downloaded_data)
            steps.append({
                "step": f"analyze_data_{quiz_count}",
                "status": "success",
                "time": time.time() - start_time
            })
            
            # Generate visualization if needed
            if quiz_data.get("requires_visualization", False):
                visualizer = DataVisualizer()
                viz_result = visualizer.create_visualization(analysis_result)
                if viz_result:
                    analysis_result["visualization"] = viz_result
                    steps.append({
                        "step": f"create_visualization_{quiz_count}",
                        "status": "success",
                        "time": time.time() - start_time
                    })
            
            # Compute final answer
            final_answer = analysis_result.get("answer")
            logger.info(f"Computed answer: {str(final_answer)[:100]}")
            
            # Submit answer
            submitter = AnswerSubmitter()
            submit_url = quiz_data.get("submit_url")
            
            if not submit_url:
                logger.error("No submit URL found")
                break
            
            submit_response = await submitter.submit(
                submit_url,
                final_answer,
                quiz_request.email
            )
            
            steps.append({
                "step": f"submit_answer_{quiz_count}",
                "url": submit_url,
                "correct": submit_response.get("correct"),
                "status": "success",
                "time": time.time() - start_time
            })
            
            final_url = submit_url
            
            # Check for next quiz URL (support both "url" and "next_url" fields)
            next_quiz_url = submit_response.get("next_url") or submit_response.get("url")
            
            if next_quiz_url and submit_response.get("correct", True):
                # Continue to next quiz in chain
                current_url = next_quiz_url
                logger.info(f"✓ Quiz {quiz_count} correct. Next quiz URL: {current_url}")
                steps.append({
                    "step": f"chain_continue_{quiz_count}",
                    "next_url": current_url,
                    "status": "continuing",
                    "time": time.time() - start_time
                })
            elif not submit_response.get("correct", True) and not timeout_mgr.is_expired():
                # Answer was wrong, could retry with alternative analysis
                logger.warning(f"Quiz {quiz_count} answer incorrect: {submit_response.get('message', 'No details')}")
                steps.append({
                    "step": f"answer_incorrect_{quiz_count}",
                    "message": submit_response.get("message", "Incorrect answer"),
                    "status": "failed",
                    "time": time.time() - start_time
                })
                # For now, stop on incorrect (could implement retry logic here)
                break
            else:
                # Chain complete - no more URLs
                logger.info(f"✓ Chain completed successfully after {quiz_count} quiz(es)")
                steps.append({
                    "step": "chain_complete",
                    "total_quizzes": quiz_count,
                    "status": "success",
                    "time": time.time() - start_time
                })
                break
        
        # Calculate total time
        time_taken = time.time() - start_time
        
        # Store in history
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "email": quiz_request.email,
            "initial_url": quiz_request.url,
            "final_url": final_url,
            "status": "success",
            "time_taken": time_taken,
            "quiz_count": quiz_count
        }
        quiz_history.append(history_entry)
        
        # Determine if chain is complete
        chain_complete = (quiz_count >= max_quizzes) or (not current_url) or timeout_mgr.is_expired()
        
        logger.info(f"✓ Quiz chain completed: {quiz_count} quiz(es) solved in {time_taken:.2f}s")
        
        return QuizResponse(
            status="ok",
            steps=steps,
            final_url=final_url or "",
            final_answer=final_answer,
            time_taken=time_taken,
            quizzes_solved=quiz_count,
            chain_complete=chain_complete,
            message=f"Successfully solved {quiz_count} quiz(es) in chain"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Error processing quiz: {e}", exc_info=True)
        time_taken = time.time() - start_time
        
        # Store failure in history
        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "email": quiz_request.email,
            "initial_url": quiz_request.url,
            "status": "failed",
            "error": str(e),
            "time_taken": time_taken
        }
        quiz_history.append(history_entry)
        
        steps.append({"step": "error", "message": str(e), "time": time_taken})
        
        return QuizResponse(
            status="error",
            steps=steps,
            final_url="",
            final_answer=None,
            time_taken=time_taken,
            quizzes_solved=0,
            chain_complete=False,
            message=f"Error: {str(e)}"
        )
    
    finally:
        # Cleanup browser
        if browser_manager:
            await browser_manager.close()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
