"""
Test script for Notion API utilities
Tests reading "분류" and "특이사항" columns from Notion database
"""
from notion_utils import NotionTableReader, create_notion_reader
import settings
from settings import NOTION_API_KEY, NOTION_DATABASE_ID # settings 모듈이 임포트되었는지 확인하세요.


def test_notion_connection():
    """Test basic Notion connection"""
    print("="*60)
    print("Test 1: Notion Connection")
    print("="*60)

    try:
        # Validate settings first
        settings.validate_notion_settings()
        print("✅ Settings validation passed")

        # # Create reader
        # reader = create_notion_reader()
        # NotionTableReader 초기화 시 database_id를 명시적으로 전달합니다.
        reader = NotionTableReader(api_key=NOTION_API_KEY, database_id=NOTION_DATABASE_ID)
        print("✅ NotionTableReader created successfully")

        return reader

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def test_database_schema(reader: NotionTableReader):
    """Test retrieving database schema"""
    print("\n" + "="*60)
    print("Test 2: Database Schema")
    print("="*60)

    try:
        reader.print_database_schema()
        print("\n✅ Schema retrieved successfully")
        return True

    except Exception as e:
        print(f"❌ Schema retrieval failed: {e}")
        return False


def test_read_specific_columns(reader: NotionTableReader):
    """Test reading "분류" and "특이사항" columns"""
    print("\n" + "="*60)
    print('Test 3: Reading "분류" and "특이사항" Columns')
    print("="*60)

    try:
        # Read specific columns
        # column_names = ["분류", "특이사항"]
        column_names = ["suspicious_start", "suspicious_end"]
        rows = reader.get_columns(column_names)

        print(f"\n총 {len(rows)}개의 행을 읽어왔습니다.\n")

        if not rows:
            print("⚠️  데이터베이스가 비어있습니다.")
            return True

        # Display results
        print("-" * 60)
        for i, row in enumerate(rows[:10], 1):  # Show first 10 rows
            분류 = row.get("분류", "N/A")
            특이사항 = row.get("특이사항", "N/A")

            print(f"Row {i}:")
            print(f"  분류: {분류}")
            print(f"  특이사항: {특이사항}")
            print("-" * 60)

        if len(rows) > 10:
            print(f"... and {len(rows) - 10} more rows")

        print(f"\n✅ Successfully read {len(rows)} rows")
        return True

    except Exception as e:
        print(f"❌ Failed to read columns: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_read_all_data(reader: NotionTableReader):
    """Test reading all data from database"""
    print("\n" + "="*60)
    print("Test 4: Reading All Data")
    print("="*60)

    try:
        rows = reader.get_all_rows()

        print(f"\n총 {len(rows)}개의 행을 읽어왔습니다.")

        if rows:
            print("\nFirst row sample:")
            first_row = rows[0]
            for key, value in first_row.items():
                # Skip internal fields for cleaner output
                if not key.startswith("_"):
                    print(f"  {key}: {value}")

        print(f"\n✅ Successfully read all data")
        return True

    except Exception as e:
        print(f"❌ Failed to read all data: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Notion API Test Suite")
    print("="*60)

    # Test 1: Connection
    reader = test_notion_connection()
    if not reader:
        print("\n❌ Tests failed: Could not connect to Notion")
        return

    # Test 2: Schema
    test_database_schema(reader)

    # Test 3: Specific columns ("분류", "특이사항")
    test_read_specific_columns(reader)

    # Test 4: All data
    test_read_all_data(reader)

    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()
