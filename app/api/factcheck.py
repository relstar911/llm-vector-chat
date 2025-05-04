from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Optional
import httpx
import asyncio

router = APIRouter()

class FactCheckRequest(BaseModel):
    text: str
    language: Optional[str] = "de"

class FactCheckResult(BaseModel):
    statement: str
    found: bool
    summary: Optional[str] = None
    url: Optional[str] = None

class FactCheckResponse(BaseModel):
    results: List[FactCheckResult]


async def search_wikipedia_async(statement: str, language: str = "de"):
    url = f"https://{language}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": statement,
        "format": "json",
        "utf8": 1,
    }
    timeout = httpx.Timeout(3.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                results = resp.json().get("query", {}).get("search", [])
                if results:
                    page = results[0]
                    page_url = f"https://{language}.wikipedia.org/wiki/{page['title'].replace(' ', '_')}"
                    return True, page.get("snippet"), page_url
        except Exception as e:
            return False, f"Fehler: {str(e)}", None
    return False, None, None

@router.post("/factcheck", response_model=FactCheckResponse)
async def factcheck(req: FactCheckRequest):
    # Satztrennung und Limitierung
    statements = [s.strip() for s in req.text.split('.') if s.strip()][:5]  # max 5 Sätze
    tasks = [search_wikipedia_async(stmt, req.language) for stmt in statements]
    results = []
    try:
        responses = await asyncio.gather(*tasks)
        for stmt, (found, summary, url) in zip(statements, responses):
            results.append(FactCheckResult(
                statement=stmt,
                found=found,
                summary=summary,
                url=url
            ))
    except Exception as e:
        # Globaler Fehlerfall
        results.append(FactCheckResult(
            statement="[Fehler]",
            found=False,
            summary=f"Faktenprüfung fehlgeschlagen: {str(e)}",
            url=None
        ))
    return FactCheckResponse(results=results)
