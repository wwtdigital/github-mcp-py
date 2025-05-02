#!/bin/bash
# Test script for GitHub MCP Server Project Management Capabilities (GraphQL Implementation)

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

# Test 1: Project Management (GraphQL) - List Projects
test_endpoint "List Projects (GraphQL API V2)" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"projects.list\", \"arguments\": [\"github\", \"github-mcp-server\"]}'"

# Test 2: Project Management - Get Project Status Options (Status field options in Projects V2)
test_endpoint "Get Project Status Options" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"projects.get_columns\", \"arguments\": [\"github\", \"github-mcp-server\", 1]}'"

# Test 3: Issue Management - Get Issues
test_endpoint "Get Repository Issues" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"issue.list\", \"arguments\": [\"github\", \"github-mcp-server\"]}'"

# Show instructions for the remaining test commands
echo -e "\n${BLUE}To test these additional commands, replace values with real GitHub details:${NC}"

echo -e "\n${GREEN}1. Get items with a specific status in a project:${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"projects.get_cards\", \"arguments\": [\"OWNER\", \"REPO\", PROJECT_NUMBER, \"Todo\"]}'"

echo -e "\n${GREEN}2. Update an item's status in a project (GraphQL):${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"projects.move_card\", \"arguments\": [\"OWNER\", \"REPO\", PROJECT_NUMBER, \"ITEM_ID\", \"In Progress\", \"top\"]}'"
echo "Note: ITEM_ID should be the GraphQL node ID of the project item"

echo -e "\n${GREEN}3. Add labels to an issue:${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"issue.add_labels\", \"arguments\": [\"OWNER\", \"REPO\", ISSUE_NUMBER, [\"label1\", \"label2\"]]}'"

echo -e "\n${GREEN}4. Remove a label from an issue:${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"issue.remove_label\", \"arguments\": [\"OWNER\", \"REPO\", ISSUE_NUMBER, \"label1\"]}'"

echo -e "\n${GREEN}5. Add a comment to an issue:${NC}"
echo "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' \\"
echo "  -d '{\"command\": \"issue.comment\", \"arguments\": [\"OWNER\", \"REPO\", ISSUE_NUMBER, \"This is a test comment from MCP server\"]}'"

echo -e "\n${BLUE}Important Note:${NC}"
echo "GitHub has deprecated the classic Projects API in favor of the new Projects experience."
echo "This script tests the GraphQL implementation for Projects V2."

echo -e "\n${GREEN}All tests completed!${NC}"
