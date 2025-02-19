# Physiotherapy Bot

An interactive learning platform for physiotherapy students to practice patient assessments and receive supervisor feedback using AI.

## Overview

This application consists of two main components:
1. A simulated patient conversation where students can practice their subjective assessment skills
2. A simulated supervisor conversation where students receive feedback on their patient interaction

### How It Works

1. Students log in using their unique identifier
2. They conduct a subjective assessment with an AI patient
3. After completing the patient conversation, they can discuss their performance with an AI supervisor
4. All conversations are saved to MongoDB for review

## Features

- **AI Patient Simulation**: Interact with a virtual patient presenting with hip pain and various comorbidities
- **Real-time Feedback**: Get expert supervision on your consultation skills
- **Communication Assessment**: Evaluation of:
  - Open-ended questioning
  - Restatement and paraphrasing
  - Emotional reflection
  - Clarification techniques
  - Professional tone and language

## Setup Instructions

### 1. Environment Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install requirements:
```bash
pip install -r requirements.txt
```

### 2. Configuration

1. Create a `.env` file in the project root with the following:
```properties
OPENAI_API_KEY=your_openai_api_key
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
MONGODB_CONNECTION_STRING=your_mongodb_connection_string
```

2. Create a `.streamlit/secrets.toml` file:
```toml
OPENAI_API_KEY="your_openai_api_key"
MONGODB_CONNECTION_STRING="your_mongodb_connection_string"
```

### 3. Setting Up Student Identifiers

1. Create a CSV file with student information (e.g., `students.csv`):
```csv
student_id,email,name
12345,student1@example.com,John Doe
12346,student2@example.com,Jane Smith
```

2. Generate identifiers and load them into MongoDB:
```bash
python scripts/generate_and_load_identifiers.py
```

3. The script will:
   - Generate unique identifiers for each student
   - Save a new CSV with the mappings (keep this secure!)
   - Upload only the identifiers to MongoDB

### 4. Running the Application

1. Start the Streamlit app:
```bash
streamlit run Home.py
```

2. Access the application at `http://localhost:8501`

## Usage

1. Start with Activity 1 - Patient Consultation
   - Practice taking a patient history
   - Use appropriate communication techniques
   - Gather relevant clinical information

2. Proceed to Activity 2 - Supervisor Feedback
   - Receive detailed feedback on your performance
   - Get suggestions for improvement
   - Review missed key clinical domains

## Educational Framework

The system evaluates students based on the WOCCSNOR framework:
- Where (pain location)
- Other sites
- Constant/Intermittent
- Severity
- Superficial/Deep
- Nature
- Other symptoms
- Referral

## Project Structure

```
physiobot/
├── Home.py                 # Main application entry point
├── pages/
│   ├── 1_Patient_Conversation.py    # Patient simulation
│   └── 2_Supervisor_Conversation.py # Supervisor feedback
├── utils/
│   └── mongodb.py         # Database utilities
├── scripts/
│   └── generate_and_load_identifiers.py # Identifier management
└── prompts/
    ├── pprompt.txt       # Patient conversation prompt
    └── supervisorprompt.txt # Supervisor conversation prompt
```

## Security Considerations

1. Never commit `.env` or `secrets.toml` files
2. Keep the CSV with student-identifier mappings secure
3. Only identifiers are stored in MongoDB, no personal information
4. Regular database backups are recommended

## Troubleshooting

1. Invalid Identifier:
   - Ensure the identifier was generated using the provided script
   - Check MongoDB connection
   - Verify the identifier in the valid_identifiers collection

2. Connection Issues:
   - Verify MongoDB connection string
   - Check internet connection
   - Ensure OpenAI API key is valid

3. Missing Conversations:
   - Check MongoDB connection
   - Verify the conversation was properly finished using the "Finish Conversation" button

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

[Insert your license information here]