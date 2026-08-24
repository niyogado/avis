import asyncio
import zipfile
from io import BytesIO

import pytest

from app.services.cv_service import (
    CVService,
    build_career_intent,
    extract_profile_from_text,
    match_profile_to_target,
    validate_cv_analysis,
)


def test_build_career_paths_prioritizes_confirmation_over_inference():
    from app.routes.ai import build_career_paths

    paths = build_career_paths(
        confirmation={'target_roles': ['AI Engineer'], 'primary_role': 'Backend Developer'},
        confirmed_intent='AI Engineering',
        directions=['Video Editor'],
        evidence={
            'skills': ['Python', 'FastAPI', 'PostgreSQL'],
            'experience': ['Built APIs at ACME'],
            'projects': ['Library API'],
            'education': [],
            'certifications': [],
            'achievements': [],
            'target_roles': ['API Developer'],
        },
        interpretation={'gaps': ['Limited production experience']},
        skills=['Python', 'FastAPI', 'PostgreSQL'],
        professional_level='junior',
    )

    labels = [p['label'] for p in paths]
    sources = [p['source'] for p in paths]

    # Confirmed items come first and are never displaced by inference.
    assert labels[0] == 'AI Engineer'
    assert all(sources[i] == 'user_confirmed' for i in range(3))
    assert 'Video Editor' in labels
    assert sources[labels.index('Video Editor')] == 'ai_inferred'
    assert sources[labels.index('API Developer')] == 'cv_supported'

    ai_path = next(p for p in paths if p['label'] == 'AI Engineer')
    assert 'Python' in ai_path['strengths']
    assert any('engineer' in g.lower() or 'evidence' in g.lower() for g in ai_path['evidence_gaps'])
    assert 'Limited production experience' in ai_path['ai_gaps']
    assert ai_path['professional_level'] == 'junior'


def test_build_career_paths_dedupes_and_caps():
    from app.routes.ai import build_career_paths

    paths = build_career_paths(
        confirmation={'target_roles': ['Nurse']},
        confirmed_intent='nurse',
        directions=['Nurse', 'Nurse', 'Tour Guide'] * 5,
        evidence={'skills': [], 'experience': []},
        interpretation={},
        skills=[],
        )
    labels = [p['label'].lower() for p in paths]
    assert len(paths) <= 6
    assert len(labels) == len(set(labels))


def _docx_bytes(text: str) -> bytes:
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body></w:document>'
    )
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
        archive.writestr('word/document.xml', document_xml)
    return buffer.getvalue()


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


def test_extract_docx_returns_readable_text():
    text = CVService.extract_text_from_upload(
        'resume.docx',
        _docx_bytes('Jane Doe Python FastAPI PostgreSQL'),
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    assert 'Jane Doe' in text
    assert 'FastAPI' in text


def test_extract_rejects_empty_and_unsupported_files():
    with pytest.raises(ValueError):
        CVService.extract_text_from_upload('resume.pdf', b'', 'application/pdf')
    with pytest.raises(ValueError):
        CVService.extract_text_from_upload('resume.png', b'not-a-cv', 'image/png')


def test_validate_cv_analysis_rejects_empty_evidence():
    with pytest.raises(ValueError):
        validate_cv_analysis({'cv_evidence': {}, 'ai_interpretation': {}}, {})


def test_validate_cv_analysis_keeps_evidence_separate_from_inference():
    parsed = validate_cv_analysis(
        {
            'cv_evidence': {
                'professional_profile': 'Backend engineer',
                'skills': ['Python', 'FastAPI'],
                'experience': ['Built APIs'],
            },
            'ai_interpretation': {
                'career_directions': ['AI Engineering'],
                'strengths': ['Backend delivery'],
            },
        },
        {},
    )
    assert parsed['cv_evidence']['skills'] == ['Python', 'FastAPI']
    assert parsed['ai_interpretation']['career_directions'] == ['AI Engineering']


def test_format_context_for_ai_includes_evidence_and_intent():
    context = CVService.format_context_for_ai({
        'profile': {'full_name': 'Jane Doe', 'headline': 'Engineer', 'location': 'Kigali'},
        'cv_evidence': {'skills': ['Python'], 'experience': ['FastAPI work'], 'education': [], 'projects': []},
        'ai_interpretation': {'career_directions': ['AI Engineering']},
        'career_intent': {'current_role': 'Engineer'},
        'confirmed_user_intent': 'AI Engineering',
        'training_notes': ['Built an internal tool'],
    })
    assert 'Python' in context
    # User confirmations must be presented as the highest-priority source.
    assert 'USER-CONFIRMED PROFESSIONAL IDENTITY' in context
    assert 'User-confirmed career intent statement: AI Engineering' in context
    # AI inference must be explicitly labeled as not chosen by the user.
    assert 'AI INFERENCE' in context


def test_get_professional_context_prioritizes_user_confirmation():
    async def scenario():
        from app.database.session import AsyncSessionLocal
        from app.services.cv_service import CVService

        user_confirmation = {
            'primary_role': 'Backend Developer',
            'professional_level': 'junior',
            'target_roles': ['AI Engineer'],
            'confirmed_skills': ['Python'],
            'career_interests': [],
            'preferred_locations': ['Kigali'],
            'work_preference': 'remote',
            'confirmed_at': '2026-08-23T00:00:00+00:00',
        }

        class FakeProfile:
            full_name = 'Jane Doe'
            headline = 'Engineer'
            summary = ''
            location = 'Kigali'
            professional_context = dict(user_confirmation)

        service = CVService.__new__(CVService)

        class FakeProfileRepo:
            async def get_by_user_id(self, user_id):
                return FakeProfile()

        service.profile_repo = FakeProfileRepo()

        class FakeRepo:
            session = None  # AITrainingService is replaced below; session unused

        service.repo = FakeRepo()

        async def fake_get_latest_cv(user_id):
            return None

        service.get_latest_cv = fake_get_latest_cv

        async def fake_trainings(user_id, active_only=True):
            return []

        import app.services.training_service as training_module

        original_service = training_module.AITrainingService
        training_module.AITrainingService = lambda db: type(
            'FakeTrainingSvc', (), {'list_trainings': staticmethod(fake_trainings)}
        )()
        try:
            context = await service.get_professional_context('user-1')
        finally:
            training_module.AITrainingService = original_service

        assert context['user_confirmation']['target_roles'] == ['AI Engineer']
        assert context['career_intent']['source_of_truth'] == 'user'
        assert context['career_intent']['target_roles'] == ['AI Engineer']
        # Confirmed skills lead the merged skill list.
        assert context['skills'][0] == 'Python'

    asyncio.run(scenario())

