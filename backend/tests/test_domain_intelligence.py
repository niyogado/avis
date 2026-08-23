"""Domain intelligence tests: ANY profession, never hardcoded tech defaults."""
from app.services.domain_intelligence import (
    UserDomain,
    build_search_queries,
    infer_user_domain,
    job_is_out_of_domain,
)


TOURISM_CV = {
    'headline': 'TOURISM & HOSPITALITY',
    'skills': ['Customer service', 'Guest relations', 'Hotel management', 'Communication'],
    'professional_profile': 'Tourism and hospitality student focused on guest services.',
    'experience': ['Receptionist | Kigali Guest House | 2024', 'Tour guide intern'],
    'education': ['Tourism and Travel Management'],
    'career_directions': [],
}

TECH_CV = {
    'headline': 'Software Developer',
    'skills': ['Python', 'React', 'PostgreSQL', 'Docker'],
    'professional_profile': 'Backend developer building APIs with Python and FastAPI.',
    'experience': ['Backend Developer | Tech Co | 2022-Present'],
    'education': ['BSc Computer Science'],
    'career_directions': ['AI Engineering'],
}

NURSE_CV = {
    'headline': 'Clinical Nurse',
    'skills': ['Patient care', 'ICU protocols', 'Ward management'],
    'professional_profile': 'Registered nurse with 4 years of hospital experience.',
    'experience': ['Staff Nurse | Referral Hospital | 2020-Present'],
    'education': ['Nursing diploma'],
    'career_directions': [],
}


def _domain(fields):
    return infer_user_domain(fields)


def test_tourism_cv_infers_hospitality_domain():
    domain = _domain(TOURISM_CV)
    assert domain.cluster == 'tourism_hospitality'
    assert domain.confident
    assert any('hotel' in term or 'touris' in term for term in domain.terms)


def test_tech_cv_infers_tech_domain():
    domain = _domain(TECH_CV)
    assert domain.cluster == 'tech'
    assert domain.confident


def test_empty_context_has_no_domain():
    domain = _domain({})
    assert not domain.confident


def test_tourism_queries_contain_no_tech_defaults():
    queries = build_search_queries({
        'user_confirmation': {},
        'career_intent': {'current_role': 'TOURISM & HOSPITALITY', 'target_roles': [], 'historical_evidence': TOURISM_CV},
        'cv_evidence': TOURISM_CV,
    })
    joined = ' '.join(queries).lower()
    assert queries, 'queries must never be empty'
    # Queries derive from the candidate's OWN evidence (role/titles/study).
    assert any('tourism' in q.lower() or 'receptionist' in q.lower() for q in queries)
    for banned in ('developer', 'software', 'engineer', 'frontend'):
        assert banned not in joined


def test_queries_fall_back_to_own_titles_and_study():
    queries = build_search_queries({
        'user_confirmation': {},
        'career_intent': {'current_role': '', 'target_roles': []},
        'cv_evidence': {
            'skills': [],
            'experience': ['Receptionist | Guest House'],
            'education': ['Tourism and Travel Management'],
        },
    })
    assert queries
    assert all(len(q.split()) <= 5 for q in queries)


def test_golang_job_rejected_for_tourism_candidate():
    domain = _domain(TOURISM_CV)
    rejected, reason = job_is_out_of_domain(
        'Senior Golang Developer',
        'We are looking for a golang engineer to build backend APIs and microservices at scale.',
        domain,
    )
    assert rejected
    assert reason


def test_hotel_receptionist_kept_for_tourism_candidate():
    domain = _domain(TOURISM_CV)
    rejected, _ = job_is_out_of_domain(
        'Hotel Receptionist',
        'Front desk reception role welcoming guests, handling reservations and customer service in our hotel.',
        domain,
    )
    assert not rejected


def test_customer_support_kept_when_skills_overlap():
    domain = _domain(TOURISM_CV)  # CV includes "customer service" skill
    rejected, _ = job_is_out_of_domain(
        'Remote Customer Support Agent',
        'Provide customer service and support to clients by phone and email.',
        domain,
        extra_terms=TOURISM_CV['skills'],
    )
    assert not rejected


def test_software_job_kept_for_tech_candidate():
    domain = _domain(TECH_CV)
    rejected, _ = job_is_out_of_domain(
        'Senior Data Engineer',
        'Build data pipelines with python, sql and airflow on aws.',
        domain,
    )
    assert not rejected


def test_nursing_job_rejected_for_tech_candidate():
    domain = _domain(TECH_CV)
    rejected, reason = job_is_out_of_domain(
        'Ward Nurse',
        'Provide patient care in the hospital ward following clinical protocols.',
        domain,
    )
    assert rejected
    assert reason


def test_unknown_domain_never_rejects():
    assert job_is_out_of_domain('Anything At All', 'Some description.', UserDomain()) == (False, '')
