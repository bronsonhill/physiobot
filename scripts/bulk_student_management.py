"""
Bulk student management for physiobot-realtime system.
Handles loading, transferring, and managing students across cohorts.
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Add the parent directory to sys.path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mongodb_realtime import get_mongo_client, get_database_name
from utils.config_manager import ConfigManager
from utils.cohort_config_manager import CohortConfigManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BulkStudentManager:
    """Manager for bulk student operations."""
    
    def __init__(self, connection_string: str):
        """
        Initialize bulk student manager.
        
        Args:
            connection_string: MongoDB connection string
        """
        self.connection_string = connection_string
        self.config_manager = ConfigManager()
        self.cohort_manager = CohortConfigManager(connection_string)
        self.db_name = get_database_name()
    
    def generate_identifier(self, row: pd.Series) -> str:
        """
        Generate a unique identifier for a student.
        
        Args:
            row: Pandas series containing student data
            
        Returns:
            Generated identifier string
        """
        # This is a simplified version - in production, you might want more sophisticated logic
        if 'student_id' in row and pd.notna(row['student_id']):
            return str(row['student_id']).upper().strip()
        elif 'email' in row and pd.notna(row['email']):
            return row['email'].split('@')[0].upper().strip()
        else:
            # Generate based on name if available
            if 'first_name' in row and 'last_name' in row:
                first = str(row['first_name']).strip()[:3].upper()
                last = str(row['last_name']).strip()[:5].upper()
                return f"{first}{last}{datetime.now().strftime('%m%d')}"
            else:
                # Fallback to timestamp-based identifier
                return f"STU{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def load_cohort_students(self, csv_path: str, cohort_id: str, clear_existing: bool = False) -> bool:
        """
        Load students for specific cohort from CSV file.
        
        Args:
            csv_path: Path to CSV file containing student data
            cohort_id: Target cohort identifier
            clear_existing: Whether to clear existing students in cohort
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate cohort exists
            cohorts = self.cohort_manager.get_active_cohorts()
            if not any(c['cohort_id'] == cohort_id for c in cohorts):
                logger.error(f"Cohort {cohort_id} does not exist")
                return False
            
            # Read CSV file
            if not os.path.exists(csv_path):
                logger.error(f"CSV file not found: {csv_path}")
                return False
            
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV with {len(df)} rows")
            
            # Validate required columns (flexible - can work with different CSV formats)
            logger.info(f"CSV columns: {list(df.columns)}")
            
            # Clear existing students if requested
            if clear_existing:
                self._clear_cohort_students(cohort_id)
            
            # Process students
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.db_name)
            
            documents = []
            for index, row in df.iterrows():
                try:
                    # Generate identifier if not provided
                    if 'identifier' in row and pd.notna(row['identifier']):
                        identifier = str(row['identifier']).strip()
                    else:
                        identifier = self.generate_identifier(row)
                    
                    # Add cohort prefix to ensure uniqueness across cohorts
                    full_identifier = f"{cohort_id}_{identifier}"
                    
                    # Build student metadata
                    student_metadata = {}
                    if 'student_id' in row and pd.notna(row['student_id']):
                        student_metadata['student_id'] = str(row['student_id'])
                    if 'year_level' in row and pd.notna(row['year_level']):
                        student_metadata['year_level'] = str(row['year_level'])
                    if 'program' in row and pd.notna(row['program']):
                        student_metadata['program'] = str(row['program'])
                    if 'first_name' in row and pd.notna(row['first_name']):
                        student_metadata['first_name'] = str(row['first_name'])
                    if 'last_name' in row and pd.notna(row['last_name']):
                        student_metadata['last_name'] = str(row['last_name'])
                    if 'email' in row and pd.notna(row['email']):
                        student_metadata['email'] = str(row['email'])
                    
                    document = {
                        "identifier": full_identifier,
                        "cohort_id": cohort_id,
                        "student_metadata": student_metadata,
                        "created_at": datetime.utcnow(),
                        "is_active": True,
                        "assignment_attempts": 0,
                        "last_access": None
                    }
                    
                    documents.append(document)
                    
                except Exception as e:
                    logger.warning(f"Error processing row {index}: {e}")
                    continue
            
            # Insert documents
            if documents:
                try:
                    result = db.valid_identifiers.insert_many(documents, ordered=False)
                    logger.info(f"Successfully loaded {len(result.inserted_ids)} students into cohort {cohort_id}")
                    
                    # Log some sample identifiers for verification
                    sample_identifiers = [doc['identifier'] for doc in documents[:5]]
                    logger.info(f"Sample identifiers: {sample_identifiers}")
                    
                    return True
                except Exception as e:
                    logger.error(f"Error inserting student documents: {e}")
                    return False
            else:
                logger.warning("No valid student documents to insert")
                return False
                
        except Exception as e:
            logger.error(f"Error loading students: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    def transfer_students(self, from_cohort: str, to_cohort: str, student_identifiers: Optional[List[str]] = None) -> bool:
        """
        Transfer students between cohorts.
        
        Args:
            from_cohort: Source cohort ID
            to_cohort: Target cohort ID
            student_identifiers: Optional list of specific students to transfer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.db_name)
            
            # Build query
            query = {"cohort_id": from_cohort, "is_active": True}
            if student_identifiers:
                query["identifier"] = {"$in": student_identifiers}
            
            # Update cohort assignment
            result = db.valid_identifiers.update_many(
                query,
                {
                    "$set": {
                        "cohort_id": to_cohort,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Transferred {result.modified_count} students from {from_cohort} to {to_cohort}")
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error transferring students: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    def export_cohort_students(self, cohort_id: str, output_path: str) -> bool:
        """
        Export cohort students to CSV file.
        
        Args:
            cohort_id: Cohort identifier
            output_path: Output CSV file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.db_name)
            
            # Get students
            students = list(db.valid_identifiers.find(
                {"cohort_id": cohort_id, "is_active": True},
                {"_id": 0}
            ))
            
            if not students:
                logger.warning(f"No students found in cohort {cohort_id}")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(students)
            
            # Flatten student_metadata if it exists
            if 'student_metadata' in df.columns:
                metadata_df = pd.json_normalize(df['student_metadata'])
                df = pd.concat([df.drop('student_metadata', axis=1), metadata_df], axis=1)
            
            # Export to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {len(students)} students to {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting students: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()
    
    def get_cohort_summary(self, cohort_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a cohort.
        
        Args:
            cohort_id: Cohort identifier
            
        Returns:
            Dictionary containing cohort summary
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.db_name)
            
            # Count active students
            active_students = db.valid_identifiers.count_documents({
                "cohort_id": cohort_id,
                "is_active": True
            })
            
            # Count students with attempts
            students_with_attempts = db.valid_identifiers.count_documents({
                "cohort_id": cohort_id,
                "is_active": True,
                "assignment_attempts": {"$gt": 0}
            })
            
            # Get recent activity
            recent_access = db.valid_identifiers.count_documents({
                "cohort_id": cohort_id,
                "is_active": True,
                "last_access": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)}
            })
            
            return {
                "active_students": active_students,
                "students_with_attempts": students_with_attempts,
                "recent_activity": recent_access,
                "participation_rate": (students_with_attempts / active_students * 100) if active_students > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting cohort summary: {e}")
            return {}
        finally:
            if 'client' in locals():
                client.close()
    
    def _clear_cohort_students(self, cohort_id: str) -> bool:
        """
        Clear all students from a cohort (soft delete).
        
        Args:
            cohort_id: Cohort identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            client = get_mongo_client(self.connection_string)
            db = getattr(client, self.db_name)
            
            result = db.valid_identifiers.update_many(
                {"cohort_id": cohort_id},
                {
                    "$set": {
                        "is_active": False,
                        "deactivated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Deactivated {result.modified_count} students from cohort {cohort_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cohort students: {e}")
            return False
        finally:
            if 'client' in locals():
                client.close()

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bulk student management for physiobot-realtime")
    parser.add_argument("action", choices=["load", "transfer", "export", "summary"], help="Action to perform")
    parser.add_argument("--csv", help="CSV file path for load/export operations")
    parser.add_argument("--cohort", required=True, help="Cohort ID")
    parser.add_argument("--target-cohort", help="Target cohort ID for transfer operations")
    parser.add_argument("--clear", action="store_true", help="Clear existing students before loading")
    parser.add_argument("--output", help="Output file path for export operations")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    if not connection_string:
        logger.error("MONGODB_CONNECTION_STRING not found in environment variables")
        return False
    
    manager = BulkStudentManager(connection_string)
    
    try:
        if args.action == "load":
            if not args.csv:
                logger.error("--csv parameter required for load operation")
                return False
            result = manager.load_cohort_students(args.csv, args.cohort, args.clear)
            
        elif args.action == "transfer":
            if not args.target_cohort:
                logger.error("--target-cohort parameter required for transfer operation")
                return False
            result = manager.transfer_students(args.cohort, args.target_cohort)
            
        elif args.action == "export":
            output_path = args.output or f"{args.cohort}_students.csv"
            result = manager.export_cohort_students(args.cohort, output_path)
            
        elif args.action == "summary":
            summary = manager.get_cohort_summary(args.cohort)
            print(f"Cohort {args.cohort} Summary:")
            for key, value in summary.items():
                print(f"  {key}: {value}")
            result = True
        
        return result
        
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)