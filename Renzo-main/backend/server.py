from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import hashlib
import base64
import json
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Data Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    username: str
    bio: Optional[str] = None
    ai_generated_bio: Optional[str] = None
    profile_type: str = "dancer"  # dancer, musician, director, fan
    tags: List[str] = []
    profile_image: Optional[str] = None
    verification_status: str = "pending"  # pending, verified, rejected
    followers: List[str] = []
    following: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: str
    name: str
    username: str
    profile_type: str = "dancer"
    tags: List[str] = []

class UserLogin(BaseModel):
    email: str
    password: str

class Video(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: Optional[str] = None
    ai_generated_tags: List[str] = []
    genre: Optional[str] = None
    category: str = "solo"  # solo, group, duet, rehearsal, performance
    video_data: str  # base64 encoded video
    thumbnail: Optional[str] = None
    likes: List[str] = []
    views: int = 0
    ai_skill_rating: Optional[float] = None
    verification_status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class VideoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "solo"
    video_data: str

class VideoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    ai_generated_tags: List[str] = []
    genre: Optional[str] = None
    category: str
    video_data: str
    thumbnail: Optional[str] = None
    likes: List[str] = []
    views: int
    ai_skill_rating: Optional[float] = None
    verification_status: str
    created_at: datetime
    user_name: str
    user_username: str

class Connection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_user_id: str
    to_user_id: str
    status: str = "pending"  # pending, accepted, rejected
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConnectionCreate(BaseModel):
    to_user_id: str
    message: Optional[str] = None

# AI Helper Functions
async def generate_ai_bio(user_data: dict) -> str:
    """Generate AI bio for user based on their profile"""
    try:
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"bio-{user_data['id']}",
            system_message="You are a creative bio writer for performers. Generate engaging, professional bios for dancers and musicians."
        ).with_model("openai", "gpt-4o")
        
        prompt = f"""Generate a creative and engaging bio for a {user_data['profile_type']} named {user_data['name']} with tags: {', '.join(user_data['tags'])}. 
        Keep it professional but vibrant, around 100-150 words. Focus on their passion and style."""
        
        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip()
    except Exception as e:
        print(f"Error generating AI bio: {e}")
        return f"Passionate {user_data['profile_type']} with expertise in {', '.join(user_data['tags'][:3])}."

async def generate_video_tags(video_data: dict) -> List[str]:
    """Generate AI tags for uploaded video"""
    try:
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"video-tags-{video_data['id']}",
            system_message="You are an expert in dance and music analysis. Generate relevant tags for performance videos."
        ).with_model("openai", "gpt-4o")
        
        prompt = f"""Analyze this video titled "{video_data['title']}" with description: "{video_data.get('description', '')}" 
        and category: "{video_data['category']}". Generate 5-8 relevant tags for this performance video. 
        Return only the tags separated by commas."""
        
        response = await chat.send_message(UserMessage(text=prompt))
        tags = [tag.strip() for tag in response.split(',')]
        return tags[:8]  # Limit to 8 tags
    except Exception as e:
        print(f"Error generating video tags: {e}")
        return ["performance", "talent", video_data['category']]

async def generate_skill_rating(video_data: dict) -> float:
    """Generate AI skill rating for video"""
    try:
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"skill-rating-{video_data['id']}",
            system_message="You are a professional talent evaluator. Rate performances on a scale of 1-10 based on technical skill, creativity, and stage presence."
        ).with_model("openai", "gpt-4o")
        
        prompt = f"""Rate this {video_data['category']} performance titled "{video_data['title']}" on a scale of 1-10. 
        Consider technical skill, creativity, stage presence, and overall performance quality. 
        Return only the numeric rating (e.g., 8.5)."""
        
        response = await chat.send_message(UserMessage(text=prompt))
        try:
            rating = float(response.strip())
            return max(1.0, min(10.0, rating))  # Ensure rating is between 1-10
        except ValueError:
            return 7.0  # Default rating if parsing fails
    except Exception as e:
        print(f"Error generating skill rating: {e}")
        return 7.0

# Authentication Routes
@api_router.post("/auth/register", response_model=User)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    existing_username = await db.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user object
    user_dict = user_data.dict()
    user_obj = User(**user_dict)
    
    # Generate AI bio
    user_obj.ai_generated_bio = await generate_ai_bio(user_dict)
    
    # Save to database
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # In a real app, you'd verify password hash here
    # For MVP, we'll do simple email-based auth
    return {"user_id": user["id"], "message": "Login successful"}

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.get("/users", response_model=List[User])
async def get_users(limit: int = 20, skip: int = 0):
    users = await db.users.find().skip(skip).limit(limit).to_list(limit)
    return [User(**user) for user in users]

