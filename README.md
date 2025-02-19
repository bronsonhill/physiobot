# Physiotherapy Bot

An interactive learning tool for physiotherapy students to practice patient consultations and receive expert feedback.

## Overview

This application provides a simulated environment for physiotherapy students to:
1. Conduct mock patient interviews (Activity 1)
2. Receive detailed feedback from an AI supervisor (Activity 2)

The system uses AI to simulate both a patient with specific conditions and a supervisor who evaluates the student's communication skills and assessment techniques.

## Features

- **AI Patient Simulation**: Interact with a virtual patient presenting with hip pain and various comorbidities
- **Real-time Feedback**: Get expert supervision on your consultation skills
- **Communication Assessment**: Evaluation of:
  - Open-ended questioning
  - Restatement and paraphrasing
  - Emotional reflection
  - Clarification techniques
  - Professional tone and language

## Setup

1. Install dependencies:
```bash
pip install streamlit openai
```

2. Set up your OpenAI API key in your environment variables:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

3. Run the application:
```bash
streamlit run Home.py
```

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

## License

This project is for educational purposes. Please ensure you have appropriate licenses for any AI models used.