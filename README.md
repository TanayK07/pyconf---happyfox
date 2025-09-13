# Intelligent Support Ticket Assignment System
PyCon25 Hackathon Project

## Overview
An intelligent system that automatically assigns support tickets to the most suitable agents based on skills, workload, and priority.

## Features
- Automatic skill extraction from ticket descriptions
- Priority-based assignment with business impact analysis
- Fair workload distribution across agents
- Skill gap identification and recommendations
- Comprehensive assignment rationale

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pycon25-hackathon

# Install dependencies (optional - only for ML features)
pip install -r requirements.txt

# Run the system
python run_system.py --input dataset.json --output output_result.json

# Run with ML enhancement (requires scikit-learn)
python run_system.py --ml-enhanced
```

## Quick Start

Basic usage:
```bash
python ticket_assignment_system.py
```

With custom configuration:
```bash
python run_system.py --input dataset.json --output output_result.json --config config.json
```

## Project Structure

```
pycon25-hackathon/
├── dataset.json                 # Input data (agents and tickets)
├── ticket_assignment_system.py  # Core assignment engine
├── ml_ticket_classifier.py      # ML-enhanced classification (optional)
├── utils.py                     # Utility functions
├── run_system.py               # Main execution script
├── test_system.py              # Test suite
├── config.json                 # Configuration file
├── requirements.txt            # Dependencies (optional)
└── README.md                   # This file
```

## Output Format

The system generates a JSON file with:
- Ticket assignments with agent details
- Priority scores and business impact
- Detailed assignment rationale
- Analytics and recommendations

Example output:
```json
{
  "ticket_id": "TKT-2025-001",
  "assigned_agent_id": "agent_001",
  "priority": "CRITICAL",
  "rationale": "Assigned to Sarah Chen - Strong skills in Networking (9), experienced professional"
}
```

## Algorithm

The system uses a weighted scoring algorithm:
- 40% Skill match
- 20% Experience level  
- 20% Current workload
- 20% Priority handling capability

## Testing

Run the test suite:
```bash
python test_system.py
```

## Video Demo


## Configuration

Edit `config.json` to customize:
- Maximum tickets per agent
- Skill matching weights
- Priority keywords
- SLA thresholds

## Results

The system outputs:
- `output_result.json` - Complete assignment results with analytics
- `output_result_simplified.json` - Simplified view of assignments

## License

Created for PyCon25 Hackathon

## Contact

Tanay Kedia
9101830620
