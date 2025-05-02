#!/bin/bash
# Test script for GitHub MCP Server API
# This script contains various curl commands to test the HTTP API endpoints

set -e  # Exit on error
BASE_URL="http://localhost:8080"

# Text formatting
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

# 1. Test the root endpoint
test_endpoint "Get server info" "curl -s ${BASE_URL}/"

# 2. Test the initialize endpoint
test_endpoint "Initialize server" "curl -s -X POST ${BASE_URL}/initialize -H 'Content-Type: application/json' -d '{\"clientInfo\": {\"name\": \"curl-test\", \"version\": \"1.0.0\"}}'"

# 3. Test user.get command
test_endpoint "Get authenticated user" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"user.get\", \"arguments\": []}'"

# 4. Test repository.list command
test_endpoint "List repositories" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"repository.list\", \"arguments\": [\"all\", \"updated\", \"desc\"]}'"

# 5. Test JSON-RPC endpoint with initialize method
test_endpoint "JSON-RPC initialize" "curl -s -X POST ${BASE_URL}/jsonrpc -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": 1, \"method\": \"initialize\", \"params\": {\"clientInfo\": {\"name\": \"curl-json-rpc\", \"version\": \"1.0.0\"}}}'"

# 6. Test JSON-RPC endpoint with executeCommand method
test_endpoint "JSON-RPC executeCommand (user.get)" "curl -s -X POST ${BASE_URL}/jsonrpc -H 'Content-Type: application/json' -d '{\"jsonrpc\": \"2.0\", \"id\": 2, \"method\": \"executeCommand\", \"params\": {\"command\": \"user.get\", \"arguments\": []}}'"

# 7. Test repository.branches command with a specific repository
# Note: Replace owner/repo with an actual repository you have access to
test_endpoint "Get repository branches" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"repository.branches\", \"arguments\": [\"github\", \"github-mcp-server\"]}'"

# 8. Test issue.list command with a specific repository
# Note: Replace owner/repo with an actual repository you have access to
test_endpoint "List repository issues" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"issue.list\", \"arguments\": [\"github\", \"github-mcp-server\", \"open\"]}'"

# 9. Test content.get command to fetch a file
# Note: Replace owner/repo/path with an actual file you want to retrieve
test_endpoint "Get file content" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"content.get\", \"arguments\": [\"github\", \"github-mcp-server\", \"README.md\"]}'"

# 10. Test pullrequest.list command
# Note: Replace owner/repo with an actual repository you have access to
test_endpoint "List pull requests" "curl -s -X POST ${BASE_URL}/executeCommand -H 'Content-Type: application/json' -d '{\"command\": \"pullrequest.list\", \"arguments\": [\"github\", \"github-mcp-server\", \"open\"]}'"

echo -e "\n${GREEN}All tests completed!${NC}"
