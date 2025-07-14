#!/usr/bin/env python3
"""Test the fixed NLP processor"""

import sys
sys.path.append('/Users/byoungs/Documents/gitlab/semantic_mcp')

from langflow_mcp_server import NaturalLanguageProcessor

# Test problematic inputs that might cause 400 errors
test_cases = [
    "",  # Empty string
    "   ",  # Whitespace only
    "hello",  # Non-business query
    "show me something",  # Vague query
    "revenue by product category",  # Should work
    "top cities",  # Should work
    "customers",  # Should work
    "xyz random text that matches nothing",  # Should default
]

print("🧪 Testing Fixed NLP Processor")
print("=" * 35)

for i, description in enumerate(test_cases, 1):
    print(f"{i}. Input: '{description}'")
    query = NaturalLanguageProcessor.convert_to_query(description)
    
    # Validate that query meets Cube.js requirements
    has_measures = bool(query.get("measures"))
    has_dimensions = bool(query.get("dimensions"))
    
    if has_measures or has_dimensions:
        print(f"   ✅ Valid query: {query}")
    else:
        print(f"   ❌ Invalid query (no measures/dimensions): {query}")
    print()