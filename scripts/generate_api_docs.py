#!/usr/bin/env python3
"""
Automatically export FastAPI's Swagger (OpenAPI) to Markdown Documentation

This script:
1. Fetches the OpenAPI schema from FastAPI
2. Converts it to a formatted API_Documentation.md file
3. Merges with manual notes if available

Usage:
    python scripts/generate_api_docs.py
    
Or fetch fresh OpenAPI schema first:
    curl http://127.0.0.1:8000/openapi.json -o docs/openapi.json
    python scripts/generate_api_docs.py
"""

import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Dict, Any, List


class OpenAPIToMarkdown:
    """Convert OpenAPI JSON to Markdown documentation"""
    
    def __init__(self, input_file: str, output_file: str):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.data: Dict[str, Any] = {}
        
    def load_openapi(self) -> bool:
        """Load OpenAPI JSON file"""
        if not self.input_file.exists():
            print(f"❌ Error: {self.input_file} not found")
            print("   Run: curl http://127.0.0.1:8000/openapi.json -o docs/openapi.json")
            return False
        
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            print(f"✓ Loaded OpenAPI schema from {self.input_file}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            return False
    
    def generate_markdown(self) -> str:
        """Generate Markdown from OpenAPI schema"""
        md = []
        
        # Header
        info = self.data.get("info", {})
        title = info.get("title", "Hall Booking System API")
        version = info.get("version", "1.0.0")
        description = info.get("description", "API Documentation")
        
        md.append(f"# {title} Documentation\n")
        md.append(f"**Version:** {version}\n")
        md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append(f"**Base URL:** `/api/v1`\n\n")
        md.append(f"---\n\n{description}\n\n---\n\n")
        
        # Table of Contents
        paths = self.data.get("paths", {})
        tags_dict = self._group_by_tags(paths)
        
        md.append("## 📋 Table of Contents\n\n")
        for tag in sorted(tags_dict.keys()):
            md.append(f"- **{tag}** ({len(tags_dict[tag])} endpoints)\n")
        md.append("\n---\n\n")
        
        # Endpoints by Tag
        for tag in sorted(tags_dict.keys()):
            md.append(f"## {tag}\n\n")
            for endpoint_info in tags_dict[tag]:
                md.extend(self._format_endpoint(endpoint_info))
            md.append("\n---\n\n")
        
        return "\n".join(md)
    
    def _group_by_tags(self, paths: Dict) -> Dict[str, List[Dict]]:
        """Group endpoints by tags"""
        tags_dict: Dict[str, List] = {}
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                    continue
                
                tags = details.get("tags", ["General"])
                tag = tags[0] if tags else "General"
                
                if tag not in tags_dict:
                    tags_dict[tag] = []
                
                tags_dict[tag].append({
                    "path": path,
                    "method": method.upper(),
                    "details": details
                })
        
        return tags_dict
    
    def _format_endpoint(self, endpoint_info: Dict) -> List[str]:
        """Format a single endpoint"""
        md = []
        path = endpoint_info["path"]
        method = endpoint_info["method"]
        details = endpoint_info["details"]
        
        summary = details.get("summary", "No description")
        description = details.get("description", "")
        
        # Endpoint header
        md.append(f"### `{method}` {path}\n")
        md.append(f"**{summary}**\n\n")
        
        if description and description != summary:
            md.append(f"{description}\n\n")
        
        # Authentication
        security = details.get("security")
        if security:
            md.append("🔒 **Requires Authentication**: JWT Bearer Token\n\n")
        
        # Parameters
        params = details.get("parameters", [])
        if params:
            md.append("**Parameters:**\n\n")
            for param in params:
                name = param["name"]
                param_in = param["in"]
                required = param.get("required", False)
                param_desc = param.get("description", "")
                param_type = param.get("schema", {}).get("type", "string")
                
                req_badge = "📌" if required else "📝"
                md.append(f"- {req_badge} `{name}` ({param_type}, in *{param_in}*) — {param_desc}\n")
            md.append("\n")
        
        # Request Body
        if "requestBody" in details:
            md.append("**Request Body:**\n\n")
            req_body = details["requestBody"]
            content = req_body.get("content", {})
            
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                example = content["application/json"].get("example")
                
                if example:
                    md.append("```json\n")
                    md.append(json.dumps(example, indent=2))
                    md.append("\n```\n\n")
        
        # Responses
        responses = details.get("responses", {})
        if responses:
            md.append("**Responses:**\n\n")
            for code, resp in responses.items():
                description = resp.get("description", "")
                md.append(f"- `{code}` — {description}\n")
            md.append("\n")
        
        return md
    
    def save_markdown(self, content: str) -> bool:
        """Save Markdown to file"""
        try:
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            self.output_file.write_text(content, encoding="utf-8")
            print(f"✓ Documentation saved to {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return False


def merge_manual_notes(api_docs: str, manual_file: Path) -> str:
    """Merge manual notes if available"""
    if not manual_file.exists():
        return api_docs
    
    try:
        manual_content = manual_file.read_text(encoding="utf-8")
        return api_docs + "\n\n---\n\n## 📌 Additional Notes\n\n" + manual_content
    except Exception as e:
        print(f"⚠️  Warning: Could not load manual notes: {e}")
        return api_docs


def main():
    """Main execution"""
    print("=" * 60)
    print("🚀 FastAPI OpenAPI → Markdown Documentation Generator")
    print("=" * 60 + "\n")
    
    # Paths
    docs_dir = Path("docs")
    openapi_file = docs_dir / "openapi.json"
    output_file = docs_dir / "API_Documentation.md"
    manual_file = docs_dir / "manual_notes.md"
    
    # Generate converter
    converter = OpenAPIToMarkdown(str(openapi_file), str(output_file))
    
    # Load OpenAPI schema
    if not converter.load_openapi():
        print("\n💡 Tip: Start FastAPI server first:")
        print("   uvicorn app.main:app --reload")
        print("\n   Then export OpenAPI schema:")
        print("   curl http://127.0.0.1:8000/openapi.json -o docs/openapi.json")
        sys.exit(1)
    
    # Generate Markdown
    print("⚙️  Converting OpenAPI to Markdown...")
    md_content = converter.generate_markdown()
    
    # Merge manual notes if available
    if manual_file.exists():
        print(f"📝 Merging manual notes from {manual_file}")
        md_content = merge_manual_notes(md_content, manual_file)
    
    # Save Markdown
    if not converter.save_markdown(md_content):
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Documentation generated successfully!")
    print(f"📄 Output: {output_file}")
    print("\n📖 Next steps:")
    print("   - Open the generated Markdown file")
    print("   - Review and customize as needed")
    print("   - Add to your documentation repository")
    print("=" * 60)


if __name__ == "__main__":
    main()
