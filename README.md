# AVIS — AI Career Platform

AVIS is an AI-powered career platform that transforms a static CV into a continuously evolving professional identity.

Users can upload their CV, build a structured professional profile, provide new information through Training, interact with an AI Digital Twin through Chat, improve their CV, discover relevant career opportunities, track applications, and receive job alerts.

> AVIS is not simply a chatbot that reads a CV. It is a continuously evolving AI-powered professional identity and career assistant.

## MVP Status

- **Project status:** MVP implementation
- **Development duration:** 9 days
- **Methodology:** Agile
- **Backend:** Python + FastAPI
- **Frontend:** React + Vite
- **Database:** PostgreSQL
- **Automation:** n8n
- **Core:** AI Digital Twin + Career Agent

## Product Vision

AVIS helps people turn their evolving skills and experiences into a living AI-powered professional identity and connect that identity with relevant career opportunities.

```text
CV
 ↓
AI Analysis
 ↓
Professional Profile
 ↓
Training
 ↓
Approved AI Knowledge
 ↓
Chat
 ↓
AI Digital Twin
 ↓
CV Writer
 ↓
Career Agent
 ↓
Job Matching
 ↓
Career Applications
 ↓
Email Job Alerts
```

## Problem

Students, graduates, developers, and young professionals often struggle to:

- Present themselves professionally.
- Keep their CV up to date.
- Explain their skills and projects effectively.
- Organize professional information.
- Discover relevant career opportunities.
- Understand which opportunities match their abilities.
- Track applications consistently.
- Avoid missing new opportunities.

People continuously gain new skills, complete projects, participate in hackathons, and earn certifications. However, their CV and professional profile often remain unchanged.

AVIS connects:

```text
What a person can do
        ↓
What their professional profile communicates
        ↓
What opportunities they discover
```

## Core Features

### Authentication

- User registration.
- Login and logout.
- Account management.
- Protected application routes.

### CV Upload and Analysis

Users can upload a CV for AI-powered analysis. AVIS extracts structured information such as names, summaries, education, skills, experience, projects, certifications, and achievements. Extracted information is stored in the user’s professional profile for review and editing.

### My Profile

The professional profile represents the user’s current professional identity and may include personal information, education, skills, experience, projects, certifications, achievements, career goals, and career preferences.

### Training

**Training** is where users provide AVIS with additional information about themselves. Training may capture new experiences, skills, projects, achievements, certifications, current learning, career goals, interests, professional preferences, and challenges overcome.

Users can review, edit, approve, and delete information. Only approved information becomes part of the user’s permanent AI knowledge.

> The feature must be called `Training`. Do not rename it to “Teach My AI”, “Teach AI”, “AI Training Center”, or “Twin Training”.

### AI Knowledge

AVIS maintains structured professional knowledge based on the CV, professional profile, approved Training information, and other approved user information.

Users should be able to view, edit, and delete stored knowledge, manage privacy, and control AI visibility.

The AI must not invent personal information. If information is unavailable, AVIS must clearly state that it does not have that information.

### Chat

Chat allows users to interact with their AI Digital Twin.

Example route:

```text
/chat/{username}
```

The AI can answer questions about the user’s skills, projects, education, experience, current learning, and career goals. The interface should display a notice similar to:

> This conversation is with an AI representation based on information provided by the user.

### CV Writer

CV Writer turns new experiences into professional CV content. Users can accept, edit, reject, add content to their CV, or add content to their profile. AVIS must not automatically modify the official CV without user approval.

### Career Agent

The Career Agent discovers relevant opportunities based on skills, education, experience, projects, career goals, preferred roles, location, and job type. Each opportunity can include a match percentage, matching skills, potential skill gaps, and an explanation of why it was recommended.

### Career Applications

Career Applications helps users manage discovered opportunities. Supported statuses are:

```text
Recommended
Saved
Applied
Interview
Rejected
Archived
```

The MVP does not automatically submit applications. Users open the original application URL through `Apply Now`.

### Job Alerts

Job Alerts notify users about relevant opportunities through email. Users can configure alert status, frequency, minimum match percentage, preferred roles, job types, locations, and remote opportunities.

