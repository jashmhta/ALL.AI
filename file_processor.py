import os
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import json
import tempfile
import mimetypes
import PyPDF2
import csv
import re

class FileProcessor:
    """
    Processes uploaded files for the Multi-AI application.
    Extracts text content from various file formats and prepares it for AI analysis.
    """
    
    def __init__(self, max_file_size_mb: int = 10):
        """
        Initialize the file processor.
        
        Args:
            max_file_size_mb: Maximum file size in MB
        """
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "files")
        
        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
    
    async def process_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process an uploaded file.
        
        Args:
            file_content: Binary content of the file
            filename: Name of the file
            
        Returns:
            Dict containing file information and processing status
        """
        try:
            # Check file size
            if len(file_content) > self.max_file_size_bytes:
                return {
                    "success": False,
                    "error": f"File size exceeds maximum allowed ({self.max_file_size_bytes / 1024 / 1024:.1f} MB)"
                }
            
            # Determine file type
            file_extension = os.path.splitext(filename)[1].lower()
            mime_type, _ = mimetypes.guess_type(filename)
            
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Save the file
            file_path = os.path.join(self.storage_dir, filename)
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # Get file info
            file_info = self.get_file_info(file_path)
            
            # Extract text preview if possible
            success, text_preview, error = await self.extract_text_from_file(file_path, max_length=500)
            
            if success:
                file_info["has_text"] = True
                file_info["text_preview"] = text_preview
            else:
                file_info["has_text"] = False
                file_info["text_preview"] = None
                file_info["extraction_error"] = error
            
            return {
                "success": True,
                "file_info": file_info
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing file: {str(e)}"
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing file information
        """
        try:
            # Get file stats
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            
            # Get file name and extension
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Format file size for display
            if file_size < 1024:
                size_human = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_human = f"{file_size / 1024:.1f} KB"
            else:
                size_human = f"{file_size / 1024 / 1024:.1f} MB"
            
            return {
                "path": file_path,
                "filename": filename,
                "extension": file_extension,
                "mime_type": mime_type,
                "size": file_size,
                "size_human": size_human
            }
        except Exception as e:
            return {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "error": str(e)
            }
    
    async def extract_text_from_file(self, file_path: str, max_length: Optional[int] = None) -> tuple:
        """
        Extract text content from a file.
        
        Args:
            file_path: Path to the file
            max_length: Maximum length of text to extract
            
        Returns:
            Tuple of (success, text_content, error_message)
        """
        try:
            # Get file extension
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # Extract text based on file type
            if file_extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']:
                # Text file
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    text = f.read()
            elif file_extension == '.pdf':
                # PDF file
                text = self._extract_text_from_pdf(file_path)
            elif file_extension == '.csv':
                # CSV file
                text = self._extract_text_from_csv(file_path)
            else:
                return False, None, f"Unsupported file type: {file_extension}"
            
            # Truncate if needed
            if max_length and len(text) > max_length:
                text = text[:max_length] + "..."
            
            return True, text, None
        except Exception as e:
            return False, None, f"Error extracting text: {str(e)}"
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_text_from_csv(self, file_path: str) -> str:
        """
        Extract text from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Extracted text
        """
        text = ""
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                csv_reader = csv.reader(f)
                
                # Get header
                header = next(csv_reader, None)
                
                if header:
                    text += ", ".join(header) + "\n"
                
                # Get rows (limit to 100)
                row_count = 0
                for row in csv_reader:
                    text += ", ".join(row) + "\n"
                    row_count += 1
                    
                    if row_count >= 100:
                        text += "...\n(CSV file truncated, showing first 100 rows)"
                        break
            
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from CSV: {str(e)}")
    
    def create_prompt_with_file_content(self, prompt: str, file_content: str, file_info: Dict[str, Any]) -> str:
        """
        Create a prompt that includes file content.
        
        Args:
            prompt: Original user prompt
            file_content: Extracted text content from the file
            file_info: Information about the file
            
        Returns:
            Enhanced prompt with file content
        """
        # Create a header with file information
        file_header = f"File: {file_info['filename']} ({file_info['size_human']})\n"
        file_header += f"Type: {file_info['mime_type']}\n\n"
        
        # Determine how to format the content based on file type
        file_extension = file_info['extension'].lower()
        
        if file_extension in ['.py', '.js', '.html', '.css', '.json', '.xml']:
            # Code file - wrap in code block
            formatted_content = f"```{file_extension[1:]}\n{file_content}\n```"
        elif file_extension == '.md':
            # Markdown file - keep as is
            formatted_content = file_content
        else:
            # Other file types - wrap in quotes
            formatted_content = f"```\n{file_content}\n```"
        
        # Combine everything
        enhanced_prompt = f"{prompt}\n\n{file_header}{formatted_content}"
        
        return enhanced_prompt
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
