# Test Login Codes for Physiotherapy Bot

This document explains how to create and use test login codes for the Physiotherapy Bot authentication system.

## Quick Start

### Option 1: Use Pre-generated Test Codes
You can immediately use these pre-generated test codes:

- `TEST1`, `TEST2`, `TEST3` - Basic test codes
- `DEMO1`, `DEMO2` - Demo codes
- `ADMIN` - Admin test code
- `USER1`, `USER2` - User test codes
- `GUEST` - Guest test code
- `DEV01` - Developer test code

### Option 2: Generate New Test Codes
Use the script to generate custom test codes:

```bash
# Generate 10 test codes (default)
python scripts/create_test_login_codes.py

# Generate 5 test codes
python scripts/create_test_login_codes.py --num-codes 5

# Generate 20 test codes with custom filename
python scripts/create_test_login_codes.py --num-codes 20 --output-file my_test_codes.csv

# Generate and automatically load to MongoDB
python scripts/create_test_login_codes.py --num-codes 10 --load-mongodb
```

## Loading Test Codes into MongoDB

### Method 1: Using the Test Code Script
```bash
python scripts/create_test_login_codes.py --load-mongodb
```

### Method 2: Using the Load Identifiers Script
```bash
python scripts/load_identifiers.py
# Then enter the path to your CSV file when prompted
```

### Method 3: Manual CSV Loading
1. Create a CSV file with a column named `identifier`
2. Run the load script:
   ```bash
   python scripts/load_identifiers.py
   ```

## CSV File Format

Your CSV file should have this structure:
```csv
identifier,test_type,created_at,description
TEST1,test,2024-12-19 10:00:00,Test code 1
TEST2,test,2024-12-19 10:00:00,Test code 2
```

## Using Test Codes

1. **Start the Physiotherapy Bot application**
2. **Enter any of the test codes** in the login field
3. **The system will authenticate** you and grant access to the bot features

## Environment Setup

Make sure you have the required environment variables set:

```bash
# In your .env file or environment
MONGODB_CONNECTION_STRING=your_mongodb_connection_string
```

## Database Structure

Test codes are stored in MongoDB with this structure:
```json
{
  "identifier": "TEST1",
  "is_active": true,
  "created_at": "2024-12-19T10:00:00Z",
  "test_code": true,
  "description": "Test code 1"
}
```

## Security Notes

- Test codes are for development and testing only
- They should not be used in production
- Test codes are clearly marked in the database
- You can easily identify and remove test codes later

## Troubleshooting

### Code Not Working
1. Check if the code exists in the `valid_identifiers` collection
2. Verify the MongoDB connection string
3. Ensure the code is marked as `is_active: true`

### MongoDB Connection Issues
1. Verify your `MONGODB_CONNECTION_STRING` environment variable
2. Check network connectivity to MongoDB
3. Ensure the database and collection exist

### Script Errors
1. Install required dependencies: `pip install pandas pymongo python-dotenv`
2. Check Python version compatibility
3. Verify file permissions on the script

## Examples

### Generate 5 Random Test Codes
```bash
python scripts/create_test_login_codes.py --num-codes 5
```

### Load Pre-generated Codes to MongoDB
```bash
python scripts/load_identifiers.py
# Enter: test_codes_manual.csv
```

### Generate and Load 15 Test Codes
```bash
python scripts/create_test_login_codes.py --num-codes 15 --load-mongodb
```

## Files Created

- `test_login_codes.csv` - Generated test codes
- `test_codes_manual.csv` - Pre-generated test codes
- `scripts/create_test_login_codes.py` - Test code generator script 