## Main Navigation

```text
AVIS

Overview
My Profile
My CV
CV Writer
Training
Chat
Career Applications
Job Alerts
Settings
```

These names should remain unchanged across the frontend, documentation, and product demonstrations.

## Technology Stack

### Frontend

- React.
- Vite.
- Reusable components.
- Responsive layouts.
- Light and dark themes.

Suggested structure:

```text
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── services/
│   ├── hooks/
│   ├── contexts/
│   └── App.jsx
├── public/
├── package.json
└── vite.config.js
```

### Backend

- Python.
- FastAPI.
- REST APIs.
- Authentication and authorization.
- AI service integration.
- PostgreSQL persistence.

Suggested structure:

```text
backend/
├── app/
│   ├── main.py
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   ├── repositories/
│   └── ai/
├── tests/
├── requirements.txt
└── .env
```

### Database

PostgreSQL entities may include:

```text
users
profiles
skills
education
experience
projects
certifications
cvs
training_sessions
training_answers
ai_memory
conversations
messages
jobs
job_matches
applications
alerts
notifications
```

### Automation

n8n is used for scheduled workflows:

```text
Scheduled Job Search
        ↓
Job Filtering
        ↓
Job Matching
        ↓
Save Opportunities
        ↓
Email Alert
```

## System Flow

```text
Create Account
      ↓
Upload CV
      ↓
AI Analysis
      ↓
Professional Profile
      ↓
Training
      ↓
Approved AI Knowledge
      ↓
Chat
      ↓
AI Digital Twin
      ↓
CV Writer
      ↓
Career Agent
      ↓
Job Matching
      ↓
Career Applications
      ↓
Email Alert
      ↓
Original Application URL
```

## API Structure

### Authentication

```http
POST /api/auth/register
POST /api/auth/login
```

### Profile

```http
GET /api/profile
PUT /api/profile
```

### CV

```http
POST /api/cv/upload
GET /api/cv
PUT /api/cv
```

### Training

```http
POST /api/training
GET /api/training
PUT /api/training/{id}
DELETE /api/training/{id}
```

### Chat

```http
POST /api/chat
GET /api/chat/history
GET /api/users/{username}/twin
```

### Jobs

```http
GET /api/jobs
GET /api/jobs/{id}
```

### Applications

```http
GET /api/applications
POST /api/applications
PUT /api/applications/{id}
```

### Alerts

```http
GET /api/alerts
PUT /api/alerts
```

## Local Development

### Prerequisites

- Python 3.10 or later.
- Node.js and npm.
- PostgreSQL.
- Git.
- n8n, if running automation locally.

### Clone the Repository

```bash
git clone <repository-url>
cd avis
```

### Backend Setup

```bash
cd backend
python -m venv venv
```

On macOS or Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\\Scripts\\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Example backend configuration:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/avis
SECRET_KEY=replace-with-a-secure-secret
AI_API_KEY=replace-with-your-ai-provider-key
CORS_ORIGINS=http://localhost:5173
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000` and API documentation is available at `http://localhost:8000/docs`.

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
```

Configure the backend URL:

```env
VITE_API_URL=http://localhost:8000/api
```

Start the Vite development server:

```bash
npm run dev
```

The frontend runs at `http://localhost:5173`.

### Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE avis;
```

Run migrations when configured:

```bash
alembic upgrade head
```

### n8n Setup

Start n8n locally:

```bash
n8n start
```

Configure the workflow:

```text
Schedule Trigger
      ↓
Find Jobs
      ↓
Filter Jobs
      ↓
Calculate Match
      ↓
Save Opportunities
      ↓
Check Alert Preferences
      ↓
Send Email
```

Never commit email credentials, API keys, or webhook secrets to the repository.

## Environment Variables

Backend:

```env
DATABASE_URL=
SECRET_KEY=
AI_API_KEY=
CORS_ORIGINS=
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
```

Frontend:

```env
VITE_API_URL=
```

Configure n8n credentials through n8n credentials or environment configuration.

## Testing

Backend tests:

```bash
cd backend
pytest
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

Test the core journey:

