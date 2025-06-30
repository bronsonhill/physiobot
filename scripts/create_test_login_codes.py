#!/usr/bin/env python3
"""
Test Login Code Generator for Physiotherapy Bot

This script generates test login codes (identifiers) for testing purposes.
It creates a CSV file with test codes and optionally loads them into MongoDB.
"""

import pandas as pd
import random
import string
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_test_identifier():
    """Generate a random 5-character identifier for testing."""
    # Use uppercase letters and numbers for better readability
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(5))

def create_test_codes(num_codes=10, output_file="test_login_codes.csv"):
    """
    Create test login codes and save to CSV file.
    
    Args:
        num_codes: Number of test codes to generate
        output_file: Output CSV file path
    """
    # Generate unique test codes
    codes = set()
    while len(codes) < num_codes:
        codes.add(generate_test_identifier())
    
    # Create DataFrame
    df = pd.DataFrame({
        'identifier': list(codes),
        'test_type': ['test'] * len(codes),
        'created_at': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * len(codes),
        'description': [f'Test code {i+1}' for i in range(len(codes))]
    })
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    logging.info(f"Generated {len(codes)} test codes and saved to {output_file}")
    
    # Display the codes
    print(f"\n{'='*50}")
    print(f"TEST LOGIN CODES ({len(codes)} codes)")
    print(f"{'='*50}")
    for i, code in enumerate(codes, 1):
        print(f"{i:2d}. {code}")
    print(f"{'='*50}")
    
    return df

def load_codes_to_mongodb(csv_file, connection_string):
    """
    Load test codes from CSV into MongoDB.
    
    Args:
        csv_file: Path to CSV file with identifiers
        connection_string: MongoDB connection string
    """
    try:
        from pymongo import MongoClient
        from pymongo.server_api import ServerApi
        
        # Read CSV
        df = pd.read_csv(csv_file)
        
        # Connect to MongoDB
        client = MongoClient(connection_string, server_api=ServerApi('1'))
        db = client.physiobot_realtime
        collection = db.valid_identifiers
        
        # Prepare documents
        documents = []
        for _, row in df.iterrows():
            documents.append({
                "identifier": row['identifier'],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "test_code": True,
                "description": row.get('description', 'Test code')
            })
        
        # Insert documents
        if documents:
            collection.insert_many(documents)
            logging.info(f"Successfully loaded {len(documents)} test codes into MongoDB")
            return True
        else:
            logging.warning("No codes to load")
            return False
            
    except Exception as e:
        logging.error(f"Error loading codes to MongoDB: {str(e)}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def main():
    parser = argparse.ArgumentParser(description='Generate test login codes for Physiotherapy Bot')
    parser.add_argument('--num-codes', type=int, default=10, 
                       help='Number of test codes to generate (default: 10)')
    parser.add_argument('--output-file', default='test_login_codes.csv',
                       help='Output CSV file path (default: test_login_codes.csv)')
    parser.add_argument('--load-mongodb', action='store_true',
                       help='Load codes into MongoDB after generation')
    parser.add_argument('--mongodb-uri', 
                       help='MongoDB connection string (overrides environment variable)')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    mongodb_uri = args.mongodb_uri or os.getenv("MONGODB_CONNECTION_STRING")
    
    if args.load_mongodb and not mongodb_uri:
        logging.error("MongoDB connection string required when --load-mongodb is used")
        logging.error("Set MONGODB_CONNECTION_STRING environment variable or use --mongodb-uri")
        return
    
    # Generate test codes
    df = create_test_codes(args.num_codes, args.output_file)
    
    # Load to MongoDB if requested
    if args.load_mongodb:
        print(f"\nLoading codes to MongoDB...")
        success = load_codes_to_mongodb(args.output_file, mongodb_uri)
        if success:
            print("✅ Test codes successfully loaded to MongoDB!")
        else:
            print("❌ Failed to load codes to MongoDB")
    
    print(f"\n📁 Test codes saved to: {args.output_file}")
    print("💡 You can now use these codes to test the Physiotherapy Bot login system")

if __name__ == "__main__":
    main() 