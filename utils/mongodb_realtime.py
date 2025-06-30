import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

class MongoDBRealtimeClient:
    def __init__(self, mongodb_uri: str, database_name: str = "physiobot-realtime"):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        
    def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.database = self.client[self.database_name]
            # Test connection
            self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
    
    def log_audio_transcript(
        self, 
        identifier: str, 
        conversation_type: str,  # "patient" or "supervisor"
        conversation_data: Dict[str, Any],
        session_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Log audio conversation transcript to MongoDB"""
        
        if not self.database:
            print("Database not connected")
            return None
            
        try:
            # Prepare document structure
            document = {
                "timestamp": datetime.utcnow(),
                "identifier": identifier,
                "conversation_type": conversation_type,
                "session_metadata": session_metadata or {
                    "duration_seconds": conversation_data.get("duration_seconds", 0),
                    "audio_quality_score": 0.0,
                    "connection_stability": 0.0,
                    "browser_info": "Unknown",
                    "device_info": "Unknown"
                }
            }
            
            # Process conversation history into transcript segments
            transcript_segments = []
            conversation_history = conversation_data.get("conversation_history", [])
            
            for item in conversation_history:
                segment = {
                    "timestamp": item.get("timestamp", datetime.utcnow()),
                    "speaker": item.get("speaker", "unknown"),
                    "text": item.get("text", ""),
                    "confidence": 1.0,  # Default confidence
                    "audio_quality": 1.0,  # Default audio quality
                    "response_number": item.get("response_number", 0)
                }
                transcript_segments.append(segment)
            
            # Calculate conversation metrics
            user_segments = [s for s in transcript_segments if s["speaker"] == "user"]
            assistant_segments = [s for s in transcript_segments if s["speaker"] == "assistant"]
            
            conversation_metrics = {
                "student_speaking_time": len(user_segments),  # Simplified metric
                "patient_speaking_time": len(assistant_segments),  # Simplified metric
                "average_response_time": 0.0,  # Would need timestamp analysis
                "interruptions_count": 0,  # Would need audio analysis
                "total_exchanges": len(transcript_segments)
            }
            
            # Add conversation-specific data
            if conversation_type == "patient":
                document["patient_conversation"] = {
                    "audio_duration": conversation_data.get("duration_seconds", 0),
                    "transcript_segments": transcript_segments,
                    "conversation_metrics": conversation_metrics,
                    "final_transcript": conversation_data.get("final_transcript", {}),
                    "response_count": conversation_data.get("response_count", 0)
                }
            elif conversation_type == "supervisor":
                document["supervisor_conversation"] = {
                    "audio_duration": conversation_data.get("duration_seconds", 0),
                    "transcript_segments": transcript_segments,
                    "conversation_metrics": conversation_metrics,
                    "final_transcript": conversation_data.get("final_transcript", {}),
                    "response_count": conversation_data.get("response_count", 0)
                }
            
            # Add assessment data placeholder
            document["assessment_data"] = {
                "communication_scores": {},
                "audio_quality_feedback": "",
                "technical_issues": []
            }
            
            # Insert into collection
            collection = self.database["audio_transcripts"]
            result = collection.insert_one(document)
            
            print(f"Audio transcript logged with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error logging audio transcript: {e}")
            return None
    
    def get_audio_transcript(self, identifier: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve audio transcript by identifier and optional session ID"""
        
        if not self.database:
            return None
            
        try:
            collection = self.database["audio_transcripts"]
            
            # Build query
            query = {"identifier": identifier}
            if session_id:
                query["_id"] = session_id
            
            # Get the most recent transcript for this identifier
            result = collection.find_one(query, sort=[("timestamp", -1)])
            
            if result:
                # Convert ObjectId to string
                result["_id"] = str(result["_id"])
                return result
            
            return None
            
        except Exception as e:
            print(f"Error retrieving audio transcript: {e}")
            return None
    
    def update_audio_transcript(
        self, 
        session_id: str, 
        conversation_type: str,
        conversation_data: Dict[str, Any]
    ) -> bool:
        """Update existing audio transcript with additional conversation data"""
        
        if not self.database:
            return False
            
        try:
            collection = self.database["audio_transcripts"]
            
            # Process conversation data similar to log_audio_transcript
            transcript_segments = []
            conversation_history = conversation_data.get("conversation_history", [])
            
            for item in conversation_history:
                segment = {
                    "timestamp": item.get("timestamp", datetime.utcnow()),
                    "speaker": item.get("speaker", "unknown"),
                    "text": item.get("text", ""),
                    "confidence": 1.0,
                    "audio_quality": 1.0,
                    "response_number": item.get("response_number", 0)
                }
                transcript_segments.append(segment)
            
            # Calculate metrics
            user_segments = [s for s in transcript_segments if s["speaker"] == "user"]
            assistant_segments = [s for s in transcript_segments if s["speaker"] == "assistant"]
            
            conversation_metrics = {
                "student_speaking_time": len(user_segments),
                "patient_speaking_time": len(assistant_segments),
                "average_response_time": 0.0,
                "interruptions_count": 0,
                "total_exchanges": len(transcript_segments)
            }
            
            # Prepare update data
            update_data = {
                f"{conversation_type}_conversation": {
                    "audio_duration": conversation_data.get("duration_seconds", 0),
                    "transcript_segments": transcript_segments,
                    "conversation_metrics": conversation_metrics,
                    "final_transcript": conversation_data.get("final_transcript", {}),
                    "response_count": conversation_data.get("response_count", 0)
                }
            }
            
            # Update document
            from bson import ObjectId
            result = collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating audio transcript: {e}")
            return False
    
    def get_user_transcripts(self, identifier: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transcripts for a user"""
        
        if not self.database:
            return []
            
        try:
            collection = self.database["audio_transcripts"]
            
            cursor = collection.find(
                {"identifier": identifier}
            ).sort("timestamp", -1).limit(limit)
            
            transcripts = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                transcripts.append(doc)
            
            return transcripts
            
        except Exception as e:
            print(f"Error retrieving user transcripts: {e}")
            return []
    
    def validate_identifier(self, identifier: str) -> bool:
        """Validate if identifier exists in valid_identifiers collection"""
        
        if not self.database:
            return False
            
        try:
            collection = self.database["valid_identifiers"]
            result = collection.find_one({"identifier": identifier})
            return result is not None
            
        except Exception as e:
            print(f"Error validating identifier: {e}")
            return False
    
    def log_session_metadata(
        self, 
        session_id: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """Log additional session metadata"""
        
        if not self.database:
            return False
            
        try:
            collection = self.database["audio_transcripts"]
            
            from bson import ObjectId
            result = collection.update_one(
                {"_id": ObjectId(session_id)},
                {"$set": {"session_metadata": metadata}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error logging session metadata: {e}")
            return False
    
    def get_conversation_analytics(self, identifier: str) -> Dict[str, Any]:
        """Get conversation analytics for a user"""
        
        if not self.database:
            return {}
            
        try:
            collection = self.database["audio_transcripts"]
            
            # Aggregate user's conversation data
            pipeline = [
                {"$match": {"identifier": identifier}},
                {"$group": {
                    "_id": "$identifier",
                    "total_sessions": {"$sum": 1},
                    "total_duration": {"$sum": "$session_metadata.duration_seconds"},
                    "avg_duration": {"$avg": "$session_metadata.duration_seconds"},
                    "avg_audio_quality": {"$avg": "$session_metadata.audio_quality_score"}
                }}
            ]
            
            result = list(collection.aggregate(pipeline))
            
            if result:
                return result[0]
            
            return {
                "total_sessions": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "avg_audio_quality": 0
            }
            
        except Exception as e:
            print(f"Error getting conversation analytics: {e}")
            return {}

# Utility functions for backward compatibility
def get_mongo_client(mongodb_uri: str) -> MongoDBRealtimeClient:
    """Get MongoDB client instance"""
    client = MongoDBRealtimeClient(mongodb_uri)
    client.connect()
    return client

def log_audio_transcript(
    mongodb_uri: str,
    conversation_type: str,
    conversation_data: Dict[str, Any],
    identifier: str = None
) -> Optional[str]:
    """Log audio transcript - backward compatibility function"""
    client = get_mongo_client(mongodb_uri)
    
    if not identifier:
        identifier = "unknown"
    
    try:
        return client.log_audio_transcript(identifier, conversation_type, conversation_data)
    finally:
        client.disconnect()