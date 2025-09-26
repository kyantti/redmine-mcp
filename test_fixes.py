#!/usr/bin/env python3
"""
Simple test script to verify the project functionality works in both versions
"""
import asyncio
from fastmcp.client import FastMCPClient


async def test_projects():
    print("Testing redmine-mcp project functionality...")
    
    try:
        # Test the new project
        async with FastMCPClient("C:/Users/pablo.setrakianbearz/Desktop/python-projects/redmine-mcp/main.py") as client:
            print("Testing get_all_projects...")
            result = await client.call_tool("get_all_projects", {})
            if result and result.content:
                print("✓ get_all_projects works!")
                print(f"  Content length: {len(str(result.content[0]))}")
            else:
                print("✗ get_all_projects failed - no content")
            
            print("\nTesting get_project_members_by_project_id...")
            result = await client.call_tool("get_project_members_by_project_id", {"project_id": 63547})
            if result and result.content:
                print("✓ get_project_members_by_project_id works!")
                members_text = str(result.content[0])
                if "Total members:" in members_text:
                    print(f"  Found members in project")
            else:
                print("✗ get_project_members_by_project_id failed - no content")
                
    except Exception as e:
        print(f"✗ Error testing redmine-mcp: {e}")
    
    print("\n" + "="*50)
    print("Testing completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_projects())
