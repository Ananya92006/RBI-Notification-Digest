# RBI Notification Intelligence Dashboard

## Overview

RBI Notification Intelligence Dashboard is a Python-based project that automatically collects RBI notifications, stores them in a database, classifies them using Google Gemini AI, and presents the results through an interactive web dashboard.

The project helps users quickly understand RBI notifications without reading lengthy regulatory documents. It identifies the category of each notification, determines whether it affects personal finance, estimates the impact level, identifies the target audience, and generates a concise summary.

---
## Dashboard Preview

<img src="assets/Screenshot (752).png" width="100%">
## Features

### RBI Notification Collection

* Scrapes RBI notifications from the official RBI website.
* Extracts notification details such as:

  * Date
  * Title
  * Link
  * Content

### Database Storage

* Stores all notifications in SQLite.
* Prevents duplicate entries.
* Maintains structured historical records.

### Gemini AI Classification

For every notification, Gemini AI automatically determines:

* Category
* Whether it affects personal finance
* Impact level
* Target audience
* Summary
* Explanation

### Supported Categories

* Interest Rates
* Foreign Exchange
* Markets
* Banking Regulations
* Savings Schemes
* Insurance
* Taxes
* Other

### Interactive Dashboard

The Flask dashboard provides:

* Notification search by title
* Gemini-powered notification analysis
* Notification summaries
* Impact levels
* Target audience information
* Links to original RBI notifications

### Dashboard Statistics

The dashboard displays:

* Total Notifications
* Personal Finance Notifications
* High Impact Notifications
* Foreign Exchange Notifications

---

## Technology Stack

### Backend

* Python
* Flask

### Database

* SQLite

### AI

* Google Gemini 2.5 Flash

### Web Scraping

* Requests
* BeautifulSoup

### Frontend

* HTML
* CSS
* Jinja Templates

---

## Project Structure

```text
RBI-Notification-Digest/
│
├── Day1/
│   ├── scraper.py
│   └── rbi.html
│
├── Day2/
│   ├── database.py
│   ├── update_db.py
│   └── queries.py
│
├── Day3/
│   ├── classifier.py
│   ├── gemini_classifier.py
│   └── notifications_balanced.csv
│
├── templates/
│   └── index.html
│
├── app.py
├── finance_digest.db
├── .env
├── requirements.txt
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Ananya92006/RBI-Notification-Digest.git
cd RBI-Notification-Digest
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux/Mac

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Gemini API Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

Get an API key from Google AI Studio.

---

## Running the Project

### Step 1: Populate Database

```bash
python Day1/scraper.py
```

### Step 2: Run Gemini Classification

```bash
python Day3/gemini_classifier.py
```

### Step 3: Launch Dashboard

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Example Dashboard Insights

For each notification, the dashboard displays:

* Category
* Personal Finance Impact
* Impact Level
* Target Audience
* Summary
* Source Link

Example:

| Field           | Value                           |
| --------------- | ------------------------------- |
| Category        | Foreign Exchange                |
| Affects Finance | Yes                             |
| Impact Level    | High                            |
| Target Audience | NRI Depositors                  |
| Summary         | Swap facility for FCNR deposits |

---

## Future Enhancements

* Category Filters
* Charts and Visual Analytics
* Automatic Daily RBI Updates
* Email Notifications
* Advanced AI Summaries
* User Authentication
* Export to CSV/PDF

---

## Learning Outcomes

Through this project:

* Learned web scraping using BeautifulSoup
* Built SQLite database workflows
* Integrated Generative AI using Gemini API
* Developed a Flask web application
* Designed an end-to-end AI-powered information system

---

## Author

Ananya Gupta

Information Technology Student

AI • Data Science • Software Development
