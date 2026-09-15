from app.services.cv_service import extract_profile_from_text, match_profile_to_target, build_career_intent


SAMPLE_CV = '''
Jane Doe
Senior Data Engineer

Email: jane@example.com
Phone: +1 (555) 111-2222
Location: London, UK

Technical Skills:
Python, SQL, PostgreSQL, AWS, Docker, Airflow, CI/CD

Soft Skills:
Leadership, Problem Solving, Communication

Experience:
Senior Data Engineer | Northstar Analytics | 2022-Present
- Built ETL pipelines with Python and SQL
- Improved data warehouse reliability using PostgreSQL and Airflow
- Mentored engineers and coordinated deployments on AWS

Education:
BSc Computer Science, University of London

Certifications:
AWS Certified Data Analytics
'''


def test_extract_profile_from_text_collects_verified_fields():
    profile = extract_profile_from_text(SAMPLE_CV)

    assert profile['full_name'] == 'Jane Doe'
    assert profile['headline'] == 'Senior Data Engineer'
    assert profile['email'] == 'jane@example.com'
    assert profile['phone'] == '+1 (555) 111-2222'
    assert 'python' in profile['skills']
    assert 'postgresql' in profile['skills']
    assert 'aws' in profile['skills']
    assert 'Leadership' in profile['soft_skills']
    assert 'BSc Computer Science, University of London' in profile['education']


def test_match_profile_to_target_returns_score_and_recommendations():
    profile = extract_profile_from_text(SAMPLE_CV)
    analysis = match_profile_to_target(
        profile,
        job_title='Senior Data Engineer',
        job_description='Python SQL Postgres Airflow AWS data pipelines leadership'
    )

    assert 0 <= analysis['match_score'] <= 100
    assert analysis['match_score'] >= 70
    assert analysis['strong_areas']
    assert analysis['potential_gaps']
    assert analysis['recommendations']
    assert analysis['tailored_mini_cv']


def test_build_career_intent_distinguishes_evidence_from_current_goal():
    profile = extract_profile_from_text(SAMPLE_CV)
    intent = build_career_intent(
        profile,
        current_role='Senior Data Engineer',
        target_roles=['Lead Data Engineer', 'Principal Data Engineer'],
        learning_priorities=['AWS architecture', 'team leadership'],
        current_intent='I want to lead data platform engineering at scale.'
    )

    assert intent['current_role'] == 'Senior Data Engineer'
    assert intent['target_roles'] == ['Lead Data Engineer', 'Principal Data Engineer']
    assert 'historical_evidence' in intent
    assert 'current_intent' in intent
    assert 'future_goal' in intent
    assert 'learning_priorities' in intent
    assert intent['current_intent'] == 'I want to lead data platform engineering at scale.'
    assert 'python' in intent['historical_evidence']['skills']
