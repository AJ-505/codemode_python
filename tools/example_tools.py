"""
Example tools that both agents can use.
These tools demonstrate various scenarios for benchmarking.
"""

import json
from typing import Dict, List, Any, Callable


# Tool implementations
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather for a location."""
    # Simulated weather data
    weather_data = {
        "san francisco": {"temp": 18, "condition": "Partly cloudy"},
        "new york": {"temp": 22, "condition": "Sunny"},
        "london": {"temp": 12, "condition": "Rainy"},
        "tokyo": {"temp": 25, "condition": "Clear"},
    }

    location_lower = location.lower()
    if location_lower not in weather_data:
        return f"Weather data not available for {location}"

    data = weather_data[location_lower]
    temp = data["temp"]
    if unit.lower() == "fahrenheit":
        temp = (temp * 9/5) + 32

    return json.dumps({
        "location": location,
        "temperature": temp,
        "unit": unit,
        "condition": data["condition"]
    })


def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    try:
        # Simple safe evaluation (in production, use a proper parser)
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return json.dumps({"error": "Invalid characters in expression"})

        result = eval(expression, {"__builtins__": {}}, {})
        return json.dumps({"expression": expression, "result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_database(query: str, category: str = "all") -> str:
    """Search a simulated database."""
    database = {
        "products": [
            {"id": 1, "name": "Laptop", "price": 999},
            {"id": 2, "name": "Mouse", "price": 25},
            {"id": 3, "name": "Keyboard", "price": 75},
        ],
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
        ]
    }

    query_lower = query.lower()
    results = []

    categories = [category] if category != "all" else database.keys()

    for cat in categories:
        if cat in database:
            for item in database[cat]:
                if any(query_lower in str(v).lower() for v in item.values()):
                    results.append({**item, "category": cat})

    return json.dumps({"query": query, "results": results})


def send_email(to: str, subject: str, body: str) -> str:
    """Simulate sending an email."""
    return json.dumps({
        "status": "sent",
        "to": to,
        "subject": subject,
        "message": "Email sent successfully (simulated)"
    })


# Tool registry
TOOLS: Dict[str, Callable] = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_database": search_database,
    "send_email": send_email,
}


def get_tools() -> Dict[str, Callable]:
    """Return the dictionary of available tools."""
    return TOOLS


def get_tool_schemas() -> List[Dict[str, Any]]:
    """
    Return tool schemas in the format expected by LLM APIs.
    This is for the regular agent using function calling.
    """
    return [
        {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit",
                        "default": "celsius"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "calculate",
            "description": "Safely evaluate a mathematical expression",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        },
        {
            "name": "search_database",
            "description": "Search a simulated database",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["all", "products", "users"],
                        "description": "Category to search in",
                        "default": "all"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "send_email",
            "description": "Simulate sending an email",
            "input_schema": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        }
    ]


def get_code_mode_api() -> str:
    """
    Return Python API definitions for Code Mode.
    This is the interface that the LLM will write code against.
    """
    return '''
from typing import TypedDict, List, Literal, Dict

# ============================================================================
# Response Type Definitions
# ============================================================================
# These TypedDicts show the exact structure of JSON responses from each tool.
# All tools return JSON strings that must be parsed with json.loads().

class WeatherResponse(TypedDict):
    """Response from get_weather"""
    location: str
    temperature: float  # In the requested unit
    unit: str  # "celsius" or "fahrenheit"
    condition: str  # Weather condition description

class CalculateSuccessResponse(TypedDict):
    """Successful response from calculate"""
    expression: str
    result: float

class CalculateErrorResponse(TypedDict):
    """Error response from calculate"""
    error: str

class DatabaseItemDict(TypedDict):
    """Structure of a database item (product or user)"""
    id: int
    category: str  # "products" or "users"
    # Additional fields vary by category:
    # Products: name (str), price (int)
    # Users: name (str), email (str)

class SearchResponse(TypedDict):
    """Response from search_database"""
    query: str
    results: List[Dict]  # List of items matching the query, structure varies

class EmailResponse(TypedDict):
    """Response from send_email"""
    status: Literal["sent"]
    to: str
    subject: str
    message: str

# ============================================================================
# Tools API
# ============================================================================

class Tools:
    """Available tools for the agent to use."""

    def get_weather(
        self,
        location: str,
        unit: Literal["celsius", "fahrenheit"] = "celsius"
    ) -> str:
        """
        Get the current weather for a location.

        Args:
            location: The city name (e.g., "San Francisco", "New York", "London", "Tokyo")
            unit: Temperature unit ('celsius' or 'fahrenheit')

        Returns:
            JSON string that parses to WeatherResponse.

            Example parsed structure:
            {
                "location": "San Francisco",
                "temperature": 18.0,
                "unit": "celsius",
                "condition": "Partly cloudy"
            }

            Or error message string if location not found:
            "Weather data not available for {location}"

            Usage:
            result_str = tools.get_weather("San Francisco", "celsius")
            result: WeatherResponse = json.loads(result_str)
            temp: float = result["temperature"]
            condition: str = result["condition"]
        """
        pass

    def calculate(self, expression: str) -> str:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: The mathematical expression to evaluate (supports +, -, *, /, parentheses)

        Returns:
            JSON string that parses to CalculateSuccessResponse or CalculateErrorResponse.

            Success example:
            {
                "expression": "10 + 5 * 2",
                "result": 20.0
            }

            Error example:
            {
                "error": "Invalid characters in expression"
            }

            Usage:
            result_str = tools.calculate("10 + 5 * 2")
            result = json.loads(result_str)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                answer: float = result["result"]
                print(f"Result: {answer}")
        """
        pass

    def search_database(
        self,
        query: str,
        category: Literal["all", "products", "users"] = "all"
    ) -> str:
        """
        Search a simulated database.

        Args:
            query: The search query (case-insensitive, searches all fields)
            category: Category to search in ('all', 'products', or 'users')

        Returns:
            JSON string that parses to SearchResponse.

            Example parsed structure:
            {
                "query": "laptop",
                "results": [
                    {
                        "id": 1,
                        "name": "Laptop",
                        "price": 999,
                        "category": "products"
                    }
                ]
            }

            Product items have: id, name, price, category
            User items have: id, name, email, category

            Usage:
            result_str = tools.search_database("laptop", "products")
            result: SearchResponse = json.loads(result_str)
            results: List[Dict] = result["results"]
            for item in results:
                if item["category"] == "products":
                    print(f"Product: {item['name']} - ${item['price']}")
        """
        pass

    def send_email(self, to: str, subject: str, body: str) -> str:
        """
        Simulate sending an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content

        Returns:
            JSON string that parses to EmailResponse.

            Example parsed structure:
            {
                "status": "sent",
                "to": "recipient@example.com",
                "subject": "Hello",
                "message": "Email sent successfully (simulated)"
            }

            Usage:
            result_str = tools.send_email("user@example.com", "Hello", "Message body")
            result: EmailResponse = json.loads(result_str)
            print(result["message"])
        """
        pass

# Available instance
tools = Tools()
'''
