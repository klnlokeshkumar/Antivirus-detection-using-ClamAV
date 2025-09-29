import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "clamav_scanner"
COLLECTION_NAME = "scan_results"

class Database:
    client = None
    database = None
    collection = None

db = Database()

async def init_db():
    """Initialize database connection"""
    try:
        db.client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Test connection
        db.client.server_info()
        db.database = db.client[DATABASE_NAME]
        db.collection = db.database[COLLECTION_NAME]
        logger.info("Connected to MongoDB successfully")
    except ServerSelectionTimeoutError as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def get_collection():
    """Get MongoDB collection"""
    if db.collection is None:
        await init_db()
    return db.collection

async def close_db():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")