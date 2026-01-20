"""
Notion API utilities for reading database tables
Provides functions to query and retrieve data from Notion databases
"""
from typing import List, Dict, Any, Optional
from notion_client import Client
import settings


class NotionTableReader:
    """Notion 데이터베이스 테이블 리더"""

    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        """
        Initialize Notion client

        Args:
            api_key: Notion API integration token (defaults to settings)
            database_id: Notion database ID (defaults to settings)
        """
        self.api_key = api_key or settings.NOTION_API_KEY
        self.database_id = database_id or settings.NOTION_DATABASE_ID

        if not self.api_key:
            raise ValueError("Notion API key is required")
        if not self.database_id:
            raise ValueError("Notion database ID is required")

        self.client = Client(auth=self.api_key, notion_version="2022-06-28")

    def query_database(self, **query_params) -> List[Dict[str, Any]]:
        """
        Query Notion database and return results

        Returns:
            List of page objects from the database
        """
        try:
            all_results = []
            has_more = True
            start_cursor = None

            while has_more:
                params = {"database_id": self.database_id, **query_params}
                if start_cursor:
                    params["start_cursor"] = start_cursor

                response = self.client.databases.query(**params)
                all_results.extend(response.get("results", []))

                has_more = response.get("has_more", False)
                start_cursor = response.get("next_cursor")

            return all_results
        except AttributeError as e:
            # Fallback: try using POST request directly if method doesn't exist
            print(f"AttributeError: {e}. Trying alternative approach...")
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Notion-Version": "2022-06-28"
                }
                url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
                response = requests.post(url, headers=headers, json=query_params)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                # Debug: print first result to see structure
                if results:
                    print(f"[DEBUG] First result keys: {results[0].keys()}")
                    print(f"[DEBUG] First result properties: {results[0].get('properties', {})}")
                return results
            except Exception as inner_e:
                print(f"Fallback also failed: {inner_e}")
                return []
        except Exception as e:
            print(f"Error querying Notion database with ID {self.database_id}: {e}")
            return []

    def get_property_value(self, page: Dict, property_name: str) -> Any:
        """
        Extract value from a page property

        Args:
            page: Notion page object
            property_name: Name of the property to extract

        Returns:
            Property value (type depends on property type)
        """
        properties = page.get("properties", {})
        prop = properties.get(property_name)

        if not prop:
            return None

        prop_type = prop.get("type")

        # Handle different property types
        if prop_type == "title":
            title_list = prop.get("title", [])
            return title_list[0].get("plain_text", "") if title_list else ""

        elif prop_type == "rich_text":
            text_list = prop.get("rich_text", [])
            return text_list[0].get("plain_text", "") if text_list else ""

        elif prop_type == "number":
            return prop.get("number")

        elif prop_type == "select":
            select = prop.get("select")
            return select.get("name") if select else None

        elif prop_type == "multi_select":
            multi_select = prop.get("multi_select", [])
            return [item.get("name") for item in multi_select]

        elif prop_type == "date":
            date = prop.get("date")
            return date.get("start") if date else None

        elif prop_type == "checkbox":
            return prop.get("checkbox", False)

        elif prop_type == "url":
            return prop.get("url")

        elif prop_type == "email":
            return prop.get("email")

        elif prop_type == "phone_number":
            return prop.get("phone_number")

        elif prop_type == "status":
            status = prop.get("status")
            return status.get("name") if status else None

        else:
            # Return raw property for unsupported types
            return prop

    def get_all_rows(self, property_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get all rows from the database with specified properties

        Args:
            property_names: List of property names to extract (None = all properties)

        Returns:
            List of dictionaries containing row data
        """
        pages = self.query_database()
        rows = []

        for page in pages:
            if property_names:
                # Extract only specified properties
                row = {
                    prop_name: self.get_property_value(page, prop_name)
                    for prop_name in property_names
                }
            else:
                # Extract all properties
                properties = page.get("properties", {})
                row = {
                    prop_name: self.get_property_value(page, prop_name)
                    for prop_name in properties.keys()
                }

            # Add page ID and URL
            row["_id"] = page.get("id")
            row["_url"] = page.get("url")

            rows.append(row)

        return rows

    def get_columns(self, column_names: List[str]) -> List[Dict[str, Any]]:
        """
        Get specific columns from all rows

        Args:
            column_names: List of column names to retrieve

        Returns:
            List of dictionaries with only the specified columns
        """
        return self.get_all_rows(property_names=column_names)

    def retrieve_database(self) -> Dict[str, Any]:
        """
        Retrieve database metadata

        Returns:
            Database metadata dictionary
        """
        try:
            return self.client.databases.retrieve(database_id=self.database_id)
        except Exception as e:
            print(f"Error retrieving database: {e}")
            return {}

    def print_database_schema(self):
        """Print database schema information"""
        try:
            database = self.retrieve_database()
            properties = database.get("properties", {})

            title_list = database.get('title', [])
            db_title = title_list[0].get('plain_text', 'Untitled') if title_list else 'Untitled'

            print(f"Database: {db_title}")
            print(f"Database ID: {self.database_id}")
            print("\nProperties:")
            print("-" * 60)

            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type")
                print(f"  {prop_name:30} | Type: {prop_type}")

            print("-" * 60)

        except Exception as e:
            print(f"Error retrieving database schema: {e}")
            raise


def create_notion_reader(api_key: Optional[str] = None, database_id: Optional[str] = None) -> NotionTableReader:
    """
    Factory function to create a NotionTableReader instance

    Args:
        api_key: Notion API integration token
        database_id: Notion database ID

    Returns:
        NotionTableReader instance
    """
    return NotionTableReader(api_key=api_key, database_id=database_id)


if __name__ == "__main__":
    # Example usage
    try:
        reader = create_notion_reader()

        print("=== Notion Database Schema ===")
        reader.print_database_schema()

        print("\n=== Sample Data ===")
        rows = reader.get_all_rows()
        print(f"Total rows: {len(rows)}")

        if rows:
            print("\nFirst row:")
            for key, value in rows[0].items():
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"Error: {e}")
