# AVIS — AI Career Platform

> **Project Status:** MVP Implementation  
> **Development Duration:** 9 Days  
> **Methodology:** Agile  
> **Backend:** Python + FastAPI  
> **Frontend:** React + Vite  
> **Database:** PostgreSQL  
> **Automation:** n8n  
> **Core:** AI Digital Twin + Career Agent

---

## 1. Project Overview

**AVIS** is an AI-powered personal career platform that creates a continuously evolving professional AI identity for each user.

AVIS starts by analyzing the user's CV and professional profile. The user can then continuously provide new information about their skills, projects, experiences, achievements, career goals, and learning through the **Training** section.

This information is used to improve the AI's understanding of the user.

The user can interact with their AI representation through **Chat**, improve their CV through **CV Writer**, discover relevant opportunities through the **Career Agent**, manage opportunities through **Career Applications**, and receive relevant job alerts through email.

AVIS is not simply a chatbot that reads a CV. It is designed as a continuously evolving AI-powered professional identity and career assistant.

---

# 2. Problem Statement

Many students, graduates, developers, and young professionals have valuable skills and experiences but struggle to:

- Present themselves professionally.
- Keep their CV up to date.
- Explain their skills and projects effectively.
- Organize their professional information.
- Discover relevant career opportunities.
- Know which opportunities match their abilities.
- Track career opportunities consistently.
- Avoid missing new opportunities.

There is a gap between:

```text
What a person can actually do
        ↓
What their CV/profile communicates
        ↓
What opportunities they discover
```

A person may learn a new technology, complete a project, participate in a hackathon, or earn a certification, while their CV remains unchanged.

### Core Problem

> People often have valuable and continuously changing skills and experiences, but they lack an intelligent system that keeps their professional identity updated and consistently connects them with relevant career opportunities.

---

# 3. Solution

AVIS connects the user's professional development with career opportunities.

```text
CV
 ↓
AI Analysis
 ↓
Professional Profile
 ↓
Training
 ↓
AI Knowledge
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

The goal is to create a single evolving professional identity instead of disconnected CVs, project descriptions, and job searches.

---

# 4. Product Vision

> **AVIS helps people turn their evolving skills and experiences into a living AI-powered professional identity and connect that identity with relevant career opportunities.**

---

# 5. Core Features

## 5.1 Authentication

Users can:

- Register.
- Login.
- Logout.
- Manage their account.

---

## 5.2 CV Upload

The user uploads their CV.

AVIS analyzes the CV and extracts structured information such as:

- Name.
- Professional summary.
- Education.
- Skills.
- Experience.
- Projects.
- Certifications.
- Achievements.

The extracted information is stored in the user's professional profile.

---

## 5.3 Professional Profile

The profile represents the user's current professional identity.

Possible information:

```text
Personal Information
Education
Skills
Experience
Projects
Certifications
Achievements
Career Goals
Career Preferences
```

---

# 6. Training

### Important terminology

The feature is called:

> **Training**

Do not rename it to:

- Teach My AI
- Teach AI
- AI Training Center
- Twin Training

Training is where users provide AVIS with additional information about themselves.

Example:

```text
AI:
Tell me about something new you have recently learned.

User:
I recently learned FastAPI and built a backend API.

AI:
What did you build the API for?

User:
I built it for a career platform.

AI:
What technologies did you use?
```

The system should ask adaptive follow-up questions when more context is useful.

Training may collect:

- New experiences.
- Skills.
- Projects.
- Achievements.
- Certifications.
- Current learning.
- Career goals.
- Interests.
- Professional preferences.
- Challenges overcome.

Users should be able to:

- Review information.
- Edit information.
- Delete information.
- Approve information.

Only approved information should become part of the user's permanent AI knowledge.

---

# 7. AI Knowledge / Memory

AVIS maintains structured professional knowledge about the user.

Information can originate from:

```text
CV
 +
Profile
 +
Training
 +
Approved User Information
```

The AI uses this information to generate personalized responses.

Users should have control over their stored information.

They should be able to:

- View knowledge.
- Edit knowledge.
- Delete knowledge.
- Manage privacy.
- Control AI visibility.

### Important AI Rule

The AI must not invent personal information.

If information is unavailable, the AI should clearly state that it does not have that information.

---

# 8. Chat

The sidebar feature is called:

> **Chat**

Do not call the feature:

- Twin AI.
- My AI Twin.
- Twin Assistant.

Chat is where the user interacts with their AI Digital Twin.

### Route

```text
/chat/{username}
```

Example:

```text
/chat/jack
```

"Jack" is only a mock/example username and should not be treated as a specific real person.

The AI can answer questions based on approved professional knowledge.

Example questions:

```text
Tell me about yourself.

What are your strongest skills?

What projects have you worked on?

What is your educational background?

