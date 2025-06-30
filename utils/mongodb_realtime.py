from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime
from typing import Dict, Any, List, Optional
import streamlit as st
import logging
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

def get_mongo_client(connection_string):
    """Get MongoDB client for realtime database."""
    return MongoClient(connection_string, server_api=ServerApi('1'))

def get_database_name():
    """Get the database name from configuration."""
    config_manager = ConfigManager()
    return config_manager.get_setting('database_settings.database_name', 'physiobot-realtime')

def check_identifier(connection_string: str, identifier: str, cohort_id: Optional[str] = None) -> bool:
    """
    Check if the identifier exists in the valid_identifiers collection.
    
    Args:
        connection_string: MongoDB connection string
        identifier: Student identifier to check
        cohort_id: Optional cohort ID for multi-cohort filtering
        
    Returns:
        True if identifier is valid, False otherwise
    """
    client = get_mongo_client(connection_string)
    db_name = get_database_name()
    db = getattr(client, db_name)
    
    try:
        query = {"identifier": identifier, "is_active": True}
        if cohort_id:
            query["cohort_id"] = cohort_id
            
        result = db.valid_identifiers.find_one(query)
        return bool(result)
    except Exception as e:
        logger.error(f"Error checking identifier {identifier}: {e}")
        return False
    finally:
        client.close()

def get_student_cohort(connection_string: str, identifier: str) -> Optional[str]:
    """
    Get the cohort ID for a given student identifier.
    
    Args:
        connection_string: MongoDB connection string
        identifier: Student identifier
        
    Returns:
        Cohort ID if found, None otherwise
    """
    client = get_mongo_client(connection_string)
    db_name = get_database_name()
    db = getattr(client, db_name)
    
    try:
        result = db.valid_identifiers.find_one(
            {"identifier": identifier, "is_active": True},
            {"cohort_id": 1}
        )
        return result.get("cohort_id") if result else None
    except Exception as e:
        logger.error(f"Error getting cohort for identifier {identifier}: {e}")
        return None
    finally:
        client.close()

def log_audio_transcript(connection_string: str, conversation_type: str, transcript_data: Dict[str, Any]) -> Optional[str]:
    """
    Log audio conversation transcript to database.
    
    Args:
        connection_string: MongoDB connection string
        conversation_type: "patient" or "supervisor"
        transcript_data: Dictionary containing conversation data
        
    Returns:
        Document ID if successful, None otherwise
    """
    client = get_mongo_client(connection_string)
    db_name = get_database_name()
    db = getattr(client, db_name)
    collection = db.audio_transcripts

    try:
        identifier = st.session_state.get("user_identifier", "anonymous")
        cohort_id = st.session_state.get("cohort_id", "PHYSIO_DEFAULT")
        
        if conversation_type == "patient":
            # Create new document for patient conversation
            document = {
                "timestamp": datetime.utcnow(),
                "identifier": identifier,
                "cohort_id": cohort_id,
                "assignment_id": st.session_state.get("assignment_id", "default"),
                "session_metadata": transcript_data.get("session_metadata", {}),
                "patient_conversation": transcript_data,
                "supervisor_conversation": {},
                "assessment_data": {}
            }
            result = collection.insert_one(document)
            return str(result.inserted_id)
        
        elif conversation_type == "supervisor" and st.session_state.get("session_id"):
            # Update existing document with supervisor conversation
            result = collection.update_one(
                {"_id": ObjectId(st.session_state.session_id)},
                {"$set": {
                    "supervisor_conversation": transcript_data,
                    "identifier": identifier,
                    "cohort_id": cohort_id
                }}
            )
            return st.session_state.session_id if result.modified_count > 0 else None
            
    except Exception as e:
        logger.error(f"Error logging {conversation_type} transcript: {e}")
        return None
    finally:
        client.close()

