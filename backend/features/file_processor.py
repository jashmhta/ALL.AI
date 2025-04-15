import os
import json
import mimetypes
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

class FileProcessor:
    """
    Processes various file types for AI consumption.
    """
    
    def __init__(self):
        """
        Initialize the file processor.
        """
        self.supported_extensions = {
            # Documents
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            
            # Spreadsheets
            ".csv": "text/csv",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            
            # Code
            ".py": "text/x-python",
            ".js": "text/javascript",
            ".html": "text/html",
            ".css": "text/css",
            ".json": "application/json",
            
            # Images
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".webp": "image/webp",
            
            # Audio
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            
            # Video
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            
            # Archives
            ".zip": "application/zip",
            ".tar": "application/x-tar",
            ".gz": "application/gzip"
        }
        
        # Ensure MIME types are registered
        for ext, mime_type in self.supported_extensions.items():
            mimetypes.add_type(mime_type, ext)
    
    def get_file_extension(self, filename: str) -> str:
        """
        Get the file extension from a filename.
        
        Args:
            filename: Input filename
            
        Returns:
            File extension (including dot)
        """
        _, ext = os.path.splitext(filename)
        return ext.lower()
    
    def get_mime_type(self, filename: str) -> str:
        """
        Get the MIME type for a file.
        
        Args:
            filename: Input filename
            
        Returns:
            MIME type
        """
        ext = self.get_file_extension(filename)
        
        if ext in self.supported_extensions:
            return self.supported_extensions[ext]
        
        # Fallback to system MIME type detection
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"
    
    def is_supported_file_type(self, filename: str) -> bool:
        """
        Check if a file type is supported.
        
        Args:
            filename: Input filename
            
        Returns:
            True if supported, False otherwise
        """
        ext = self.get_file_extension(filename)
        return ext in self.supported_extensions
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file for AI consumption.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Processed file data
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        filename = os.path.basename(file_path)
        ext = self.get_file_extension(filename)
        mime_type = self.get_mime_type(filename)
        
        # Get file metadata
        file_size = os.path.getsize(file_path)
        modified_time = os.path.getmtime(file_path)
        
        # Initialize result
        result = {
            "filename": filename,
            "extension": ext,
            "mime_type": mime_type,
            "file_size": file_size,
            "modified_time": datetime.fromtimestamp(modified_time).isoformat(),
            "content_type": self._get_content_type(mime_type),
            "extracted_text": None,
            "error": None
        }
        
        # Extract content based on file type
        try:
            if mime_type.startswith("text/"):
                # Text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    result["extracted_text"] = f.read()
            
            elif mime_type == "application/pdf":
                # PDF files
                result["extracted_text"] = self._extract_pdf_text(file_path)
            
            elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                # Word documents
                result["extracted_text"] = self._extract_doc_text(file_path)
            
            elif mime_type in ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                # Spreadsheets
                result["extracted_text"] = self._extract_spreadsheet_text(file_path)
            
            elif mime_type.startswith("image/"):
                # Images - no text extraction, but mark as processed
                result["content_type"] = "image"
            
            elif mime_type.startswith("audio/"):
                # Audio - no text extraction, but mark as processed
                result["content_type"] = "audio"
            
            elif mime_type.startswith("video/"):
                # Video - no text extraction, but mark as processed
                result["content_type"] = "video"
            
            elif mime_type in ["application/zip", "application/x-tar", "application/gzip"]:
                # Archives - list contents
                result["extracted_text"] = self._list_archive_contents(file_path)
            
            else:
                # Unsupported file type
                result["error"] = f"Unsupported file type: {mime_type}"
        
        except Exception as e:
            result["error"] = f"Error processing file: {str(e)}"
        
        return result
    
    def _get_content_type(self, mime_type: str) -> str:
        """
        Get content type category from MIME type.
        
        Args:
            mime_type: MIME type
            
        Returns:
            Content type category
        """
        if mime_type.startswith("text/"):
            return "text"
        elif mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return "document"
        elif mime_type in ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            return "spreadsheet"
        elif mime_type in ["application/zip", "application/x-tar", "application/gzip"]:
            return "archive"
        else:
            return "binary"
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            import PyPDF2
            
            text = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
            
            return "\n\n".join(text)
        
        except ImportError:
            # Fallback to command-line tools
            try:
                import subprocess
                result = subprocess.run(['pdftotext', file_path, '-'], capture_output=True, text=True)
                return result.stdout
            except:
                return "[PDF text extraction requires PyPDF2 or pdftotext]"
    
    def _extract_doc_text(self, file_path: str) -> str:
        """
        Extract text from Word document.
        
        Args:
            file_path: Path to Word document
            
        Returns:
            Extracted text
        """
        try:
            import docx
            
            if file_path.endswith('.docx'):
                doc = docx.Document(file_path)
                return "\n\n".join(paragraph.text for paragraph in doc.paragraphs)
            else:
                return "[DOC text extraction requires conversion to DOCX]"
        
        except ImportError:
            return "[Word document text extraction requires python-docx]"
    
    def _extract_spreadsheet_text(self, file_path: str) -> str:
        """
        Extract text from spreadsheet.
        
        Args:
            file_path: Path to spreadsheet
            
        Returns:
            Extracted text
        """
        if file_path.endswith('.csv'):
            try:
                import csv
                
                rows = []
                with open(file_path, 'r', newline='') as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        rows.append(",".join(row))
                
                return "\n".join(rows)
            
            except Exception as e:
                return f"[CSV parsing error: {str(e)}]"
        
        else:
            try:
                import pandas as pd
                
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                    return df.to_string()
                else:
                    return "[Excel text extraction requires pandas and openpyxl]"
            
            except ImportError:
                return "[Spreadsheet text extraction requires pandas and openpyxl]"
    
    def _list_archive_contents(self, file_path: str) -> str:
        """
        List contents of archive file.
        
        Args:
            file_path: Path to archive
            
        Returns:
            List of archive contents
        """
        if file_path.endswith('.zip'):
            try:
                import zipfile
                
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                
                return "Archive contents:\n" + "\n".join(file_list)
            
            except Exception as e:
                return f"[ZIP parsing error: {str(e)}]"
        
        elif file_path.endswith(('.tar', '.gz')):
            try:
                import tarfile
                
                with tarfile.open(file_path, 'r:*') as tar_ref:
                    file_list = tar_ref.getnames()
                
                return "Archive contents:\n" + "\n".join(file_list)
            
            except Exception as e:
                return f"[TAR parsing error: {str(e)}]"
        
        else:
            return "[Unsupported archive format]"
    
    def extract_text_chunk(self, file_path: str, chunk_size: int = 4000) -> List[str]:
        """
        Extract text from file in chunks.
        
        Args:
            file_path: Path to file
            chunk_size: Maximum chunk size in characters
            
        Returns:
            List of text chunks
        """
        result = self.process_file(file_path)
        
        if result["error"] or not result["extracted_text"]:
            return [result.get("error", "No text could be extracted")]
        
        text = result["extracted_text"]
        
        # Split into chunks
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i+chunk_size])
        
        return chunks
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            File metadata
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        filename = os.path.basename(file_path)
        ext = self.get_file_extension(filename)
        mime_type = self.get_mime_type(filename)
        
        # Get file stats
        stats = os.stat(file_path)
        
        return {
            "filename": filename,
            "extension": ext,
            "mime_type": mime_type,
            "content_type": self._get_content_type(mime_type),
            "file_size": stats.st_size,
            "created_time": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "accessed_time": datetime.fromtimestamp(stats.st_atime).isoformat(),
            "is_supported": self.is_supported_file_type(filename)
        }
    
    def batch_process_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process multiple files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Dictionary of file paths to processing results
        """
        results = {}
        
        for file_path in file_paths:
            results[file_path] = self.process_file(file_path)
        
        return results
