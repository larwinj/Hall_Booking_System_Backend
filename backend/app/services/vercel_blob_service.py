import httpx
import json
from datetime import datetime
import os
from typing import Dict, Any

class VercelBlobService:
    
    @staticmethod
    async def upload_backup_to_vercel(backup_data: Dict[str, Any], backup_name: str) -> Dict[str, Any]:
        """
        Upload backup data to Vercel Blob Storage
        """
        from app.core.config import get_settings
        settings = get_settings()
        BLOB_READ_WRITE_TOKEN = settings.BLOB_READ_WRITE_TOKEN
        
        if not BLOB_READ_WRITE_TOKEN:
            raise ValueError("BLOB_READ_WRITE_TOKEN environment variable is not set")
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backups/{backup_name}_{timestamp}.json"
        
        # Convert backup data to JSON string
        backup_json = json.dumps(backup_data, indent=2)
        
        try:
            # Upload to Vercel Blob using async httpx client
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"https://blob.vercel-storage.com/{filename}",
                    headers={
                        "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    content=backup_json,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "vercel_url": result.get("url"),
                    "vercel_pathname": result.get("pathname"),
                    "filename": filename,
                    "uploaded_at": datetime.now().isoformat()
                }
            else:
                raise Exception(f"Vercel Blob upload failed: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Vercel Blob upload error: {str(e)}")
    
    @staticmethod
    async def download_backup_from_vercel(filename: str) -> Dict[str, Any]:
        """
        Download backup data from Vercel Blob Storage
        """
        from app.core.config import get_settings
        settings = get_settings()
        BLOB_READ_WRITE_TOKEN = settings.BLOB_READ_WRITE_TOKEN
        
        if not BLOB_READ_WRITE_TOKEN:
            raise ValueError("BLOB_READ_WRITE_TOKEN environment variable is not set")
        
        try:
            # Download from Vercel Blob using async httpx client
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://blob.vercel-storage.com/{filename}",
                    headers={
                        "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
                    },
                    timeout=30.0
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Vercel Blob download failed: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Vercel Blob download error: {str(e)}")