# Video Routes
@api_router.post("/videos", response_model=Video)
async def create_video(
    user_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form("solo"),
    video_data: str = Form(...)
):
    # Verify user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create video object
    video_dict = {
        "user_id": user_id,
        "title": title,
        "description": description,
        "category": category,
        "video_data": video_data
    }
    video_obj = Video(**video_dict)
    
    # Generate AI tags and skill rating
    video_obj.ai_generated_tags = await generate_video_tags(video_dict)
    video_obj.ai_skill_rating = await generate_skill_rating(video_dict)
    
    # Save to database
    await db.videos.insert_one(video_obj.dict())
    return video_obj

@api_router.get("/videos", response_model=List[VideoResponse])
async def get_videos(limit: int = 20, skip: int = 0):
    videos = await db.videos.find().skip(skip).limit(limit).to_list(limit)
    
    # Enrich videos with user data
    enriched_videos = []
    for video in videos:
        user = await db.users.find_one({"id": video["user_id"]})
        if user:
            video_response = VideoResponse(
                **video,
                user_name=user["name"],
                user_username=user["username"]
            )
            enriched_videos.append(video_response)
    
    return enriched_videos

@api_router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str):
    video = await db.videos.find_one({"id": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Increment view count
    await db.videos.update_one({"id": video_id}, {"$inc": {"views": 1}})
    video["views"] += 1
    
    # Get user data
    user = await db.users.find_one({"id": video["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return VideoResponse(
        **video,
        user_name=user["name"],
        user_username=user["username"]
    )

@api_router.post("/videos/{video_id}/like")
async def like_video(video_id: str, user_id: str = Form(...)):
    video = await db.videos.find_one({"id": video_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    likes = video.get("likes", [])
    if user_id in likes:
        # Unlike
        likes.remove(user_id)
    else:
        # Like
        likes.append(user_id)
    
    await db.videos.update_one({"id": video_id}, {"$set": {"likes": likes}})
    return {"message": "Like updated", "likes_count": len(likes)}

# Connection Routes
@api_router.post("/connections", response_model=Connection)
async def create_connection(
    from_user_id: str = Form(...),
    to_user_id: str = Form(...),
    message: str = Form("")
):
    # Verify both users exist
    from_user = await db.users.find_one({"id": from_user_id})
    to_user = await db.users.find_one({"id": to_user_id})
    
    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if connection already exists
    existing = await db.connections.find_one({
        "from_user_id": from_user_id,
        "to_user_id": to_user_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Connection already exists")
    
    # Create connection
    connection_dict = {
        "from_user_id": from_user_id,
        "to_user_id": to_user_id,
        "message": message
    }
    connection_obj = Connection(**connection_dict)
    
    await db.connections.insert_one(connection_obj.dict())
    return connection_obj

@api_router.get("/connections/{user_id}")
async def get_connections(user_id: str):
    connections = await db.connections.find({
        "$or": [
            {"from_user_id": user_id},
            {"to_user_id": user_id}
        ]
    }).to_list(100)
    
    return {"connections": connections}

@api_router.post("/connections/{connection_id}/respond")
async def respond_to_connection(connection_id: str, status: str = Form(...)):
    if status not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    connection = await db.connections.find_one({"id": connection_id})
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    await db.connections.update_one(
        {"id": connection_id},
        {"$set": {"status": status}}
    )
    
    return {"message": f"Connection {status}"}

# AI-powered recommendations
@api_router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get videos that match user's interests
    user_tags = user.get("tags", [])
    
    # Find videos with similar tags
    videos = await db.videos.find({
        "user_id": {"$ne": user_id},
        "ai_generated_tags": {"$in": user_tags}
    }).limit(10).to_list(10)
    
    # Enrich with user data
    enriched_videos = []
    for video in videos:
        video_user = await db.users.find_one({"id": video["user_id"]})
        if video_user:
            video_response = VideoResponse(
                **video,
                user_name=video_user["name"],
                user_username=video_user["username"]
            )
            enriched_videos.append(video_response)
    
    return {"recommended_videos": enriched_videos}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()