```text
Register
 ↓
Login
 ↓
Upload CV
 ↓
Review Profile
 ↓
Approve Information
 ↓
Complete Training
 ↓
Approve Training Information
 ↓
Open Chat
 ↓
Generate CV Content
 ↓
View Job Matches
 ↓
Save Application
 ↓
Receive Alert
```

## Definition of Done

A feature is complete only when:

- Code is implemented.
- API is connected.
- Database is working.
- Validation is added.
- Error handling is included.
- Loading and empty states are included.
- The feature is tested.
- The feature is responsive.
- Code has been reviewed.
- The pull request has been merged.

## Agile Workflow

```text
BACKLOG
   ↓
TODO
   ↓
IN PROGRESS
   ↓
CODE REVIEW
   ↓
TESTING
   ↓
DONE
```

Every task should include an owner, priority, acceptance criteria, deadline, dependencies, and test status.

## Git Workflow

Branches:

```text
main
develop
```

Feature branches:

```text
feature/auth
feature/profile
feature/cv
feature/training
feature/chat
feature/jobs
feature/applications
feature/alerts
```

Workflow:

```text
Issue
 ↓
Feature Branch
 ↓
Development
 ↓
Testing
 ↓
Pull Request
 ↓
Code Review
 ↓
Merge
```

Do not develop directly on `main`.

Example:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/training

git add .
git commit -m "Implement Training approval workflow"
git push origin feature/training
```

## UI Design Principles

AVIS supports light mode, dark mode, desktop layouts, tablet layouts, and mobile layouts.

Visual identity:

- Black.
- White.
- Orange.

Orange should primarily be used for borders, outlines, active navigation, focus states, selected elements, important actions, AI indicators, and progress indicators.

The interface should feel modern, premium, professional, minimal, intelligent, clean, and human-centered. Avoid excessive gradients, glassmorphism, neon colors, animations, and decorative elements.

## AI Safety and Data Rules

1. Use only approved professional information for personalized responses.
2. Never invent personal information.
3. Clearly state when information is unavailable.
4. Do not automatically modify the official CV.
5. Require user approval before permanent knowledge updates.
6. Allow users to edit or delete stored information.
7. Protect authentication credentials and API keys.
8. Avoid exposing private user information through public routes.
9. Validate AI-generated structured output before saving it.
10. Keep job recommendations explainable.

## 9-Day Roadmap

| Day | Primary goal | Required output |
|---|---|---|
| 1 | Foundation | Repository, database, API skeleton, design system |
| 2 | Authentication and profile | Registration, login, onboarding, profile |
| 3 | CV pipeline | Upload, extraction, structured CV data |
| 4 | Training | Training, approval, knowledge updates |
| 5 | Chat | Grounded responses from approved knowledge |
| 6 | Career Agent | Jobs, matching logic, match explanations |
| 7 | Applications and alerts | Status workflow and n8n email automation |
| 8 | Integration and QA | Full journey testing and bug fixing |
| 9 | Demo and delivery | Deployment, demo account, presentation |

## MVP Success Criteria

The MVP is successful when a user can:

```text
Create account
        ↓
Upload CV
        ↓
AVIS analyzes CV
        ↓
Professional profile is created
        ↓
User provides new information through Training
        ↓
User approves the information
        ↓
AI knowledge is updated
        ↓
User opens Chat
        ↓
AI Digital Twin responds
        ↓
User adds a new experience
        ↓
CV Writer creates improved CV content
        ↓
Career Agent finds relevant jobs
        ↓
Jobs receive match scores
        ↓
Jobs appear in Career Applications
        ↓
User receives an email alert
        ↓
User opens the original application URL
```

## Project Principle

Do not think of AVIS as:

> A chatbot that reads a CV.

Think of AVIS as:

> A continuously evolving AI-powered professional identity and career assistant.

The CV is only the starting point. Training allows the user to add information continuously, AI Knowledge maintains professional context, Chat represents that context, CV Writer keeps professional documents updated, and Career Agent connects the user with relevant opportunities.

## Final Product Statement

AVIS helps people turn their evolving skills and experiences into a living AI-powered professional identity while continuously connecting that identity with relevant career opportunities.