What experience do you have?

What are you currently learning?

What are your career goals?
```

The interface should clearly communicate that the responses come from an AI representation based on user-provided information.

Example notice:

> This conversation is with an AI representation based on information provided by the user.

---

# 9. CV Writer

CV Writer helps users turn new experiences into professional CV content.

Example:

### User

> I recently participated in an AI hackathon where I built a FastAPI backend.

### AVIS

> Participated in an AI-focused hackathon, developing backend services using FastAPI.

The user can:

```text
Accept
Edit
Reject
Add to CV
Add to Profile
```

AVIS must not automatically change the official CV without user approval.

---

# 10.1 Target-Specific CV Generator

AVIS should support generating a **target-specific mini CV** from the user's complete CV.

The user's main CV remains the source of truth and is stored in their profile/storage. When the user wants to apply for a specific opportunity, they can tell AVIS what they are applying for.

Example:

> I want to apply for a Backend Developer position.

AVIS should then:

1. Read the user's complete stored CV and professional knowledge.
2. Analyze the target role, opportunity, or application purpose.
3. Select the most relevant experience, skills, projects, education, and achievements.
4. Generate a focused **mini CV / tailored CV** specifically for that application.
5. Explain why each selected section is relevant.
6. Identify missing or weak areas that could reduce the user's eligibility.
7. Suggest skills, experiences, projects, certifications, or improvements that would strengthen the application.

### Example Flow

```text
Complete CV + AI Knowledge
            ↓
      Target Opportunity
            ↓
     Relevance Analysis
            ↓
    Tailored Mini CV
            ↓
   Eligibility / Gap Analysis
            ↓
 Suggested Improvements
```

### Example

User:

> I want to apply for a Junior Backend Developer position.

AVIS analyzes the full CV and produces:

```text
TAILORED CV

Professional Summary
Relevant Skills
Relevant Experience
Relevant Projects
Relevant Education
Relevant Certifications
```

It should prioritize backend-related information instead of copying the entire CV.

AVIS can also provide:

```text
Match: 82%

Strong areas:
✓ Python
✓ FastAPI
✓ PostgreSQL
✓ Backend projects

Potential gaps:
△ Limited professional backend experience
△ No cloud certification listed

Suggestions:
• Add measurable results from backend projects.
• Highlight API development experience.
• Consider adding relevant deployment/cloud experience.
```

### Important Principle

The tailored CV must be generated **from the user's existing information**. AVIS must not invent experience, skills, qualifications, or achievements.

The user must review and approve the tailored CV before using it for an application.

This feature connects **CV Writer + Career Agent + Career Applications** and allows AVIS to help users present the most relevant version of their professional profile for each opportunity.

---

# 10. Career Agent

The Career Agent discovers relevant career opportunities based on the user's:

- Skills.
- Education.
- Experience.
- Projects.
- Career goals.
- Preferred roles.
- Location.
- Job type.

The system calculates or estimates a match score.

Example:

```text
Junior Backend Developer

94% Match

Python       ✓
FastAPI      ✓
PostgreSQL   ✓
Backend      ✓
```

AVIS should also explain:

> Why AVIS recommended this opportunity.

---

# 11. Career Applications

The sidebar section must be:

> **Career Applications**

Users can view discovered opportunities here.

Each opportunity may contain:

- Job title.
- Company.
- Location.
- Employment type.
- Match percentage.
- Matching skills.
- Potential skill gaps.
- Deadline.
- Original application URL.
- Application status.

Application statuses:

```text
Recommended
Saved
Applied
Interview
Rejected
Archived
```

The user can open the original application URL through:

> **Apply Now**

The 9-day MVP does not need to automatically submit applications.

---

# 12. Job Alerts

The sidebar section is:

> **Job Alerts**

When AVIS finds relevant opportunities, it can notify the user through email.

Example:

```text
Subject:
3 New Opportunities Match Your Career Profile

Backend Developer — 94%
AI Intern — 89%
Software Developer — 86%

