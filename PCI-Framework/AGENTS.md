# Agent Developer Guide

## Precision Contract Intent Framework (PCI Framework)

Execution and Deployment Guide

---

## Overview

This document explains how to execute the Precision Contract Intent Framework (PCI Framework):

1. On a local machine
2. In a cloud environment
3. As an Apify Actor

The framework is implemented in Python and designed to run asynchronously using `asyncio` and `httpx`.

---

## 1. Local Execution

### Requirements

* Python 3.9+
* pip
* Virtual environment (recommended)

### Step 1: Clone the Repository

```
git clone <repository-url>
cd <repository-folder>
```

### Step 2: Create Virtual Environment

```
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### Step 3: Install Dependencies

```
pip install -r requirements.txt
```

If a requirements file is not available, install manually:

```
pip install apify httpx beautifulsoup4 lxml
```

### Step 4: Configure Input

Create an `input.json` file:

```
{
  "startUrl": "https://example.com",
  "maxDepth": 1,
  "categoriesToInclude": []
}
```

### Step 5: Run the Agent

```
python main.py
```

The output will be stored via Apify's local storage mechanism and pushed as structured JSON.

---

## 2. Cloud Execution

The framework can be deployed on any Python-compatible cloud infrastructure.

### Supported Environments

* AWS EC2
* AWS ECS / Fargate
* Google Cloud Run
* Azure App Service
* Docker-based environments

### Option A: Direct VM Deployment

1. Provision a Linux VM
2. Install Python 3.9+
3. Clone repository
4. Install dependencies
5. Run using:

```
python main.py
```

### Option B: Docker Deployment

Create a `Dockerfile`:

```
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir apify httpx beautifulsoup4 lxml

CMD ["python", "main.py"]
```

Build and run:

```
docker build -t pci-framework .
docker run pci-framework
```

For scalable deployments, integrate with:

* Kubernetes
* Cloud Run
* ECS Fargate

---

## 3. Deployment as an Apify Actor

PCI Framework is natively compatible with Apify.

### Step 1: Install Apify CLI

```
npm install -g apify-cli
```

Login:

```
apify login
```

### Step 2: Initialize Actor (if not already initialized)

```
apify init
```

Choose Python Actor template.

### Step 3: Ensure Required Files

Your project should contain:

1. main.py
2. requirements.txt
3. .actor/actor.json:

```
{
  "name": "precision-contract-intent-framework",
  "title": "PCI Framework: FAQ to Chatbot Conversation Flow Generator",
  "description": "Automatically converts website FAQs & Scraped data into chatbot-ready JSON conversation flows.",
  "version": "0.0.1",
  "buildTag": "latest",
  "meta": {
    "templateId": "python-start"
  },
  "input": "./input_schema.json",
  "output": "./output_schema.json",
  "datasetSchema": "./dataset_schema.json"
}

```

4. `requirements.txt`:

```
apify
httpx
beautifulsoup4
lxml
```

### Step 4: Test Locally in Apify Environment

```
apify run
```

### Step 5: Deploy to Apify Cloud

```
apify push
```

Once deployed:

1. Navigate to Apify Console
2. Open the Actor
3. Provide input JSON
4. Run the Actor
5. Retrieve output from dataset or key-value store

---

## Environment Variables

If extended for production, consider defining:

* REQUEST_TIMEOUT
* USER_AGENT
* MAX_DEPTH
* STRICT_MODE

These can be configured via:

* `.env` files
* Apify Actor settings
* Cloud environment variables

---

## Execution Flow Summary

1. Actor receives structured input
2. Asynchronous crawl begins
3. FAQ content extracted
4. Navigation intents generated
5. Conversation tree constructed
6. Structured JSON output stored and pushed

---

## Operational Notes

* Deterministic output depends on consistent site structure
* Dynamic JavaScript-heavy sites may require headless browser integration
* Ensure compliance with target site terms of service
* Use appropriate crawl depth to avoid excessive traversal

---

Precision Contract Intent Framework (PCI Framework)
Enterprise Deterministic Conversational Infrastructure
