# GitHub MCP Server (Python Implementation)

A Python implementation of the GitHub Message Control Protocol (MCP) server for facilitating communication between Windsurf and GitHub.

## Overview

This server provides an interface for communicating with GitHub services via either:
- Standard I/O (stdio) streams using JSON-RPC messages
- HTTP API endpoints 

It supports various GitHub operations and is designed to run in both standalone mode and containerized environments.

## Features

- Modern Python implementation with async support
- Standard I/O communication using JSON-RPC
- REST API interface for HTTP communication
- Configurable GitHub toolsets
- Comprehensive capability advertising
- Advanced GitHub integrations:
  - Repository management
  - Issue tracking with labels and comments
  - Project management (see note on GitHub Projects below)
  - Pull request operations
  - Content management
- Comprehensive logging
- Docker support with configurable ports
- Read-only mode option for restricted operations

### GitHub Projects Implementation

GitHub has deprecated the classic Projects API in favor of their new Projects experience. This MCP server now uses GitHub's GraphQL API to interact with Projects v2, providing full support for the new Projects experience. This means:

1. Project operations use GraphQL instead of REST API
2. Instead of moving cards between columns, you now update a status field value
3. Item IDs are GraphQL node IDs rather than numeric IDs

The API methods maintain backwards compatibility with existing code while using the modern Projects v2 implementation behind the scenes.

## Installation

### Requirements

- Python 3.10+
- Pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/github-mcp-py.git
cd github-mcp-py
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### GitHub Personal Access Token

The MCP server requires a GitHub Personal Access Token to authenticate with the GitHub API. Follow these steps to create one:

1. Go to your GitHub account settings: https://github.com/settings/tokens
2. Click on "Generate new token" (classic)
3. Give your token a descriptive name, e.g., "GitHub MCP Server"
4. Set an expiration date (or choose "No expiration" for testing purposes)
5. Select the following permissions:
   - **repo**: Full control of private repositories
     - repo:status: Access commit status
     - repo_deployment: Access deployment status
     - public_repo: Access public repositories
     - repo:invite: Access repository invitations
   - **user**: Read all user profile data
   - **read:org**: Read org and team data
   - **workflow**: Update GitHub Action workflows

6. Click "Generate token"
7. Copy the generated token (it will only be shown once)
8. Set the token as an environment variable:

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
```

> **IMPORTANT**: Keep your token secure. Anyone with your token can access your GitHub account with the permissions you specified. Never commit your token to version control or share it publicly.

## Usage

### Environment Variables

Create a `.env` file or set the following environment variables:

```
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
GITHUB_HOST=github.com  # Optional: For GitHub Enterprise
GITHUB_READ_ONLY=false  # Optional: Set to true for read-only operations
GITHUB_LOG_FILE=path/to/logfile.log  # Optional: Log file path
GITHUB_ENABLE_COMMAND_LOGGING=false  # Optional: Log all commands
GITHUB_TOOLSETS=all  # Optional: Comma-separated list of toolsets to enable
GITHUB_DYNAMIC_TOOLSETS=false  # Optional: Enable dynamic toolsets
```

### API Methods

The GitHub MCP Server supports the following API methods:

### Repository Operations
- `repository.get` - Get repository details
- `repository.list` - List repositories for a user or organization
- `repository.list_branches` - List branches in a repository
- `repository.get_branch` - Get details of a specific branch

### Issue Management
- `issue.get` - Get issue details
- `issue.list` - List issues in a repository
- `issue.create` - Create a new issue
- `issue.update` - Update an existing issue
- `issue.add_labels` - Add labels to an issue
- `issue.remove_label` - Remove a label from an issue
- `issue.comment` - Add a comment to an issue

### Pull Request Operations
- `pullrequest.get` - Get pull request details
- `pullrequest.list` - List pull requests in a repository
- `pullrequest.create` - Create a new pull request
- `pullrequest.update` - Update an existing pull request
- `pullrequest.merge` - Merge a pull request

### Project Management
- `projects.list` - List projects in a repository
- `projects.get_columns` - Get columns in a project
- `projects.get_cards` - Get cards in a project column
- `projects.move_card` - Move a card to a different column or position

### Content Operations
- `content.get` - Get file contents
- `content.create` - Create a file
- `content.update` - Update file contents

### User Management
- `user.get` - Get user details
- `user.list_followers` - List a user's followers
- `user.list_following` - List users a user is following

### Running the Server

#### Standard I/O Mode

Run the server with stdio communication:

```bash
python -m github_mcp_server stdio
```

#### HTTP Mode

Run the server with HTTP API:

```bash
python -m github_mcp_server http --port 8080
```

## Docker Usage

### Building the Docker Image

```bash
docker build -t github-mcp-server .
```

### Running with Docker

```bash
docker run -p 8080:8080 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
  github-mcp-server http --port 8080
```

For stdio mode (for integration with Windsurf):

```bash
docker run -i \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
  github-mcp-server stdio
```

## Integration with Windsurf

### Using the MCP Server with Windsurf

To integrate this MCP server with Windsurf in a containerized environment:

1. Run the GitHub MCP server in a container:

```bash
docker run -d --name github-mcp \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
  github-mcp-server stdio
```

2. Configure Windsurf to connect to the MCP server container:

In your Windsurf container setup, add:

```yaml
services:
  windsurf:
    # ... windsurf configuration ...
    environment:
      - MCP_GITHUB_SERVER=github-mcp
    depends_on:
      - github-mcp
```

3. In your Windsurf configuration, specify the MCP server endpoint:

```
MCP_GITHUB_SERVER_MODE=container
MCP_GITHUB_SERVER_CONTAINER=github-mcp
```

### Alternative: HTTP Integration

If using HTTP mode instead of stdio:

1. Run the GitHub MCP server with HTTP:

```bash
docker run -d --name github-mcp -p 8080:8080 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
  github-mcp-server http --port 8080
```

2. Configure Windsurf to connect via HTTP:

```
MCP_GITHUB_SERVER_MODE=http
MCP_GITHUB_SERVER_URL=http://github-mcp:8080
```

## API Documentation

The HTTP server exposes a REST API and JSON-RPC endpoints. Documentation available at `/docs` or `/redoc` when running the HTTP server.

## Development

### Running Tests

```bash
pytest
```

## License

[Add your license here]
