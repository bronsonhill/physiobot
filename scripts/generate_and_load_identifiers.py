import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import hashlib
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_mongo_client(connection_string):
    return MongoClient(connection_string, server_api=ServerApi('1'))

def generate_identifier(row, salt):
    """Generate a unique identifier based on student information."""
    # Combine all available fields with a salt for uniqueness
    combined = ""
    for value in row.values:
        if pd.notna(value):
            combined += str(value)
    combined += salt
    
    # Create a hash and take first 8 characters
    hash_object = hashlib.sha256(combined.encode())
    return f"PHYSIO{hash_object.hexdigest()[:8].upper()}"

def process_and_load_identifiers(input_csv_path, connection_string):
    """
    1. Read student data
    2. Generate identifiers
    3. Save new CSV with identifiers
    4. Upload only identifiers to MongoDB
    """
    try:
        # Read CSV file
        df = pd.read_csv(input_csv_path)
        
        # Generate a random salt for this batch
        salt = str(uuid.uuid4())
        
        # Generate identifiers
        df['identifier'] = df.apply(lambda row: generate_identifier(row, salt), axis=1)
        
        # Save new CSV with identifiers
        output_path = input_csv_path.rsplit('.', 1)[0] + '_with_identifiers.csv'
        df.to_csv(output_path, index=False)
        logging.info(f"Saved CSV with identifiers to: {output_path}")

        # Connect to MongoDB and upload only the identifiers
        client = get_mongo_client(connection_string)
        db = client.physiobot
        collection = db.valid_identifiers

        # Clear existing identifiers if needed
        should_clear = input("Clear existing identifiers? (y/n): ").lower() == 'y'
        if should_clear:
            collection.delete_many({})
            logging.info("Cleared existing identifiers")

        # Prepare documents (only identifiers, no personal data)
        documents = [
            {
                "identifier": identifier,
                "created_at": datetime.utcnow()
            }
            for identifier in df['identifier'].unique()
        ]

        # Insert documents
        if documents:
            collection.insert_many(documents)
            logging.info(f"Successfully loaded {len(documents)} identifiers into MongoDB")
            
            # Print example mappings for verification
            logging.info("\nExample identifier mappings (first 5):")
            for _, row in df.head().iterrows():
                logging.info(f"Student info -> Identifier: {row['identifier']}")
        else:
            logging.warning("No valid identifiers generated")

    except Exception as e:
        logging.error(f"Error processing identifiers: {str(e)}")
        raise
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("MONGODB_CONNECTION_STRING not found in environment variables")

    # Get CSV path
    csv_path = input("Enter path to CSV file containing student information: ").strip()
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    process_and_load_identifiers(csv_path, connection_string)