def get_conversation_history(connection_string: str, identifier: str, cohort_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get conversation history for a student.
    
    Args:
        connection_string: MongoDB connection string
        identifier: Student identifier
        cohort_id: Optional cohort ID for filtering
        limit: Maximum number of conversations to return
        
    Returns:
        List of conversation documents
    """
    client = get_mongo_client(connection_string)
    db_name = get_database_name()
    db = getattr(client, db_name)
    
    try:
        query = {"identifier": identifier}
        if cohort_id:
            query["cohort_id"] = cohort_id
            
        conversations = list(db.audio_transcripts.find(
            query,
            {"_id": 1, "timestamp": 1, "session_metadata": 1}
        ).sort("timestamp", -1).limit(limit))
        
        return conversations
    except Exception as e:
        logger.error(f"Error getting conversation history for {identifier}: {e}")
        return []
    finally:
        client.close()

def update_session_metadata(connection_string: str, session_id: str, metadata: Dict[str, Any]) -> bool:
    """
    Update session metadata for a conversation.
    
    Args:
        connection_string: MongoDB connection string
        session_id: Session document ID
        metadata: Metadata dictionary to update
        
    Returns:
        True if successful, False otherwise
    """
    client = get_mongo_client(connection_string)
    db_name = get_database_name()
    db = getattr(client, db_name)
    
    try:
        result = db.audio_transcripts.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"session_metadata": metadata}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating session metadata for {session_id}: {e}")
        return False
    finally:
        client.close()

def get_cohort_statistics(connection_string: str, cohort_id: str) -> Dict[str, Any]:
    """
    Get statistics for a specific cohort.
    
    Args:
        connection_string: MongoDB connection string
        cohort_id: Cohort identifier
        
    Returns:
        Dictionary containing cohort statistics
    """
    client = get_mongo_client(connection_string)
    db_name = get_database_name()
    db = getattr(client, db_name)
    
    try:
        # Count total students in cohort
        total_students = db.valid_identifiers.count_documents(
            {"cohort_id": cohort_id, "is_active": True}
        )
        
        # Count completed conversations
        completed_conversations = db.audio_transcripts.count_documents({
            "cohort_id": cohort_id,
            "supervisor_conversation": {"$ne": {}}
        })
        
        # Get average session duration
        pipeline = [
            {"$match": {"cohort_id": cohort_id}},
            {"$group": {
                "_id": None,
                "avg_duration": {"$avg": "$session_metadata.duration_seconds"},
                "avg_quality": {"$avg": "$session_metadata.audio_quality_score"}
            }}
        ]
        
        avg_stats = list(db.audio_transcripts.aggregate(pipeline))
        avg_duration = avg_stats[0].get("avg_duration", 0) if avg_stats else 0
        avg_quality = avg_stats[0].get("avg_quality", 0) if avg_stats else 0
        
        return {
            "total_students": total_students,
            "completed_conversations": completed_conversations,
            "avg_duration_seconds": avg_duration,
            "avg_quality_score": avg_quality,
            "completion_rate": (completed_conversations / total_students * 100) if total_students > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error getting cohort statistics for {cohort_id}: {e}")
        return {
            "total_students": 0,
            "completed_conversations": 0,
            "avg_duration_seconds": 0,
            "avg_quality_score": 0,
            "completion_rate": 0
        }
    finally:
        client.close()

def migrate_legacy_data(connection_string: str, legacy_db_name: str = "physiobot") -> bool:
    """
    Migrate data from legacy physiobot database to realtime database.
    
    Args:
        connection_string: MongoDB connection string
        legacy_db_name: Name of the legacy database
        
    Returns:
        True if successful, False otherwise
    """
    client = get_mongo_client(connection_string)
    legacy_db = getattr(client, legacy_db_name)
    new_db_name = get_database_name()
    new_db = getattr(client, new_db_name)
    
    try:
        # Create default cohort for legacy data
        default_cohort = {
            "cohort_id": "PHYSIO_LEGACY",
            "cohort_name": "Legacy Cohort",
            "academic_year": "2024",
            "semester": "Migration",
            "instructor_emails": [],
            "created_at": datetime.utcnow(),
            "is_active": True,
            "settings": {}
        }
        
        new_db.cohorts.update_one(
            {"cohort_id": "PHYSIO_LEGACY"},
            {"$setOnInsert": default_cohort},
            upsert=True
        )
        
        # Migrate valid_identifiers
        legacy_identifiers = list(legacy_db.valid_identifiers.find({}))
        for identifier_doc in legacy_identifiers:
            identifier_doc["cohort_id"] = "PHYSIO_LEGACY"
            identifier_doc["is_active"] = True
            if "student_metadata" not in identifier_doc:
                identifier_doc["student_metadata"] = {}
            
        if legacy_identifiers:
            new_db.valid_identifiers.insert_many(legacy_identifiers)
            logger.info(f"Migrated {len(legacy_identifiers)} identifiers")
        
        # Note: Legacy transcripts would need custom migration logic
        # based on the specific structure differences
        
        return True
        
    except Exception as e:
        logger.error(f"Error migrating legacy data: {e}")
        return False
    finally:
        client.close()