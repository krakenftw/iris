# Testing the Slack-Mem0 Integration

This directory contains tests and utilities for verifying the Slack-Mem0 integration.

## Available Test Tools

### `test_slack_mem0.py`

This script provides both automated tests and a monitoring utility for the Slack-Mem0 integration.

**Features:**
- Unit tests for Mem0Memory functionality
- Unit tests for SlackMem0Adapter
- A monitor that can listen to Slack in real-time and store messages in Mem0

**Usage:**

Run unit tests:
```bash
python tests/test_slack_mem0.py
```

Run the monitor to listen for Slack messages and store them in Mem0:
```bash
python tests/test_slack_mem0.py --monitor
```

Monitor for a specific duration (in seconds):
```bash
python tests/test_slack_mem0.py --monitor --duration 300
```

### `check_mem0_contents.py`

This utility allows you to inspect the contents of your Mem0 database.

**Features:**
- View all memories stored in Mem0
- Filter memories by query or source
- Display Slack conversations with formatting
- View tasks stored in Mem0

**Usage:**

View all memories (limited to 10 by default):
```bash
python tests/check_mem0_contents.py
```

Search for specific memories:
```bash
python tests/check_mem0_contents.py --query "project meeting"
```

Filter by source:
```bash
python tests/check_mem0_contents.py --source slack
```

Display Slack conversations:
```bash
python tests/check_mem0_contents.py --conversations
```

Display tasks:
```bash
python tests/check_mem0_contents.py --tasks
```

Adjust the number of results:
```bash
python tests/check_mem0_contents.py --limit 20
```

## Environment Setup

Before running tests, ensure you have the following environment variables configured in a `.env` file:

```
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
MEM0_API_KEY=your-mem0-api-key
```

The tests will check for these variables and skip certain tests if the required credentials are not available.

## Test Data Cleanup

If you're running tests that store data in Mem0, you can use the following options:

1. Mem0 Dashboard: Use the Mem0 web interface to delete test data
2. API Calls: Use the Mem0 Python SDK directly to delete test data 