[View Career Applications]
```

Users should be able to configure:

- Enable/disable alerts.
- Alert frequency.
- Minimum match percentage.
- Preferred roles.
- Job types.
- Locations.
- Remote opportunities.

---

# 13. UI Design

AVIS must support both:

- Light Mode.
- Dark Mode.

## Visual Identity

Primary visual language:

> **Black + White + Orange**

### Light Mode

- Light background.
- Dark text.
- White cards.
- Orange accents.
- Orange outlines.

### Dark Mode

- Black/charcoal background.
- Light text.
- Dark cards.
- Orange accents.
- Orange outlines.

Orange should mainly be used for:

- Outlines.
- Borders.
- Active navigation.
- Focus states.
- Selected elements.
- Important actions.
- AI indicators.
- Progress indicators.

Avoid making the entire interface orange.

### Design Style

The UI should feel:

- Modern.
- Premium.
- Professional.
- Minimal.
- Intelligent.
- Clean.
- Human-centered.

Avoid excessive:

- Gradients.
- Glassmorphism.
- Neon colors.
- Animations.
- Decorative elements.

---

# 14. Main Sidebar

Use these exact navigation names:

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

Do not rename these features.

Desktop:

- Persistent sidebar.

Tablet:

- Collapsible sidebar.

Mobile:

- Navigation drawer or bottom navigation.

---

# 15. Technology Stack

## Frontend

```text
React
Vite
```

Use reusable components.

Suggested frontend areas:

```text
components/
pages/
layouts/
services/
hooks/
```

---

## Backend

```text
Python
FastAPI
```

Do not use Node.js or Express for the backend.

Suggested backend structure:

```text
backend/
├── app/
│   ├── main.py
│   ├── config/
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

---

## Database

```text
PostgreSQL
```

Potential entities:

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

---

## AI Layer

The AI architecture should support:

- CV analysis.
- Structured information extraction.
- Training.
- Personal knowledge retrieval.
- AI Chat.
- CV writing.
- Job matching.

RAG/vector search can be introduced where useful.

---

## Automation

Use:

```text
n8n
```

for workflows such as:

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

---

# 16. Suggested API Structure

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
```

## Profile

```text
GET /api/profile
PUT /api/profile
```

## CV

```text
POST /api/cv/upload
GET /api/cv
PUT /api/cv
```

## Training

```text
POST /api/training
GET /api/training
PUT /api/training/{id}
DELETE /api/training/{id}
```

## Chat

```text
POST /api/chat
GET /api/chat/history
GET /api/users/{username}/twin
```

## Jobs

```text
GET /api/jobs
GET /api/jobs/{id}
```

## Applications

```text
GET /api/applications
POST /api/applications
PUT /api/applications/{id}
```

## Alerts

```text
GET /api/alerts
PUT /api/alerts
```

---

# 17. System Flow

```text
                    AVIS
                     │
                     ▼
              Create Account
                     │
                     ▼
                 Upload CV
                     │
                     ▼
               AI Analysis
                     │
                     ▼
            Professional Profile
                     │
                     ▼
                  Training
                     │
                     ▼
               AI Knowledge
                     │
                     ▼
                   Chat
                     │
                     ▼
               AI Digital Twin
                     │
                     ▼
                CV Writer
                     │
                     ▼
              Career Agent
                     │
                     ▼
              Job Matching
                     │
                     ▼
          Career Applications
                     │
                     ▼
               Job Alert
                     │
                     ▼
            Application URL
```

---

# 18. 9-Day Agile Development Roadmap

## Day 1 — Foundation

### Goal

Set up the complete development foundation.

Tasks:

- Finalize requirements.
- Create GitHub repository.
- Create Agile project board.
- Define database schema.
- Define API structure.
- Initialize React + Vite.
- Initialize FastAPI.
- Connect PostgreSQL.
- Create base UI.
- Establish AVIS design system.

### Deliverable

```text
Frontend ✓
Backend ✓
Database ✓
GitHub ✓
Design system ✓
API structure ✓
```

---

## Day 2 — Authentication & Profile

### Backend

Implement:

```text
POST /api/auth/register
POST /api/auth/login

GET /api/profile
PUT /api/profile
```

Create initial database tables.

### Frontend

Build:

- Register.
- Login.
- Onboarding.
- Profile.
- Sidebar.
- Dashboard shell.

### Deliverable

```text
Register
   ↓
Login
   ↓
Profile
   ↓
Dashboard
```

---

## Day 3 — CV

### Backend

Implement:

```text
POST /api/cv/upload
GET /api/cv
PUT /api/cv
```

Flow:

```text
CV Upload
   ↓
Text Extraction
   ↓
AI Analysis
   ↓
Structured Information
   ↓
PostgreSQL
```

### Frontend

Build:

- CV upload.
- Upload progress.
- CV preview.
- Extracted information.
- CV editing.

### Deliverable

A user uploads a CV and AVIS creates structured professional information.

---

## Day 4 — Training

### Backend

Implement:

```text
POST /api/training
GET /api/training
PUT /api/training/{id}
DELETE /api/training/{id}
```

### Frontend

Build the Training interface.

The system should ask questions and collect new professional information.

### Deliverable

Approved Training information becomes part of the user's AI knowledge.

---

## Day 5 — Chat / AI Digital Twin

### Major MVP milestone

Implement:

```text
POST /api/chat
GET /api/chat/history
GET /api/users/{username}/twin
```

Architecture:

```text
User Question
      ↓
FastAPI
      ↓
Retrieve User Knowledge
      ↓
LLM
      ↓
