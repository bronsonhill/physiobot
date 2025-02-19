from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime
import streamlit as st

def get_mongo_client(connection_string):
    return MongoClient(connection_string, server_api=ServerApi('1'))

def check_identifier(connection_string, identifier):
    """Check if the identifier exists in the valid_identifiers collection."""
    client = get_mongo_client(connection_string)
    db = client.physiobot
    try:
        result = db.valid_identifiers.find_one({"identifier": identifier})
        return bool(result)
    finally:
        client.close()

def log_transcript(connection_string, conversation_type, messages):
    client = get_mongo_client(connection_string)
    db = client.physiobot
    collection = db.transcripts

    try:
        if conversation_type == "patient":
            # Create new document for patient conversation
            document = {
                "timestamp": datetime.utcnow(),
                "patient_messages": messages,
                "supervisor_messages": [],
                "identifier": st.session_state.get("user_identifier", "anonymous")
            }
            result = collection.insert_one(document)
            return str(result.inserted_id)
        
        elif conversation_type == "supervisor" and st.session_state.get("session_id"):
            # Update existing document with supervisor messages
            collection.update_one(
                {"_id": ObjectId(st.session_state.session_id)},
                {"$set": {
                    "supervisor_messages": messages,
                    "identifier": st.session_state.get("user_identifier", "anonymous")
                }}
            )
    finally:
        client.close()
