#!/bin/bash
# Test script for GitHub MCP Server Project Management Capabilities

set -e  # Exit on error
BASE_URL="http://localhost:8080"

# Text formatting
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function for testing
test_endpoint() {
  local description=$1
  local command=$2
  
  echo -e "\n${BLUE}Test: ${description}${NC}"
  echo -e "Command: ${command}"
  
  # Execute the command and capture output and exit status
  output=$(eval "${command}")
  status=$?
  
  if [ $status -eq 0 ]; then
    echo -e "${GREEN}✓ Success${NC}"
    echo "Response:"
    echo "$output" | jq '.'
  else
    echo -e "${RED}✗ Failed${NC}"
    echo "Error: $output"
  fi
  
  # Pause between requests
  sleep 1
}

# Test 1: Project Management - List Projects
test_endpoint "List Projects" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"projects.list\", \"arguments\": [\"github\", \"github-mcp-server\"]}'"

# Test 2: Project Management - Get Project Columns (replace 1 with your project number)
test_endpoint "Get Project Columns" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"projects.get_columns\", \"arguments\": [\"github\", \"github-mcp-server\", 1]}'"

# Test 3: Issue Management - Get Labels
test_endpoint "Get Repository Labels" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"issue.list\", \"arguments\": [\"github\", \"github-mcp-server\"]}'"

# Test 4: Issue Management - Add Labels (requires issue number)
echo -e "\n${BLUE}To test these additional commands, replace values with real GitHub details:${NC}"
echo -e "${GREEN}1. Add labels to an issue:${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"issue.add_labels\", \"arguments\": [\"OWNER\", \"REPO\", ISSUE_NUMBER, [\"label1\", \"label2\"]]}'"

echo -e "\n${GREEN}2. Remove a label from an issue:${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"issue.remove_label\", \"arguments\": [\"OWNER\", \"REPO\", ISSUE_NUMBER, \"label1\"]}'"

echo -e "\n${GREEN}3. Add a comment to an issue:${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"issue.comment\", \"arguments\": [\"OWNER\", \"REPO\", ISSUE_NUMBER, \"This is a test comment from MCP server\"]}'"

echo -e "\n${GREEN}4. Move a card to a different column:${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"projects.move_card\", \"arguments\": [\"OWNER\", \"REPO\", PROJECT_NUMBER, CARD_ID, \"Target Column\", \"top\"]}'"

echo -e "\n${GREEN}All tests completed!${NC}"
