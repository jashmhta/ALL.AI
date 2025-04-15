import os
import base64
import hashlib
import mimetypes
from typing import Dict, Any, List, Optional, Tuple
import aiofiles

class FileProcessor:
    """
    Handles file uploads and processing for the multi-AI application.
    Supports text extraction, file analysis, and content processing.
    """
    
    def __init__(self, upload_dir: str = None, max_file_size_mb: int = 10):
        """
        Initialize the file processor.
        
        Args:
            upload_dir: Directory to store uploaded files
            max_file_size_mb: Maximum file size in megabytes
        """
        # Set up upload directory
        self.upload_dir = upload_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Set maximum file size
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        
        # Initialize supported file types
        self.supported_text_types = {
            '.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm',
            '.py', '.js', '.java', '.c', '.cpp', '.cs', '.go', '.rb',
            '.php', '.pl', '.sh', '.bat', '.ps1', '.sql', '.yaml', '.yml'
        }
        
        self.supported_document_types = {
            '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'
        }
        
        self.supported_image_types = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'
        }
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> Tuple[bool, str, str]:
        """
        Save an uploaded file to disk.
        
        Args:
            file_content: Binary content of the file
            filename: Original filename
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        # Check file size
        if len(file_content) > self.max_file_size:
            return (False, "", f"File exceeds maximum size of {self.max_file_size // (1024 * 1024)}MB")
        
        # Generate a unique filename to prevent collisions
        file_hash = hashlib.md5(file_content).hexdigest()
        _, file_ext = os.path.splitext(filename)
        safe_filename = f"{file_hash}{file_ext.lower()}"
        file_path = os.path.join(self.upload_dir, safe_filename)
        
        # Save the file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            return (True, file_path, "")
        except Exception as e:
            return (False, "", f"Error saving file: {str(e)}")
    
    async def extract_text_from_file(self, file_path: str) -> Tuple[bool, str, str]:
        """
        Extract text content from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return (False, "", "File not found")
        
        # Get file extension
        _, file_ext = os.path.splitext(file_path)
        file_ext = file_ext.lower()
        
        # Handle text files
        if file_ext in self.supported_text_types:
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                return (True, content, "")
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                        content = await f.read()
                    return (True, content, "")
                except Exception as e:
                    return (False, "", f"Error reading file: {str(e)}")
            except Exception as e:
                return (False, "", f"Error reading file: {str(e)}")
        
        # Handle PDF files
        elif file_ext == '.pdf':
            try:
                # Try to import PyPDF2
                import PyPDF2
                
                # Read PDF content
                text = ""
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num in range(len(pdf_reader.pages)):
                        text += pdf_reader.pages[page_num].extract_text() + "\n\n"
                
                if text.strip():
                    return (True, text, "")
                else:
                    return (False, "", "No text could be extracted from the PDF")
            except ImportError:
                return (False, "", "PyPDF2 library not installed. Cannot extract text from PDF.")
            except Exception as e:
                return (False, "", f"Error extracting text from PDF: {str(e)}")
        
        # Handle document files (requires additional libraries)
        elif file_ext in self.supported_document_types:
            return (False, "", f"Text extraction from {file_ext} files is not supported in this version")
        
        # Handle image files (would require OCR)
        elif file_ext in self.supported_image_types:
            return (False, "", f"Text extraction from images requires OCR, which is not supported in this version")
        
        # Unsupported file type
        else:
            return (False, "", f"Unsupported file type: {file_ext}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        if not os.path.exists(file_path):
            return {
                "exists": False,
                "error": "File not found"
            }
        
        # Get file stats
        file_stats = os.stat(file_path)
        
        # Get file extension and mime type
        _, file_ext = os.path.splitext(file_path)
        file_ext = file_ext.lower()
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Determine file type category
        if file_ext in self.supported_text_types:
            category = "text"
        elif file_ext in self.supported_document_types:
            category = "document"
        elif file_ext in self.supported_image_types:
            category = "image"
        else:
            category = "other"
        
        return {
            "exists": True,
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size": file_stats.st_size,
            "size_human": self._format_size(file_stats.st_size),
            "modified": file_stats.st_mtime,
            "extension": file_ext,
            "mime_type": mime_type or "application/octet-stream",
            "category": category
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024 or unit == 'GB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
    
    def get_file_as_base64(self, file_path: str) -> Tuple[bool, str, str]:
        """
        Get file content as base64 encoded string.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (success, base64_content, error_message)
        """
        if not os.path.exists(file_path):
            return (False, "", "File not found")
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            base64_content = base64.b64encode(file_content).decode('utf-8')
            return (True, base64_content, "")
        except Exception as e:
            return (False, "", f"Error reading file: {str(e)}")
    
    def create_prompt_with_file_content(self, prompt: str, file_content: str, 
                                      file_info: Dict[str, Any]) -> str:
        """
        Create a prompt that includes file content for AI processing.
        
        Args:
            prompt: Original user prompt
            file_content: Extracted text content from the file
            file_info: File information dictionary
            
        Returns:
            Enhanced prompt with file content
        """
        # Create a header with file information
        file_header = f"""
File Information:
- Filename: {file_info['filename']}
- Type: {file_info['mime_type']}
- Size: {file_info['size_human']}

User prompt: {prompt}

File content:
```
{file_content[:8000]}  # Limit content to prevent token overflow
```
"""
        
        # Check if content was truncated
        if len(file_content) > 8000:
            file_header += "\n[Note: File content was truncated due to length. Only the first portion is shown.]\n"
        
        # Create the enhanced prompt
        enhanced_prompt = f"""
Please analyze the following file content and respond to the user's prompt.
{file_header}

Based on the file content above, please respond to the user's prompt: {prompt}
"""
        
        return enhanced_prompt
    
    def list_uploaded_files(self) -> List[Dict[str, Any]]:
        """
        List all uploaded files with their information.
        
        Returns:
            List of file information dictionaries
        """
        files = []
        
        for filename in os.listdir(self.upload_dir):
            file_path = os.path.join(self.upload_dir, filename)
            if os.path.isfile(file_path):
                file_info = self.get_file_info(file_path)
                files.append(file_info)
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x.get('modified', 0), reverse=True)
        
        return files
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (success, error_message)
        """
        # Ensure the file is within the upload directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(self.upload_dir)):
            return (False, "Access denied: File is outside the upload directory")
        
        if not os.path.exists(file_path):
            return (False, "File not found")
        
        try:
            os.remove(file_path)
            return (True, "")
        except Exception as e:
            return (False, f"Error deleting file: {str(e)}")
