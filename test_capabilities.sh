#!/bin/bash
# Test script for GitHub MCP Server Capability Advertising

set -e  # Exit on error
BASE_URL="http://localhost:8080"

# Text formatting
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Testing /capabilities endpoint${NC}"
curl -s ${BASE_URL}/capabilities | jq '.'

echo -e "\n${BLUE}2. Testing initialize with capability advertising${NC}"
curl -s -X POST ${BASE_URL}/initialize -H 'Content-Type: application/json' \
  -d '{"clientInfo": {"name": "capability-test", "version": "1.0.0"}}' | jq '.'

echo -e "\n${GREEN}Capability Advertising Tests Completed!${NC}"
