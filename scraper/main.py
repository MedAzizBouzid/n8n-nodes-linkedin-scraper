from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import subprocess
import sys
import pandas as pd
import os

app = FastAPI()

class ScrapeRequest(BaseModel):
    job_name: str
    job_location: str
    pages_to_extract: int

@app.post("/scrape")
def scrape(data: ScrapeRequest):
    try:
        # Run your script
        process = subprocess.run(
            [
                sys.executable,
                "scraper.py",
                data.job_name,
                data.job_location,
                str(data.pages_to_extract),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # stdout = CSV path (by your design)
        csv_path = process.stdout.strip()

        if not os.path.exists(csv_path):
            raise HTTPException(
                status_code=500,
                detail=f"CSV not found at {csv_path}"
            )

        # Read CSV and convert to both JSON and CSV string
        df = pd.read_csv(csv_path)
        results = df.to_dict(orient="records")
        
        # Generate CSV content as string
        csv_content = df.to_csv(index=False, encoding='utf-8')

        return {
            "success": True,
            "total_jobs": len(results),
            "results": results,
            "csv_content": csv_content  # CSV as string for n8n
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Scraper execution failed",
                "stdout": e.stdout,
                "stderr": e.stderr
            }
        )

# Optional: Separate endpoint that returns ONLY CSV
@app.post("/scrape-csv")
def scrape_csv(data: ScrapeRequest):
    try:
        # Run your script
        process = subprocess.run(
            [
                sys.executable,
                "scraper.py",
                data.job_name,
                data.job_location,
                str(data.pages_to_extract),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        csv_path = process.stdout.strip()

        if not os.path.exists(csv_path):
            raise HTTPException(
                status_code=500,
                detail=f"CSV not found at {csv_path}"
            )

        # Read CSV file content
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()

        # Return as CSV file response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=job_offers_{data.job_name.replace(' ', '_')}.csv"
            }
        )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Scraper execution failed",
                "stdout": e.stdout,
                "stderr": e.stderr
            }
        )