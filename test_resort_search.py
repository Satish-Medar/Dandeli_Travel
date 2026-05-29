# Ad hoc test or script for resort search validation outside the main test suite.
# File: test_resort_search.py

#!/usr/bin/env python
"""Test resort search functionality"""

import sys
import asyncio
from travel_tools.search_engine import load_all_documents, retrieve_matching_resorts, SearchFilters
from travel_tools.search_tool import search_resorts_tool, find_resort_by_name

def test_data_loading():
    """Test if resort data loads properly"""
    print("=" * 60)
    print("TEST 1: Loading resort data")
    print("=" * 60)
    docs = load_all_documents()
    print(f"✓ Total resorts loaded: {len(docs)}")
    if docs:
        print(f"✓ First resort: {docs[0]['metadata'].get('name')}")
        print(f"✓ Resorts: {[doc['metadata'].get('name') for doc in docs[:5]]}")
    return docs

def test_find_by_name():
    """Test finding a resort by name"""
    print("\n" + "=" * 60)
    print("TEST 2: Finding resort by name")
    print("=" * 60)
    
    resort = find_resort_by_name("Bison River Resort")
    if resort:
        print(f"✓ Found: {resort['name']}")
        print(f"  Category: {resort['category']}")
        print(f"  Price: ₹{resort['price_per_person']}")
        print(f"  Rating: {resort['rating']}")
        print(f"  Phone: {resort['contact_phone']}")
    else:
        print("✗ Resort not found")
    return resort

def test_filter_extraction():
    """Test filter extraction from query"""
    print("\n" + "=" * 60)
    print("TEST 3: Filter extraction")
    print("=" * 60)
    
    queries = [
        "tell me about Bison River Resort",
        "what facilities does Bison River Resort provide",
        "Bison River Resort details"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        try:
            from travel_tools.search_engine import extract_filters_async
            filters = asyncio.run(extract_filters_async(query))
            print(f"  Filters: target_resort_names={filters.target_resort_names}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

async def test_search_tool():
    """Test the search tool directly"""
    print("\n" + "=" * 60)
    print("TEST 4: Search tool async test")
    print("=" * 60)
    
    queries = [
        "tell me about Bison River Resort",
        "what facilities does Bison River Resort provide",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        try:
            result = await search_resorts_tool.ainvoke(query)
            print(f"Result length: {len(str(result))} chars")
            # Try to parse as JSON
            import json
            try:
                data = json.loads(result)
                print(f"✓ Valid JSON")
                print(f"  Status: {data.get('status')}")
                if 'top_results' in data:
                    print(f"  Found resorts: {len(data['top_results'])}")
                    for resort in data['top_results'][:1]:
                        print(f"    - {resort['name']}")
            except json.JSONDecodeError as je:
                print(f"✗ Invalid JSON: {str(result)[:200]}")
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("\nRunning Resort Search Diagnostics\n")
    
    # Test 1: Load data
    docs = test_data_loading()
    
    # Test 2: Find by name
    resort = test_find_by_name()
    
    # Test 3: Filter extraction
    test_filter_extraction()
    
    # Test 4: Async search tool
    print("\n" + "=" * 60)
    asyncio.run(test_search_tool())
    
    print("\n" + "=" * 60)
    print("Diagnostics complete!")
