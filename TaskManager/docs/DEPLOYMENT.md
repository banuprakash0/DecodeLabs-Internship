# Production Deployment Guide

This guide details how to package, containerize, and deploy `TaskManager` in staging and production environments.

---

## 1. Local Environment Setup

### Prerequisites
- Python 3.10 or higher
- Git

### Installation Commands
```powershell
# Clone the repository
git clone https://github.com/your-org/TaskManager.git
cd TaskManager

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

---

## 2. Docker Containerization

Below is the production multi-stage `Dockerfile`:

```dockerfile
# Stage 1: Build & Dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final Minimal Runtime Image
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
```

### Docker Commands

```bash
# Build image
docker build -t taskmanager:latest .

# Run container interactively
docker run -it --name taskmanager_app -v taskmanager_data:/app/data taskmanager:latest
```
