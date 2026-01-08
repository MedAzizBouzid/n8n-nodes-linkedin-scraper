# 🤖 AI-Powered Job Application Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![n8n](https://img.shields.io/badge/n8n-Workflow-FF6D5A.svg)](https://n8n.io/)

An automated workflow system that scrapes LinkedIn jobs, generates personalized cover letters, and creates ATS-friendly CVs tailored to each job posting using AI.

## 📋 Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **🔍 LinkedIn Job Scraping**: Automated job extraction using Playwright
- **📝 AI Cover Letter Generation**: Personalized cover letters using OpenRouter AI
- **📄 LaTeX CV Generation**: ATS-friendly, one-page CVs tailored to job descriptions
- **🔄 n8n Workflow Automation**: Visual workflow builder for easy customization
- **🐳 Docker Support**: Containerized deployment for consistent environments
- **📊 CSV Export**: Structured job data export for further analysis
- **🚀 FastAPI Backend**: High-performance REST API

## 🎬 Demo

```bash
# Example API call
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "Data Scientist",
    "job_location": "France",
    "pages_to_extract": 1
  }'
```

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (version 2.0+) - [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git** - [Install Git](https://git-scm.com/downloads)
- **OpenRouter API Key** (Free tier available) - [Get API Key](https://openrouter.ai/)

### System Requirements

- **OS**: Linux, macOS, or Windows (with WSL2)
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: At least 5GB free
- **Network**: Stable internet connection for scraping

## 📦 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/MedAzizBouzid/n8n-nodes-linkedin-scraper.git
cd n8n-nodes-linkedin-scraper
```

### Step 2: Project Structure

Ensure your project has the following structure:

```
n8n-nodes-linkedin-scraper/
├── docker-compose.yml
├── Dockerfile.scraper
├── n8n_data/
├── scraper/
│   ├── Dockerfile
│   ├── main.py
│   ├── scraper.py
│   └── requirements.txt
└── README.md
```

### Step 3: Build and Start Services

```bash
# Build and start all containers
docker compose up --build -d

# Check if containers are running
docker compose ps
```

You should see two services running:
- `n8n` on port 5678
- `scraper` on port 8000

### Step 4: Verify Installation

```bash
# Check n8n
curl http://localhost:5678

# Check scraper API
curl http://localhost:8000/docs
```

## ⚙️ Configuration

### 1. Access n8n Interface

Open your browser and navigate to:
```
http://localhost:5678
```

On first launch, you'll be prompted to create an admin account.

### 2. Set Up OpenRouter Credentials

1. Go to **Settings** → **Credentials**
2. Click **"Add Credential"**
3. Search for **"OpenRouter"** or **"HTTP Header Auth"**
4. Add your OpenRouter API key:
   - **Name**: `OpenRouter API`
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer YOUR_OPENROUTER_API_KEY`

### 3. Import the Workflow

1. In n8n, click **"Workflows"** → **"Add Workflow"**
2. Click the **three dots (⋮)** → **"Import from File"**
3. Select the `workflow.json` file from the repository
4. Click **"Save"**

### 4. Configure Workflow Nodes

#### Webhook Node (Get form data):
- **Webhook URL**: Will be auto-generated (e.g., `http://localhost:5678/webhook-test/linkedin-scraper`)
- **Method**: POST
- **Path**: `/linkedin-scraper` (or your preferred path)
- **Copy this URL** - you'll need it for the HTML form

**Important**: Copy your webhook URL and update it in `jobs-scraper/input-form.html`:
```javascript
// Find this line in input-form.html:
value="http://localhost:5678/webhook-test/linkedin-scraper"

// Replace with your actual webhook URL from n8n
```

#### HTTP Request Node (Extract LinkedIn jobs):
- **URL**: `http://scraper:8000/scrape`
- **Method**: POST
- **Body**: JSON with `job_name`, `job_location`, `pages_to_extract`

#### OpenRouter Nodes:
- **Credential**: Select the OpenRouter credential you created
- **Model**: `meta-llama/llama-3.2-3b-instruct:free` (or any free model)

## 🚀 Usage

### Method 1: Using the Web Form (Easiest - Recommended)

The project includes a user-friendly HTML form for submitting job applications:

1. **Open the form** in your browser:
   ```bash
   # If running locally
   open jobs-scraper/input-form.html
   
   # Or navigate to:
   file:///path/to/your/project/jobs-scraper/input-form.html
   ```

2. **Configure the webhook URL** in the form:
   - Open `input-form.html` in a text editor
   - Find the line: `value="http://localhost:5678/webhook-test/linkedin-scraper"`
   - Replace it with your actual n8n webhook URL from the workflow

3. **Use the form**:
   - **Upload your profile**: Use the `.txt` or `.md` file with your complete career information
   - **Download/View template**: Click the template buttons to see the required format
   - **Enter job criteria**: Job title, location, and number of pages to scrape (1-5)
   - **Submit**: Click "Start Custom Application Generation"

The form will:
- ✅ Validate all inputs
- ✅ Read your profile file content
- ✅ Send data to your n8n webhook
- ✅ Show success/error messages
- ✅ Retry failed requests automatically

**Template File Format** (`Template.md` provided):
```markdown
JOHN DOE – DATA SCIENTIST

PERSONAL INFORMATION
Full Name: John Doe
Email: john.doe@example.com
Phone: +1-555-123-456
LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
[Your 3-4 sentence career summary]

EDUCATION
- Degree details
- Institution, Year

PROFESSIONAL EXPERIENCE
1. Job Title – Company (Date Range)
   - Key achievements
   - Technologies used

TECHNICAL SKILLS
Programming Languages: Python, Java, etc.
ML & AI: TensorFlow, PyTorch, etc.
Tools: Docker, Git, etc.
```

### Method 2: Using the Webhook (For API Integration)

Send a POST request to your n8n webhook with the candidate profile:

```bash
curl -X POST http://localhost:5678/webhook/YOUR_WEBHOOK_ID \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_profile": "Your complete profile text here...",
    "job_name": "Data Scientist",
    "job_location": "France",
    "pages_to_extract": 1
  }'
```

### Method 3: Direct API Call

Test the scraper API directly:

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "Software Engineer",
    "job_location": "Remote",
    "pages_to_extract": 1
  }'
```

### Method 3: Using the Interactive API Docs

Navigate to:
```
http://localhost:8000/docs
```

Use the Swagger UI to test the endpoints interactively.

## 📚 API Documentation

### Endpoints

#### `POST /scrape`
Scrapes LinkedIn jobs and returns JSON with CSV content.

**Request Body:**
```json
{
  "job_name": "string",
  "job_location": "string",
  "pages_to_extract": 1
}
```

**Response:**
```json
{
  "success": true,
  "total_jobs": 5,
  "results": [
    {
      "title": "Job Title",
      "url": "https://linkedin.com/...",
      "description": "Job description..."
    }
  ],
  "csv_content": "title,url,description\n..."
}
```

#### `POST /scrape-csv`
Scrapes jobs and returns CSV file directly.

**Request Body:** Same as `/scrape`

**Response:** CSV file download

### Response Codes

- `200`: Success
- `500`: Scraper execution failed
- `422`: Invalid request parameters

## 📁 Project Structure

```
n8n-nodes-linkedin-scraper/
├── docker-compose.yml          # Docker services configuration
├── Dockerfile.scraper          # n8n container with dependencies
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore file
├── README.md                   # This file
├── workflow.json               # n8n workflow export
├── n8n_data/                   # n8n persistent data
│   └── (auto-generated)
├── jobs-scraper/               # Web form and templates
│   ├── input-form.html         # User-friendly web form
│   ├── Template.md             # Profile template file
│   └── requirements.txt        # Python dependencies
└── scraper/                    # Job scraper service
    ├── Dockerfile              # Scraper container
    ├── main.py                 # FastAPI application
    ├── scraper.py              # LinkedIn scraper logic
    └── requirements.txt        # Python dependencies
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker compose logs scraper
docker compose logs n8n

# Restart services
docker compose restart
```

#### 2. LinkedIn Scraping Fails

**Issue**: Timeout or no results found

**Solutions**:
- Check your internet connection
- LinkedIn may have rate-limited you - wait 15-30 minutes
- Try a different job search query
- Reduce `pages_to_extract` to 1

#### 3. OpenRouter API Errors

**Issue**: 401 Unauthorized or rate limit errors

**Solutions**:
- Verify your API key is correct in n8n credentials
- Check your OpenRouter account quota at https://openrouter.ai/
- Try a different free model
- Wait for rate limit to reset (usually 1 hour)

#### 4. "No output data returned" in n8n

**Solutions**:
- Check if previous nodes executed successfully
- Verify the CSV parsing code node has no syntax errors
- Check Docker logs for Python errors
- Ensure the scraper found jobs (might be 0 results)

#### 5. Port Already in Use

```bash
# Find and kill process using port 5678 or 8000
lsof -ti:5678 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Or change ports in docker-compose.yml
```

### Debug Mode

Enable verbose logging:

```bash
# View real-time logs
docker compose logs -f scraper

# Check specific container
docker exec -it scraper python --version
docker exec -it scraper ls -la /app/
```

### Reset Everything

If things are completely broken:

```bash
# Stop and remove all containers
docker compose down

# Remove all data (WARNING: deletes n8n workflows!)
rm -rf n8n_data/

# Clean rebuild
docker compose up --build --force-recreate
```

## 🔧 Advanced Configuration

### Custom Scraper Settings

Edit `scraper/scraper.py`:

```python
# Change number of jobs to scrape per page
offers_to_process = job_urls_to_scrape[:10]  # Default is 5

# Adjust timeout
await page.wait_for_selector("selector", timeout=30000)  # 30 seconds
```

### Using Different AI Models

In n8n OpenRouter nodes, you can use:

**Free Models:**
- `meta-llama/llama-3.2-3b-instruct:free`
- `google/gemini-flash-1.5:free`
- `microsoft/phi-3-mini-128k-instruct:free`

**Paid Models (better quality):**
- `anthropic/claude-sonnet-4`
- `openai/gpt-4-turbo`

### Environment Variables

Create a `.env` file:

```env
# n8n Configuration
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_HOST=localhost

# Scraper Configuration
SCRAPER_PORT=8000
OUTPUT_CSV_PATH=/tmp/job_offers_results.csv

# OpenRouter (optional - set in n8n instead)
OPENROUTER_API_KEY=your_key_here
```

Then update `docker-compose.yml` to use it:

```yaml
services:
  scraper:
    env_file:
      - .env
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
cd scraper
pytest

# Lint code
black .
flake8 .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [n8n](https://n8n.io/) - Workflow automation platform
- [Playwright](https://playwright.dev/) - Browser automation
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [OpenRouter](https://openrouter.ai/) - AI model aggregator

## 📧 Contact

For questions or support:
- Open an issue on GitHub
- Email: azizbouzid789@gmail.com
- LinkedIn: [Med Aziz Bouzid](https://linkedin.com/in/mohamed-aziz-bouzid)

## 🗺️ Roadmap

- [ ] Support for more job boards (Indeed, Glassdoor)
- [ ] PDF generation from LaTeX CVs
- [ ] Email automation for applications
- [ ] Database storage for job tracking
- [ ] Web UI for easier configuration
- [ ] Multi-language support
- [ ] Resume parsing from uploaded files

---

**Made with ❤️ by Mohamed Aziz Bouzid**

⭐ Star this repo if you find it helpful!