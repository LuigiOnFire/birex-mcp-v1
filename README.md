# Anomaly Detector MCP
This project contains an MCP server that allows users to make queries to a anomoly detection monitoring system.

The first draft will entail a simple agent that reads a PostgreSQL TimeScaleDB database of event rows containing:
- time
- process id
- whether or not an anomaly was detected

The agent is capable of responding to natural language queries about the database. The natural language query is translated to an SQL query which is executed on the PostgreSQL database. The results are then interpreted by the agent and reported to the user.

## Usage Instructions

1. Place an `.env` file in the root directory of the project container a valid GOOGLE_AI API key, it should look like

```
GOOGLE_API_KEY=<your API -key>
```

2. Run ./reset_container.sh to run the agent.