# Deployment Guide

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

### Option 1: Streamlit Cloud

[Streamlit Cloud](https://streamlit.io/cloud) provides an easy way to deploy Streamlit applications.

1. **Push your code to GitHub**
   - Ensure your repository is public or you have access to Streamlit Cloud with private repositories

2. **Set up Secrets**
   - In Streamlit Cloud, add your API keys as secrets
   - These will be available as environment variables to your application

3. **Deploy the Application**
   - Connect your GitHub repository to Streamlit Cloud
   - Select the `frontend/app.py` file as the entry point
   - Click "Deploy"

### Option 2: Docker Deployment

1. **Create a Dockerfile**
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   EXPOSE 8501

   CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build the Docker Image**
   ```bash
   docker build -t multi-ai-app .
   ```

3. **Run the Docker Container**
   ```bash
   docker run -p 8501:8501 --env-file .env multi-ai-app
   ```

4. **Access the Application**
   - Open your web browser and navigate to `http://localhost:8501`

### Option 3: Heroku Deployment

1. **Create a Procfile**
   ```
   web: streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Add a runtime.txt file**
   ```
   python-3.9.13
   ```

3. **Deploy to Heroku**
   ```bash
   heroku create multi-ai-app
   git push heroku main
   ```

4. **Configure Environment Variables**
   - Set your API keys as environment variables in the Heroku dashboard or using the Heroku CLI:
   ```bash
   heroku config:set OPENAI_API_KEY=your_openai_api_key
   heroku config:set GEMINI_API_KEY=your_gemini_api_key
   # Add other API keys as needed
   ```

5. **Access the Application**
   - Open your web browser and navigate to the URL provided by Heroku

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

4. **Rate Limiting**
   - Implement rate limiting to prevent abuse
   - Monitor usage to stay within API provider limits

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
