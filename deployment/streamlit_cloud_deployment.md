# Streamlit Cloud Configuration

This file contains instructions for deploying the Multi-AI application to Streamlit Cloud.

## Prerequisites

1. A GitHub account
2. A Streamlit Cloud account (sign up at https://streamlit.io/cloud)
3. The Multi-AI application repository on GitHub

## Deployment Steps

1. Log in to Streamlit Cloud using your GitHub account
2. Click "New app" button
3. Select the GitHub repository "ALL.AI"
4. Set the main file path to "frontend/app.py"
5. Configure the following secrets in the Streamlit Cloud dashboard:
   - OPENAI_API_KEY
   - GEMINI_API_KEY
   - HUGGINGFACE_API_KEY
   - OPENROUTER_API_KEY
   - CLAUDE_API_KEY
   - LLAMA_API_KEY
   - BOTPRESS_API_KEY
6. Click "Deploy" to launch the application

## Advanced Configuration

For advanced configuration, you can create a `.streamlit/config.toml` file in the repository with the following content:

```toml
[theme]
primaryColor = "#0E639C"
backgroundColor = "#1E1E1E"
secondaryBackgroundColor = "#252526"
textColor = "#FAFAFA"
```

This will ensure the dark theme is applied consistently in the Streamlit Cloud deployment.

## Updating the Deployment

The deployment will automatically update whenever changes are pushed to the GitHub repository.

## Custom Domain (Optional)

To use a custom domain with your Streamlit Cloud deployment:

1. Go to the app settings in Streamlit Cloud
2. Click on "Custom domain"
3. Follow the instructions to configure your domain's DNS settings
4. Verify ownership and apply the custom domain
