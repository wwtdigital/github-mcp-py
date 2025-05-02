"""
GitHub GraphQL API client.

This module provides a client for interacting with GitHub's GraphQL API,
primarily for the new Projects experience which is only available through GraphQL.
"""

import os
from typing import Dict, List, Optional, Any, Union
import json

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from loguru import logger

from ..config import Config


class GitHubGraphQLClient:
    """
    GitHub GraphQL API client.
    
    This class provides methods for querying and mutating data through
    GitHub's GraphQL API, with a focus on the new Projects experience.
    """
    
    def __init__(self, config: Config):
        """
        Initialize GitHub GraphQL client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.token = config.github_personal_access_token
        self.read_only = config.github_read_only
        self.host = config.github_host
        
        # Set up the transport with auth token
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v4+json"
        }
        
        # Determine the endpoint URL based on host config
        if self.host:
            # GitHub Enterprise
            self.endpoint = f"https://{self.host}/api/graphql"
        else:
            # GitHub.com
            self.endpoint = "https://api.github.com/graphql"
            
        # Initialize the transport
        transport = RequestsHTTPTransport(
            url=self.endpoint,
            headers=headers,
            verify=True
        )
        
        # Initialize the client
        self.client = Client(transport=transport, fetch_schema_from_transport=False)
        
        logger.debug(f"GitHub GraphQL client initialized for endpoint: {self.endpoint}")
        
    def execute_query(self, query_string: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        
        Args:
            query_string: GraphQL query string
            variables: Variables for the query
            
        Returns:
            Query result
            
        Raises:
            Exception: If the query fails
        """
        try:
            # Parse the query
            query = gql(query_string)
            
            # Execute the query
            result = self.client.execute(query, variable_values=variables or {})
            return result
        except Exception as e:
            logger.error(f"GraphQL query failed: {str(e)}")
            raise
            
    def execute_mutation(self, mutation_string: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL mutation.
        
        Args:
            mutation_string: GraphQL mutation string
            variables: Variables for the mutation
            
        Returns:
            Mutation result
            
        Raises:
            Exception: If the mutation fails or in read-only mode
        """
        if self.read_only:
            logger.warning("Attempted to execute mutation in read-only mode")
            raise Exception("Server is in read-only mode, mutations are not allowed")
            
        try:
            # Parse the mutation
            mutation = gql(mutation_string)
            
            # Execute the mutation
            result = self.client.execute(mutation, variable_values=variables or {})
            return result
        except Exception as e:
            logger.error(f"GraphQL mutation failed: {str(e)}")
            raise
            
    # Projects V2 specific queries and mutations
    
    def list_organization_projects(self, org: str, first: int = 20) -> Dict[str, Any]:
        """
        List projects for an organization.
        
        Args:
            org: Organization login
            first: Number of projects to return
            
        Returns:
            List of projects
        """
        query = """
        query($org: String!, $first: Int!) {
          organization(login: $org) {
            projectsV2(first: $first) {
              nodes {
                id
                number
                title
                shortDescription
                closed
                url
                createdAt
                updatedAt
              }
            }
          }
        }
        """
        variables = {
            "org": org,
            "first": first
        }
        
        return self.execute_query(query, variables)
        
    def list_repository_projects(self, owner: str, repo: str, first: int = 20) -> Dict[str, Any]:
        """
        List projects for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            first: Number of projects to return
            
        Returns:
            List of projects
        """
        query = """
        query($owner: String!, $repo: String!, $first: Int!) {
          repository(owner: $owner, name: $repo) {
            projectsV2(first: $first) {
              nodes {
                id
                number
                title
                shortDescription
                closed
                url
                createdAt
                updatedAt
              }
            }
          }
        }
        """
        variables = {
            "owner": owner,
            "repo": repo,
            "first": first
        }
        
        return self.execute_query(query, variables)
        
    def get_project(self, owner: str, project_number: int, org_project: bool = False) -> Dict[str, Any]:
        """
        Get a specific project.
        
        Args:
            owner: Owner (organization or user)
            project_number: Project number
            org_project: Whether the project belongs to an organization
            
        Returns:
            Project details
        """
        if org_project:
            query = """
            query($org: String!, $number: Int!) {
              organization(login: $org) {
                projectV2(number: $number) {
                  id
                  number
                  title
                  shortDescription
                  closed
                  url
                  createdAt
                  updatedAt
                }
              }
            }
            """
            variables = {
                "org": owner,
                "number": project_number
            }
        else:
            query = """
            query($owner: String!, $number: Int!) {
              user(login: $owner) {
                projectV2(number: $number) {
                  id
                  number
                  title
                  shortDescription
                  closed
                  url
                  createdAt
                  updatedAt
                }
              }
            }
            """
            variables = {
                "owner": owner,
                "number": project_number
            }
            
        return self.execute_query(query, variables)
        
    def get_project_fields(self, project_id: str) -> Dict[str, Any]:
        """
        Get fields for a project.
        
        Args:
            project_id: Project node ID
            
        Returns:
            Project fields
        """
        query = """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 20) {
                nodes {
                  ... on ProjectV2Field {
                    id
                    name
                  }
                  ... on ProjectV2IterationField {
                    id
                    name
                    configuration {
                      iterations {
                        startDate
                        endDate
                      }
                    }
                  }
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options {
                      id
                      name
                      color
                    }
                  }
                }
              }
            }
          }
        }
        """
        variables = {
            "projectId": project_id
        }
        
        return self.execute_query(query, variables)
        
    def get_project_items(self, project_id: str, first: int = 100) -> Dict[str, Any]:
        """
        Get items in a project.
        
        Args:
            project_id: Project node ID
            first: Number of items to return
            
        Returns:
            Project items
        """
        query = """
        query($projectId: ID!, $first: Int!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: $first) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      id
                      number
                      title
                      state
                      repository {
                        name
                        owner {
                          login
                        }
                      }
                    }
                    ... on PullRequest {
                      id
                      number
                      title
                      state
                      repository {
                        name
                        owner {
                          login
                        }
                      }
                    }
                  }
                  fieldValues(first: 8) {
                    nodes {
                      ... on ProjectV2ItemFieldTextValue {
                        text
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldDateValue {
                        date
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        variables = {
            "projectId": project_id,
            "first": first
        }
        
        return self.execute_query(query, variables)
        
    def add_item_to_project(self, project_id: str, content_id: str) -> Dict[str, Any]:
        """
        Add an item to a project.
        
        Args:
            project_id: Project node ID
            content_id: Content node ID (issue or PR)
            
        Returns:
            Result of the mutation
        """
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {
            projectId: $projectId,
            contentId: $contentId
          }) {
            item {
              id
            }
          }
        }
        """
        variables = {
            "projectId": project_id,
            "contentId": content_id
        }
        
        return self.execute_mutation(mutation, variables)
        
    def update_project_item_field(self, project_id: str, item_id: str, field_id: str, 
                                value: Union[str, int, bool]) -> Dict[str, Any]:
        """
        Update a field value for a project item.
        
        Args:
            project_id: Project node ID
            item_id: Item node ID
            field_id: Field node ID
            value: New value
            
        Returns:
            Result of the mutation
        """
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId,
            itemId: $itemId,
            fieldId: $fieldId,
            value: $value
          }) {
            projectV2Item {
              id
            }
          }
        }
        """
        # Convert the value to a string format that GraphQL expects
        # Different field types require different JSON formatting
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        else:
            value_str = json.dumps(str(value))
            
        variables = {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "value": value_str
        }
        
        return self.execute_mutation(mutation, variables)
        
    def remove_item_from_project(self, project_id: str, item_id: str) -> Dict[str, Any]:
        """
        Remove an item from a project.
        
        Args:
            project_id: Project node ID
            item_id: Item node ID
            
        Returns:
            Result of the mutation
        """
        mutation = """
        mutation($projectId: ID!, $itemId: ID!) {
          deleteProjectV2Item(input: {
            projectId: $projectId,
            itemId: $itemId
          }) {
            deletedItemId
          }
        }
        """
        variables = {
            "projectId": project_id,
            "itemId": item_id
        }
        
        return self.execute_mutation(mutation, variables)
