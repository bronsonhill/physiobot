from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime, timedelta
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

def get_database_stats() -> Dict[str, Any]:
    """
    Get overall database statistics for the admin dashboard.
    
    Returns:
        Dictionary containing database statistics
    """
    try:
        connection_string = st.session_state.get("mongodb_uri")
        if not connection_string:
            return {"error": "No database connection"}
            
        client = get_mongo_client(connection_string)
        db_name = get_database_name()
        db = getattr(client, db_name)
        
        # Total sessions
        total_sessions = db.audio_transcripts.count_documents({})
        
        # Active users in last 24 hours
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        active_users_24h = db.audio_transcripts.distinct("identifier", {
            "timestamp": {"$gte": twenty_four_hours_ago}
        })
        
        # Average session duration
        pipeline = [
            {"$match": {"session_metadata.duration_seconds": {"$exists": True}}},
            {"$group": {
                "_id": None,
                "avg_duration": {"$avg": "$session_metadata.duration_seconds"},
                "total_completed": {"$sum": 1}
            }}
        ]
        
        duration_stats = list(db.audio_transcripts.aggregate(pipeline))
        avg_duration = duration_stats[0].get("avg_duration", 0) if duration_stats else 0
        total_completed = duration_stats[0].get("total_completed", 0) if duration_stats else 0
        
        # Success rate (sessions with both patient and supervisor conversations)
        successful_sessions = db.audio_transcripts.count_documents({
            "supervisor_conversation": {"$ne": {}}
        })
        
        success_rate = (successful_sessions / total_sessions) if total_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "active_users_24h": len(active_users_24h),
            "avg_session_duration": avg_duration,
            "success_rate": success_rate,
            "completed_sessions": total_completed,
            "successful_sessions": successful_sessions
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {
            "total_sessions": 0,
            "active_users_24h": 0,
            "avg_session_duration": 0,
            "success_rate": 0,
            "completed_sessions": 0,
            "successful_sessions": 0,
            "error": str(e)
        }
    finally:
        if 'client' in locals():
            client.close()

def get_recent_sessions(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get recent session data for the admin dashboard.
    
    Args:
        limit: Maximum number of sessions to return
        
    Returns:
        List of recent session documents
    """
    try:
        connection_string = st.session_state.get("mongodb_uri")
        if not connection_string:
            return []
            
        client = get_mongo_client(connection_string)
        db_name = get_database_name()
        db = getattr(client, db_name)
        
        # Get recent sessions with relevant fields
        sessions = list(db.audio_transcripts.find(
            {},
            {
                "timestamp": 1,
                "identifier": 1,
                "session_metadata.duration_seconds": 1,
                "patient_conversation.conversation_metrics.total_exchanges": 1,
                "supervisor_conversation": 1
            }
        ).sort("timestamp", -1).limit(limit))
        
        # Format sessions for display
        formatted_sessions = []
        for session in sessions:
            session_duration = session.get("session_metadata", {}).get("duration_seconds", 0)
            total_exchanges = session.get("patient_conversation", {}).get("conversation_metrics", {}).get("total_exchanges", 0)
            
            # Determine status
            if session.get("supervisor_conversation"):
                status = "Completed"
            elif session.get("patient_conversation"):
                status = "In Progress"
            else:
                status = "Started"
            
            formatted_sessions.append({
                "_id": str(session["_id"]),
                "timestamp": session.get("timestamp"),
                "identifier": session.get("identifier", "Unknown"),
                "session_duration": session_duration,
                "total_exchanges": total_exchanges,
                "status": status
            })
        
        return formatted_sessions
        
    except Exception as e:
        logger.error(f"Error getting recent sessions: {e}")
        return []
    finally:
        if 'client' in locals():
            client.close()

def get_system_health() -> Dict[str, Any]:
    """
    Check system health status for monitoring.
    
    Returns:
        Dictionary containing system health information
    """
    try:
        connection_string = st.session_state.get("mongodb_uri")
        health_status = {
            "database": "unknown",
            "openai_api": "unknown",
            "audio_service": "unknown",
            "overall": "unknown"
        }
        
        # Test database connection
        try:
            client = get_mongo_client(connection_string)
            db_name = get_database_name()
            db = getattr(client, db_name)
            # Simple ping test
            db.command("ping")
            health_status["database"] = "healthy"
            client.close()
        except Exception as e:
            health_status["database"] = f"error: {str(e)}"
        
        # Test OpenAI API (basic check)
        try:
            # This would be a real API health check
            # For now, just check if API key exists
            openai_key = st.secrets.get("OPENAI_API_KEY")
            if openai_key:
                health_status["openai_api"] = "available"
            else:
                health_status["openai_api"] = "error: no API key"
        except Exception as e:
            health_status["openai_api"] = f"error: {str(e)}"
        
        # Audio service health (mock for now)
        health_status["audio_service"] = "available"
        
        # Overall health
        healthy_services = sum(1 for status in health_status.values() 
                             if status in ["healthy", "available"])
        total_services = len(health_status) - 1  # Exclude 'overall'
        
        if healthy_services == total_services:
            health_status["overall"] = "healthy"
        elif healthy_services > total_services / 2:
            health_status["overall"] = "degraded"
        else:
            health_status["overall"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return {
            "database": "error",
            "openai_api": "error", 
            "audio_service": "error",
            "overall": "error"
        }