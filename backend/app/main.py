from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, Field
from uuid import uuid4
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
import json
import os
import secrets
from .database import Base, engine, get_db
from .models import Memory, Skill

if os.getenv("MEMORA_ENV", "development").lower() != "production":
    Base.metadata.create_all(bind=engine)
app = FastAPI(title="MEMORA AI API", version="0.4.0", docs_url=None if os.getenv("MEMORA_ENV", "development").lower() == "production" else "/docs", redoc_url=None if os.getenv("MEMORA_ENV", "development").lower() == "production" else "/redoc")
API_TOKEN = os.getenv("MEMORA_API_TOKEN", "").strip()
ENVIRONMENT = os.getenv("MEMORA_ENV", "development").lower()
if ENVIRONMENT == "production" and not API_TOKEN:
    raise RuntimeError("MEMORA_API_TOKEN must be configured in production")

allowed_origins = [x.strip() for x in os.getenv("MEMORA_ALLOWED_ORIGINS", "").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + ["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_origin_regex=r"chrome-extension://[a-zA-Z0-9]+",
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
if FRONTEND.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")

def require_api_token(authorization: str | None = Header(default=None)):
    if not API_TOKEN:
        return True
    expected = "Bearer " + API_TOKEN
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Valid bearer token required")
    return True

class MemoryIn(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    content: str = Field(min_length=1)
    source: str = "manual"
    source_ref: str | None = None
    importance: int = Field(default=3, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)

class SkillIn(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = ""
    instructions: str = Field(min_length=1)
    version: str = "1.0.0"
    tags: list[str] = Field(default_factory=list)

class ConversationIn(BaseModel):
    platform: str
    title: str = "Imported conversation"
    content: str = Field(min_length=1)
    conversation_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    importance: int = Field(default=3, ge=1, le=5)

def memdict(m):
    return {"id":m.id,"title":m.title,"content":m.content,"source":m.source,
            "source_ref":m.source_ref,"importance":m.importance,"tags":m.tags or [],
            "created_at":m.created_at.isoformat()}

def skilldict(s):
    return {"id":s.id,"name":s.name,"description":s.description,
            "instructions":s.instructions,"version":s.version,"tags":s.tags or [],
            "created_at":s.created_at.isoformat()}

@app.get("/api/health")
def health():
    return {"status":"ok","service":"memora-ai","version":app.version}

@app.post("/api/memories", dependencies=[Depends(require_api_token)])
def add_memory(x:MemoryIn, db:Session=Depends(get_db)):
    if x.source_ref and x.source == "android":
        existing=db.query(Memory).filter(Memory.source=="android",Memory.source_ref==x.source_ref).first()
        if existing:
            return memdict(existing)
    m=Memory(id=str(uuid4()),**x.model_dump())
    db.add(m);db.commit();db.refresh(m)
    return memdict(m)

@app.get("/api/memories", dependencies=[Depends(require_api_token)])
def memories(q:str="",tag:str="",limit:int=Query(100,ge=1,le=500),db:Session=Depends(get_db)):
    query=db.query(Memory)
    if q:
        like=f"%{q}%"
        query=query.filter(or_(Memory.title.ilike(like),Memory.content.ilike(like)))
    rows=query.order_by(Memory.created_at.desc()).limit(limit).all()
    if tag:
        rows=[m for m in rows if tag in (m.tags or [])]
    return [memdict(m) for m in rows]

@app.get("/api/agents/context", dependencies=[Depends(require_api_token)])
def agent_context(q:str=Query(min_length=1),limit:int=Query(8,ge=1,le=30),db:Session=Depends(get_db)):
    terms=[term.lower() for term in q.split() if len(term)>1]
    candidates=db.query(Memory).order_by(Memory.created_at.desc()).limit(500).all()
    ranked=[]
    for m in candidates:
        title=m.title.lower();content=m.content.lower()
        score=sum(title.count(t)*3+content.count(t) for t in terms)
        if score:
            score+=max(0,m.importance-3)*0.25
            ranked.append((score,m))
    ranked.sort(key=lambda pair:(pair[0],pair[1].created_at),reverse=True)
    return {"query":q,"retrieval":"lexical-v1","context":[
        {**memdict(m),"relevance_score":round(score,3),
         "provenance":{"source":m.source,"source_ref":m.source_ref}}
        for score,m in ranked[:limit]]}

@app.delete("/api/memories/{mid}", dependencies=[Depends(require_api_token)])
def delete_memory(mid:str,db:Session=Depends(get_db)):
    m=db.get(Memory,mid)
    if not m: raise HTTPException(404,"Memory not found")
    db.delete(m);db.commit()
    return {"deleted":True}

@app.post("/api/ingest/conversation", dependencies=[Depends(require_api_token)])
def ingest(x:ConversationIn,db:Session=Depends(get_db)):
    m=Memory(id=str(uuid4()),title=x.title,content=x.content,source=x.platform,
        source_ref=x.conversation_url,importance=x.importance,
        tags=list(set(x.tags+["conversation"])))
    db.add(m);db.commit();db.refresh(m)
    return memdict(m)

@app.post("/api/skills", dependencies=[Depends(require_api_token)])
def add_skill(x:SkillIn,db:Session=Depends(get_db)):
    s=Skill(id=str(uuid4()),**x.model_dump())
    db.add(s);db.commit();db.refresh(s)
    return skilldict(s)

@app.get("/api/skills", dependencies=[Depends(require_api_token)])
def skills(db:Session=Depends(get_db)):
    return [skilldict(s) for s in db.query(Skill).order_by(Skill.created_at.desc()).all()]

@app.get("/api/skills/{sid}/export", dependencies=[Depends(require_api_token)])
def export_skill(sid:str,format:str=Query("md",pattern="^(md|zip)$"),db:Session=Depends(get_db)):
    s=db.get(Skill,sid)
    if not s: raise HTTPException(404,"Skill not found")
    slug="".join(c.lower() if c.isalnum() else "-" for c in s.name).strip("-") or "skill"
    md=f"---\nname: {slug}\ndescription: {s.description.replace(chr(10),' ')}\n---\n\n# {s.name}\n\n{s.instructions}\n"
    if format=="md":
        return StreamingResponse(BytesIO(md.encode()),media_type="text/markdown",
            headers={"Content-Disposition":f'attachment; filename="{slug}.md"'})
    buf=BytesIO()
    with ZipFile(buf,"w",ZIP_DEFLATED) as z:
        z.writestr(f"{slug}/SKILL.md",md)
        z.writestr(f"{slug}/memora-skill.json",json.dumps({"name":s.name,"version":s.version,"tags":s.tags},indent=2))
    buf.seek(0)
    return StreamingResponse(buf,media_type="application/zip",
        headers={"Content-Disposition":f'attachment; filename="{slug}.zip"'})

@app.get("/")
def dashboard():
    index=FRONTEND/"index.html"
    if not index.exists():
        return {"service":"MEMORA AI API","docs":"/docs","health":"/api/health"}
    return FileResponse(index)