Personalized Response
```

Frontend route:

```text
/chat/{username}
```

### Deliverable

A working AI Digital Twin that responds using the user's stored professional information.

---

## Day 6 — Career Agent & Job Matching

Create:

```text
jobs
job_matches
applications
```

Implement job APIs and matching logic.

Example:

```text
User Profile
      +
Job Requirements
      ↓
Match Engine
      ↓
Match Score
```

### Deliverable

Relevant jobs appear with match scores.

---

## Day 7 — Career Applications & Email Alerts

Build the Career Applications workflow.

Create n8n automation:

```text
Schedule
   ↓
Find Jobs
   ↓
Filter Jobs
   ↓
Match Users
   ↓
Save Opportunities
   ↓
Send Email
```

### Deliverable

A matching job appears in Career Applications and can trigger an email alert.

---

## Day 8 — Integration & QA

### Feature freeze

Do not add major features.

Test the entire system:

```text
Register
 ↓
Upload CV
 ↓
Profile
 ↓
Training
 ↓
Chat
 ↓
CV Writer
 ↓
Job Matching
 ↓
Career Applications
 ↓
Email Alert
```

Fix:

- Critical bugs.
- API failures.
- Database issues.
- AI response problems.
- UI inconsistencies.
- Responsive issues.
- Loading states.
- Error states.

---

## Day 9 — Demo & Delivery

Do not introduce major new features.

Focus on:

- Final testing.
- Bug fixes.
- Deployment.
- Demo account.
- Presentation.
- Product story.
- Architecture explanation.
- Community impact.

---

# 19. Team Structure

For a 5-person team:

## Member 1 — Product Owner / Scrum Lead

Responsible for:

- Requirements.
- User stories.
- Sprint planning.
- Coordination.
- Documentation.
- Acceptance criteria.
- Final demo.

## Member 2 — Frontend Developer

Responsible for:

- React + Vite.
- Dashboard.
- Profile.
- CV.
- CV Writer.
- Training.
- Chat.
- Career Applications.
- Job Alerts.
- Responsive UI.

## Member 3 — Backend Developer

Responsible for:

- Python.
- FastAPI.
- PostgreSQL.
- Authentication.
- REST APIs.
- Profile.
- CV APIs.
- Training APIs.
- Chat APIs.
- Job APIs.

## Member 4 — AI Integration Developer

Responsible for:

- CV analysis.
- AI knowledge.
- Training intelligence.
- Chat.
- RAG/personal knowledge retrieval.
- CV rewriting.
- Job matching.

## Member 5 — Career Agent / Automation / QA

Responsible for:

- Job discovery.
- Job matching.
- Career Applications.
- n8n.
- Email alerts.
- API testing.
- Integration testing.
- Final QA.

---

# 20. Agile Workflow

Use:

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

Every task should have:

- Owner.
- Priority.
- Acceptance criteria.
- Deadline.

---

# 21. GitHub Workflow

Branches:

```text
main
develop

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

---

# 22. Definition of Done

A task is considered complete only when:

- [ ] Code implemented.
- [ ] API connected.
- [ ] Database working.
- [ ] UI completed.
- [ ] Validation added.
- [ ] Error handling added.
- [ ] Tested.
- [ ] Responsive.
- [ ] Code reviewed.
- [ ] Pull request merged.

---

# 23. MVP Success Criteria

At the end of the 9-day sprint, the team should be able to demonstrate one complete working journey:

```text
User creates account
        ↓
Uploads CV
        ↓
AVIS analyzes CV
        ↓
Professional profile created
        ↓
User provides new information through Training
        ↓
AI knowledge updated
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
User receives email alert
        ↓
User opens original application URL
```

If this journey works reliably, the 9-day MVP has achieved its primary goal.

---

# 24. Product Principle

Do not think of AVIS as:

> "A chatbot that reads a CV."

Think of AVIS as:

> **A continuously evolving AI-powered professional identity and career assistant.**

The CV is only the starting point.

**Training** allows the user to continuously add information.

**AI Knowledge** maintains professional context.

**Chat** allows the AI Digital Twin to represent that context.

**CV Writer** keeps the professional document updated.

**Career Agent** connects the user's profile with opportunities.

**Career Applications** organizes those opportunities.

**Job Alerts** help users avoid missing relevant opportunities.

---

# 25. Final Product Statement

> **AVIS helps people turn their evolving skills and experiences into a living AI-powered professional identity while continuously connecting that identity with relevant career opportunities.**

---

## Implementation Priority

When time becomes limited, prioritize:

```text
1. Authentication
2. CV Upload + Analysis
3. Training
4. AI Knowledge
5. Chat / AI Digital Twin
6. Job Matching
7. Career Applications
8. Email Alerts
9. CV Writer
10. Advanced features
```

The team should prioritize a **working end-to-end MVP** over building many incomplete features.
