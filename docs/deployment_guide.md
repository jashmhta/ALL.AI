# Deployment Guide for Multi-AI Application

This document provides instructions for deploying the Multi-AI application both locally and in production environments.

## Local Deployment

### Prerequisites

- Python 3.8+
- API keys for at least one of the supported AI services
- Git (for cloning the repository)

### Steps for Local Deployment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jashmhta/ALL.AI.git
   cd ALL.AI
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   - Create a `.env` file in the root directory
   - Add your API keys (see `docs/api_configuration.md` for details)

4. **Run the Application**
   ```bash
   cd frontend
   streamlit run app.py
   ```

5. **Access the Application**
   - Open your web browser and navigate to `http://localhost:8501`

## Production Deployment

### Option 1: Streamlit Cloud (Recommended)

[Streamlit Cloud](https://streamlit.io/cloud) is the easiest and most reliable way to deploy Streamlit applications.

1. **Prerequisites**
   - A GitHub account
   - A Streamlit Cloud account (sign up at https://streamlit.io/cloud)
   - The Multi-AI application repository on GitHub

2. **Deployment Steps**
   - Log in to Streamlit Cloud using your GitHub account
   - Click "New app" button
   - Select the GitHub repository "ALL.AI"
   - Set the main file path to "frontend/app.py"
   - Configure the following secrets in the Streamlit Cloud dashboard:
     - OPENAI_API_KEY
     - GEMINI_API_KEY
     - HUGGINGFACE_API_KEY
     - OPENROUTER_API_KEY
     - CLAUDE_API_KEY
     - LLAMA_API_KEY
     - BOTPRESS_API_KEY
   - Click "Deploy" to launch the application

3. **Custom Domain (Optional)**
   - Go to the app settings in Streamlit Cloud
   - Click on "Custom domain"
   - Follow the instructions to configure your domain's DNS settings
   - Verify ownership and apply the custom domain

### Option 2: Docker Deployment

1. **Build the Docker Image**
   ```bash
   docker build -t multi-ai-app .
   ```

2. **Run the Docker Container**
   ```bash
   docker run -p 8501:8501 --env-file .env multi-ai-app
   ```

3. **Using Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Option 3: Render

[Render](https://render.com/) is a cloud platform that supports Python applications.

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Configure the service:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0`
4. **Add environment variables for your API keys**
5. **Deploy the service**

### Option 4: Fly.io

[Fly.io](https://fly.io/) is another platform that can host Streamlit applications.

1. **Install the Fly CLI**
2. **Initialize your app:**
   ```bash
   fly launch
   ```
3. **Deploy your app:**
   ```bash
   fly deploy
   ```

## Security Considerations for Deployment

1. **API Key Protection**
   - Never commit API keys to your repository
   - Use environment variables or secrets management
   - Regularly rotate API keys

2. **HTTPS**
   - Ensure your deployment uses HTTPS to encrypt data in transit
   - Most cloud platforms provide this by default

3. **Access Control**
   - Consider adding authentication if your deployment is public
   - Limit access to authorized users

## Monitoring and Maintenance

1. **Logging**
   - Implement logging to track usage and errors
   - Review logs regularly to identify issues

2. **Updates**
   - Keep dependencies updated
   - Check for security vulnerabilities

3. **Backup**
   - Regularly backup any persistent data
   - Test restoration procedures

## Troubleshooting Deployment Issues

1. **Application Not Starting**
   - Check logs for error messages
   - Verify all dependencies are installed
   - Ensure environment variables are set correctly

2. **API Connection Issues**
   - Verify API keys are valid
   - Check network connectivity
   - Ensure API services are available

3. **Performance Issues**
   - Monitor resource usage
   - Consider scaling resources if needed
   - Optimize code for performance
