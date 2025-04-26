from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from typing import Dict, List, Optional
import os

class LinearService:
    def __init__(self, api_key: str = None):
        """Initialize Linear service with API key
        
        Args:
            api_key (str, optional): Linear API key. If not provided, will look for LINEAR_API_KEY env variable
        """
        self.api_key = api_key or os.environ.get('LINEAR_API_KEY')
        if not self.api_key:
            raise ValueError("Linear API key must be provided or set in LINEAR_API_KEY environment variable")

        transport = RequestsHTTPTransport(
            url='https://api.linear.app/graphql',
            headers={'Authorization': self.api_key}
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def create_issue(self, 
                    title: str, 
                    description: str, 
                    team_id: str,
                    priority: int = 2,
                    assignee_id: Optional[str] = None) -> Dict:
        """Create a new issue in Linear
        
        Args:
            title (str): Issue title
            description (str): Issue description
            team_id (str): ID of the team the issue belongs to
            priority (int, optional): Priority level (0-4). Defaults to 2
            assignee_id (str, optional): ID of the user to assign the issue to
        
        Returns:
            Dict: Created issue data
        """
        mutation = gql("""
            mutation CreateIssue(
                $title: String!
                $description: String!
                $teamId: String!
                $priority: Int
                $assigneeId: String
            ) {
                issueCreate(input: {
                    title: $title
                    description: $description
                    teamId: $teamId
                    priority: $priority
                    assigneeId: $assigneeId
                }) {
                    success
                    issue {
                        id
                        title
                        url
                        priority
                        assignee {
                            id
                            name
                        }
                    }
                }
            }
        """)

        variables = {
            "title": title,
            "description": description,
            "teamId": team_id,
            "priority": priority,
            "assigneeId": assignee_id
        }

        result = self.client.execute(mutation, variable_values=variables)
        return result["issueCreate"]["issue"]

    def get_team_id(self, team_name: str) -> Optional[str]:
        """Get team ID by name
        
        Args:
            team_name (str): Name of the team
            
        Returns:
            Optional[str]: Team ID if found, None otherwise
        """
        query = gql("""
            query GetTeam($teamName: String!) {
                teams(filter: { name: { eq: $teamName } }) {
                    nodes {
                        id
                        name
                    }
                }
            }
        """)

        result = self.client.execute(query, variable_values={"teamName": team_name})
        teams = result["teams"]["nodes"]
        return teams[0]["id"] if teams else None

    def get_user_id(self, email: str) -> Optional[str]:
        """Get user ID by email
        
        Args:
            email (str): User's email address
            
        Returns:
            Optional[str]: User ID if found, None otherwise
        """
        query = gql("""
            query GetUser($email: String!) {
                users(filter: { email: { eq: $email } }) {
                    nodes {
                        id
                        name
                        email
                    }
                }
            }
        """)

        result = self.client.execute(query, variable_values={"email": email})
        users = result["users"]["nodes"]
        return users[0]["id"] if users else None

    def update_issue(self, 
                    issue_id: str, 
                    **kwargs) -> Dict:
        """Update an existing issue
        
        Args:
            issue_id (str): ID of the issue to update
            **kwargs: Fields to update (title, description, priority, status, etc.)
            
        Returns:
            Dict: Updated issue data
        """
        mutation = gql("""
            mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
                issueUpdate(id: $id, input: $input) {
                    success
                    issue {
                        id
                        title
                        description
                        priority
                        status {
                            name
                        }
                    }
                }
            }
        """)

        variables = {
            "id": issue_id,
            "input": kwargs
        }

        result = self.client.execute(mutation, variable_values=variables)
        return result["issueUpdate"]["issue"]

    def create_urgent_issue(self, 
                          title: str, 
                          description: str,
                          team_name: str,
                          assignee_email: Optional[str] = None) -> Dict:
        """Create an urgent issue with high priority
        
        Args:
            title (str): Issue title
            description (str): Issue description
            team_name (str): Name of the team
            assignee_email (str, optional): Email of the user to assign the issue to
            
        Returns:
            Dict: Created issue data
        """
        team_id = self.get_team_id(team_name)
        if not team_id:
            raise ValueError(f"Team '{team_name}' not found")

        assignee_id = None
        if assignee_email:
            assignee_id = self.get_user_id(assignee_email)
            if not assignee_id:
                raise ValueError(f"User with email '{assignee_email}' not found")

        return self.create_issue(
            title=title,
            description=description,
            team_id=team_id,
            priority=4,  # Highest priority
            assignee_id=assignee_id
        )
