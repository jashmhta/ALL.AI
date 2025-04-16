import os
import streamlit as st
import base64
from pathlib import Path

# Function to convert SVG to PNG for compatibility
def svg_to_png(svg_path, size=24):
    try:
        from cairosvg import svg2png
        png_data = svg2png(url=svg_path, output_width=size, output_height=size)
        return base64.b64encode(png_data).decode('utf-8')
    except ImportError:
        # If cairosvg is not available, return the SVG directly
        with open(svg_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

# Function to load and encode images for model icons
def get_model_icon_html(model_name):
    icon_map = {
        "openai": "openai_icon.svg",
        "claude": "anthropic_icon.svg",
        "gemini": "gemini_icon.svg",
        "llama": "llama_icon.svg",
        "huggingface": "huggingface_icon.svg",
        "openrouter": "openrouter_icon.svg",
        "deepseek": "deepseek_icon.svg",
        "mixture": "mixture_icon.svg",
        "github_gpt4_mini": "openai_icon.svg",
        "github_deepseek": "deepseek_icon.svg",
        "github_llama": "llama_icon.svg",
        "puter": "placeholder.svg"
    }
    
    # Default icon if model-specific icon not found
    icon_file = icon_map.get(model_name.lower(), "placeholder.svg")
    icon_path = os.path.join(os.path.dirname(__file__), "static", "icons", icon_file)
    
    # Use a placeholder if the icon file doesn't exist
    if not os.path.exists(icon_path):
        return f'<div class="model-icon-placeholder">{model_name[0].upper()}</div>'
    
    # Read and encode the image
    if icon_path.endswith('.svg'):
        try:
            encoded_image = svg_to_png(icon_path)
            img_format = 'png'
        except Exception as e:
            # Fallback to direct SVG if conversion fails
            with open(icon_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode()
            img_format = 'svg+xml'
    else:
        with open(icon_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode()
        img_format = Path(icon_path).suffix[1:]  # Get extension without dot
    
    return f'<img src="data:image/{img_format};base64,{encoded_image}" class="model-icon" alt="{model_name} icon">'

# Function to create expandable/collapsible sections
def create_expandable_section(header, content, expanded=False):
    expanded_class = "expanded" if expanded else ""
    return f"""
    <div class="expandable-section">
        <div class="expandable-header" onclick="toggleExpand(this)">
            <div>{header}</div>
            <div class="expand-icon">{'▼' if expanded else '▶'}</div>
        </div>
        <div class="expandable-content {expanded_class}">
            {content}
        </div>
    </div>
    """

# Function to create a code block with syntax highlighting and copy button
def create_code_block(code, language="python"):
    # Escape HTML characters in code
    code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Add syntax highlighting classes based on language
    highlighted_code = highlight_syntax(code, language)
    
    return f"""
    <div class="code-block-container">
        <div class="code-header">
            <span class="code-language">{language}</span>
            <button class="copy-button" onclick="copyCode(this)">Copy</button>
        </div>
        <pre class="language-{language}">
            <code class="language-{language}">{highlighted_code}</code>
        </pre>
    </div>
    """

# Function to add basic syntax highlighting classes
def highlight_syntax(code, language):
    if language == "python":
        # Very basic Python syntax highlighting
        keywords = ["def", "class", "import", "from", "return", "if", "else", "elif", "for", "while", "try", "except", "with", "as", "in", "not", "and", "or", "True", "False", "None"]
        for keyword in keywords:
            # Only replace whole words, not parts of words
            code = code.replace(f" {keyword} ", f" <span class='token keyword'>{keyword}</span> ")
            code = code.replace(f"\n{keyword} ", f"\n<span class='token keyword'>{keyword}</span> ")
            if code.startswith(f"{keyword} "):
                code = f"<span class='token keyword'>{keyword}</span> " + code[len(keyword)+1:]
        
        # String highlighting (very basic)
        code = code.replace('\"\"\"', '<span class="token string">\"\"\"</span>')
        code = code.replace('\'\'\'', '<span class="token string">\'\'\'</span>')
        
        # Function calls
        import re
        code = re.sub(r'(\w+)(\()', r'<span class="token function">\1</span>\2', code)
        
    elif language == "javascript":
        # Very basic JavaScript syntax highlighting
        keywords = ["function", "const", "let", "var", "return", "if", "else", "for", "while", "try", "catch", "class", "new", "this", "true", "false", "null", "undefined"]
        for keyword in keywords:
            code = code.replace(f" {keyword} ", f" <span class='token keyword'>{keyword}</span> ")
            code = code.replace(f"\n{keyword} ", f"\n<span class='token keyword'>{keyword}</span> ")
            if code.startswith(f"{keyword} "):
                code = f"<span class='token keyword'>{keyword}</span> " + code[len(keyword)+1:]
    
    return code

# Function to create the thinking indicator
def create_thinking_indicator():
    return """
    <div class="thinking-indicator">
        <span>Thinking</span>
        <div class="thinking-dots">
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
        </div>
    </div>
    """

# Function to create the loading indicator
def create_loading_indicator(message="Loading..."):
    return f"""
    <div class="loading-indicator">
        <div class="loading-spinner">
            <div class="spinner-ring"></div>
        </div>
        <div class="loading-message">{message}</div>
    </div>
    """

# Function to create the credit display
def create_credit_display(credits):
    html = '<div class="credit-display"><h4>API Credits</h4>'
    
    for model, amount in credits.items():
        html += f"""
        <div class="credit-item">
            <div class="credit-model">
                {get_model_icon_html(model)}
                <span>{model}</span>
            </div>
            <div class="credit-amount">{amount}</div>
        </div>
        """
    
    html += '</div>'
    return html

# Function to load CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "static", "style.css")
    with open(css_file, "r") as f:
        css = f.read()
    return css

# Function to inject JavaScript for interactivity
def inject_javascript():
    return """
    <script>
    function toggleExpand(element) {
        const content = element.nextElementSibling;
        const icon = element.querySelector('.expand-icon');
        
        if (content.classList.contains('expanded')) {
            content.classList.remove('expanded');
            icon.textContent = '▶';
        } else {
            content.classList.add('expanded');
            icon.textContent = '▼';
        }
    }
    
    function copyCode(button) {
        const codeElement = button.closest('.code-block-container').querySelector('code');
        const textArea = document.createElement('textarea');
        textArea.value = codeElement.textContent.trim();
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        // Show feedback
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    }

    // Add responsive handling for mobile devices
    function adjustForMobile() {
        const isMobile = window.innerWidth < 768;
        const elements = document.querySelectorAll('.model-selection, .chat-container');
        
        elements.forEach(el => {
            if (isMobile) {
                el.classList.add('mobile-view');
            } else {
                el.classList.remove('mobile-view');
            }
        });
    }
    
    // Syntax highlighting for code blocks
    function highlightSyntax() {
        document.querySelectorAll('pre code').forEach((block) => {
            // Add line numbers
            const lines = block.innerHTML.split('\\n');
            let numberedLines = '';
            lines.forEach((line, index) => {
                numberedLines += `<span class="line-number">${index + 1}</span>${line}\\n`;
            });
            block.innerHTML = numberedLines;
        });
    }
    
    // Run on load and resize
    window.addEventListener('load', function() {
        adjustForMobile();
        highlightSyntax();
    });
    window.addEventListener('resize', adjustForMobile);
    </script>
    """

# Function to create model selection interface
def create_model_selection(models, selected_models=None):
    if selected_models is None:
        selected_models = []
    
    html = '<div class="model-selection">'
    
    for model in models:
        selected_class = "selected" if model in selected_models else ""
        html += f"""
        <div class="model-option {selected_class}" data-model="{model}">
            {get_model_icon_html(model)}
            <span>{model}</span>
        </div>
        """
    
    html += '</div>'
    return html

# Function to create chat message bubbles
def create_chat_message(content, role="assistant", model=None, expandable=True):
    role_class = "user-message" if role == "user" else "assistant-message"
    model_info = f'<div class="model-info">{get_model_icon_html(model)} {model}</div>' if model else ''
    
    # Process code blocks in content
    import re
    code_pattern = r'```(\w+)?\n(.*?)\n```'
    
    def replace_code_block(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        return create_code_block(code, lang)
    
    # Replace code blocks with syntax highlighted versions
    content = re.sub(code_pattern, replace_code_block, content, flags=re.DOTALL)
    
    if expandable and role == "assistant":
        return create_expandable_section(
            f"{model_info}<div class='message-preview'>{content[:100]}{'...' if len(content) > 100 else ''}</div>",
            f"<div class='{role_class}-content'>{content}</div>",
            expanded=True
        )
    else:
        return f"""
        <div class="{role_class}">
            {model_info if role == "assistant" else ""}
            {content}
        </div>
        """

# Function to create file upload area
def create_file_upload_area():
    return """
    <div class="file-upload-area">
        <div class="upload-icon">📁</div>
        <div class="upload-text">Drag and drop files here or click to upload</div>
        <div class="upload-subtext">Supports all file formats</div>
    </div>
    """
