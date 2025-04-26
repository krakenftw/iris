import os
import json
from typing import Dict, List, Any, Optional, Union
from orchestrator.client import LLMClient
from tools.slack.service import SlackService

class ToolCallingLayer:
    def __init__(self):
        self.llm_client = LLMClient()
        self.slack_service = SlackService()
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """Initialize all available tools."""
        return [
            # Calculator tool
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Evaluate a mathematical expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The mathematical expression to evaluate",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            },
            # Slack tool
            {
                "type": "function",
                "function": {
                    "name": "slack_send_message",
                    "description": "Send a message to a Slack channel or user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel": {
                                "type": "string",
                                "description": "The channel or user ID to send the message to",
                            },
                            "message": {
                                "type": "string",
                                "description": "The message content to send",
                            }
                        },
                        "required": ["channel", "message"],
                    },
                },
            },
            # Google Calendar tool
            {
                "type": "function",
                "function": {
                    "name": "gcal_create_event",
                    "description": "Create a new event in Google Calendar",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the event",
                            },
                            "start_time": {
                                "type": "string",
                                "description": "The start time of the event in ISO format",
                            },
                            "end_time": {
                                "type": "string",
                                "description": "The end time of the event in ISO format",
                            },
                            "attendees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of email addresses of attendees",
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the event",
                            }
                        },
                        "required": ["title", "start_time", "end_time"],
                    },
                },
            },
            # Linear tool
            {
                "type": "function",
                "function": {
                    "name": "linear_create_issue",
                    "description": "Create a new issue in Linear",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title of the issue",
                            },
                            "description": {
                                "type": "string",
                                "description": "The description of the issue",
                            },
                            "priority": {
                                "type": "integer",
                                "description": "Priority level (1-4, where 1 is highest)",
                            },
                            "team_id": {
                                "type": "string",
                                "description": "The ID of the team to assign the issue to",
                            },
                            "assignee_id": {
                                "type": "string",
                                "description": "The ID of the user to assign the issue to",
                            }
                        },
                        "required": ["title", "team_id"],
                    },
                },
            },
        ]
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute the specified tool with the given arguments."""
        if tool_name == "calculate":
            expression = arguments.get("expression", "")
            try:
                # WARNING: Using eval is dangerous in production. This is just an example.
                result = eval(expression)
                return f"The result is: {result}"
            except Exception as e:
                return f"Error calculating expression: {str(e)}"
                
        elif tool_name == "slack_send_message":
            # Implementation for sending Slack messages
            channel = arguments.get("channel", "")
            message = arguments.get("message", "")
            self.slack_service.send_message(channel, message)
            return f"Message sent to Slack channel {channel}: {message}"
            
        elif tool_name == "gcal_create_event":
            # Implementation for creating Google Calendar events would go here
            title = arguments.get("title", "")
            start_time = arguments.get("start_time", "")
            end_time = arguments.get("end_time", "")
            return f"Created Google Calendar event '{title}' from {start_time} to {end_time}"
            
        elif tool_name == "linear_create_issue":
            # Implementation for creating Linear issues would go here
            title = arguments.get("title", "")
            team_id = arguments.get("team_id", "")
            return f"Created Linear issue '{title}' for team {team_id}"
            
        else:
            return f"Unknown tool: {tool_name}"
    
    def process_query(self, user_prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Process a user query and execute any requested tools."""
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": user_prompt
        })
        
        # Get response with tools from the LLM client
        response = self.llm_client.get_response(
            prompt=user_prompt,
            tools=self.tools,
        )
        
        message = response.choices[0].message
        
        if not hasattr(message, 'tool_calls') or not message.tool_calls:
            # No tool was called
            return {
                "result": message.content,
                "tool_called": False
            }
        
        # Process tool calls
        tool_results = []
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the tool
            result = self._execute_tool(function_name, function_args)
            tool_results.append({
                "tool": function_name,
                "args": function_args,
                "result": result
            })
            
            # Add the tool call and result to the conversation
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                ]
            })
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # Get final response from the model
        final_prompt = "Based on the tool results, provide a helpful summary response."
        final_response = self.llm_client.get_response(prompt=final_prompt)
        
        return {
            "result": final_response.choices[0].message.content,
            "tool_called": True,
            "tool_results": tool_results
        }

if __name__ == "__main__":
    # Example usage
    api_key = os.environ.get("OPENAI_API_KEY")
    tool_layer = ToolCallingLayer(api_key=api_key)
    
    result = tool_layer.process_query(
        user_prompt="What is 25 * 4 + 10?",
        system_prompt="You are a helpful assistant. Use available tools when appropriate."
    )
    
    print(json.dumps(result, indent=2))