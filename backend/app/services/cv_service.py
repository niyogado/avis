import json
import re
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from fastapi import UploadFile

from app.config.settings import settings
from app.models.ai_memory import AIMemory
from app.repositories.cv import CVRepository
from app.repositories.profile import ProfileRepository
from app.utils.storage import Storage

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None


SECTION_HEADERS = {
    'full_name': ['full name'],
    'headline': ['headline', 'title', 'professional title'],
    'summary': ['summary', 'profile', 'about'],
    'skills': ['technical skills', 'skills', 'core skills', 'tools', 'technologies', 'tech stack', 'technical stack'],
    'soft_skills': ['soft skills', 'strengths', 'core competencies', 'competencies'],
    'experience': ['experience', 'professional experience', 'work experience'],
    'projects': ['projects', 'selected projects'],
    'education': ['education', 'academic qualifications'],
    'certifications': ['certifications', 'licenses', 'awards'],
}

STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'for', 'with', 'from', 'into', 'of', 'to', 'in', 'on', 'at',
    'by', 'as', 'is', 'are', 'your', 'their', 'our', 'this', 'that', 'role', 'skills', 'experience',
    'years', 'year', 'developer', 'engineer', 'manager', 'analyst', 'specialist', 'senior', 'junior',
    'lead', 'team', 'data', 'business', 'product'
}


def _normalize_keyword(value: str) -> str:
    value = re.sub(r'[^a-z0-9]+', ' ', (value or '').lower()).strip()
    if not value:
        return ''
    synonyms = {
        'postgres': 'postgresql',
        'postgresql': 'postgresql',
        'sqlserver': 'sql server',
        'sql-server': 'sql server',
        'ci cd': 'ci/cd',
        'cicd': 'ci/cd',
        'etl': 'etl',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'llm': 'llm',
    }
    return synonyms.get(value, value)


def _split_name(full_name: str | None) -> tuple[str, str]:
    clean = (full_name or '').strip()
    if not clean:
        return '', ''
    parts = clean.split()
    if len(parts) == 1:
        return parts[0], ''
    return parts[0], ' '.join(parts[1:])


def _extract_document_text(filename: str, content: bytes, content_type: str | None = None) -> str:
    lower_name = (filename or '').lower()
    media_type = (content_type or '').lower()

    if media_type.startswith('text/') or lower_name.endswith('.txt'):
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('latin-1', errors='ignore')

    if lower_name.endswith('.docx') or media_type.endswith('wordprocessingml.document'):
        try:
            with zipfile.ZipFile(BytesIO(content)) as zf:
                xml = zf.read('word/document.xml')
            root = ET.fromstring(xml)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = [
                ''.join(node.text or '' for node in para.findall('.//w:t', ns))
                for para in root.findall('.//w:p', ns)
            ]
            return '\n'.join(p for p in paragraphs if p.strip())
        except Exception:
            return content.decode('latin-1', errors='ignore')

    if lower_name.endswith('.pdf') or media_type == 'application/pdf':
        if PdfReader is not None:
            try:
                reader = PdfReader(BytesIO(content))
                pages = []
                for page in reader.pages:
                    page_text = page.extract_text() or ''
                    pages.append(page_text)
                return '\n'.join(pages)
            except Exception:
                pass
        return content.decode('latin-1', errors='ignore')

    return content.decode('utf-8', errors='ignore')


def _ensure_extracted_text(filename: str, content: bytes, content_type: str | None = None) -> str:
    text = re.sub(r'\n{3,}', '\n\n', _extract_document_text(filename, content, content_type)).strip()
    if not text:
        raise ValueError("AVIS could not extract readable text from this CV. Try a text-based PDF or DOCX file.")
    return text


def _unique_strings(items: Any, limit: int = 25) -> list[str]:
    if isinstance(items, str):
        items = [items]
    if not isinstance(items, list):
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, str):
            continue
        value = re.sub(r'\s+', ' ', item).strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
        if len(result) >= limit:
            break
    return result


def parse_ai_json_response(raw_response: str) -> dict[str, Any]:
    raw = (raw_response or '').strip()
    if raw.startswith('```'):
        raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.I)
        raw = re.sub(r'\s*```$', '', raw)
    match = re.search(r'\{.*\}', raw, flags=re.S)
    if match:
        raw = match.group(0)
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("EjoChat returned a non-object JSON response.")
    return parsed


def validate_cv_analysis(payload: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    evidence_input = payload.get('cv_evidence') if isinstance(payload.get('cv_evidence'), dict) else payload
    interpretation_input = payload.get('ai_interpretation') if isinstance(payload.get('ai_interpretation'), dict) else payload

    evidence = {
        'professional_profile': str(
            evidence_input.get('professional_profile')
            or profile.get('summary')
            or profile.get('headline')
            or ''
        ).strip(),
        'skills': _unique_strings(evidence_input.get('skills') or profile.get('skills', []), 30),
        'experience': _unique_strings(evidence_input.get('experience') or profile.get('work_experience', []), 20),
        'education': _unique_strings(evidence_input.get('education') or profile.get('education', []), 20),
        'projects': _unique_strings(evidence_input.get('projects') or profile.get('projects', []), 20),
        'certifications': _unique_strings(evidence_input.get('certifications') or profile.get('certifications', []), 20),
        'career_signals': _unique_strings(evidence_input.get('career_signals'), 20),
    }

    interpretation = {
        'strengths': _unique_strings(interpretation_input.get('strengths'), 20),
        'gaps': _unique_strings(interpretation_input.get('gaps'), 20),
        'career_signals': _unique_strings(interpretation_input.get('career_signals'), 20),
        'career_directions': _unique_strings(
            interpretation_input.get('career_directions') or interpretation_input.get('target_roles'),
            10,
        ),
    }

    if not any(evidence[key] for key in ('professional_profile', 'skills', 'experience', 'education', 'projects', 'certifications')):
        raise ValueError("EjoChat analysis did not contain usable CV evidence.")

    return {
        'cv_evidence': evidence,
        'ai_interpretation': interpretation,
    }


def _section_value(section_map: dict[str, str], labels: list[str]) -> str:
    for label in labels:
        candidates = {label, label.lower(), re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')}
        for candidate in candidates:
            value = section_map.get(candidate)
            if value:
                return value
    return ''


def _split_sections(text: str) -> dict[str, str]:
    cleaned = text.replace('\r', '')
    lines = [line.strip() for line in cleaned.split('\n')]
    sections: dict[str, str] = {}
    current_label = None
    current_lines: list[str] = []

    for line in lines:
        normalized = _normalize_keyword(line)
        matched_label = None
        for label, aliases in SECTION_HEADERS.items():
            if any(_normalize_keyword(alias) == normalized or normalized.startswith(_normalize_keyword(alias) + ':') for alias in aliases):
                matched_label = label
                break
        if matched_label:
            if current_label is not None:
                sections[current_label] = '\n'.join(current_lines).strip()
            current_label = matched_label
            current_lines = []
            continue

        if current_label is not None:
            current_lines.append(line)

    if current_label is not None:
        sections[current_label] = '\n'.join(current_lines).strip()

    return sections


def _parse_list_value(value: str, preserve_case: bool = False, split_on_commas: bool = True) -> list[str]:
    if not value:
        return []

    delimiter = r'\n|;' if not split_on_commas else r'\n|;|,'
    items: list[str] = []
    for chunk in re.split(delimiter, value):
        cleaned = re.sub(r'\s+', ' ', chunk).strip().strip('-•*')
        if cleaned and len(cleaned) > 1:
            items.append(cleaned)

    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.strip() if preserve_case else _normalize_keyword(item)
        if not key:
            continue
        identifier = key.lower()
        if identifier not in seen:
            seen.add(identifier)
            result.append(key)
    return result


def extract_profile_from_text(text: str) -> dict[str, Any]:
    plain = (text or '').strip()
    if not plain:
        return {
            'full_name': '',
            'headline': '',
            'email': '',
            'phone': '',
            'location': '',
            'summary': '',
            'skills': [],
            'soft_skills': [],
            'work_experience': [],
            'projects': [],
            'education': [],
            'certifications': [],
        }

    lines = [line.strip() for line in plain.split('\n') if line.strip()]
    full_name = ''
    if lines:
        first_line = lines[0]
        if not re.search(r'@|\d{3,}', first_line) and len(first_line.split()) <= 5:
            full_name = first_line

    email_match = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', plain)
    phone_match = re.search(r'(?:\+?\d[\d\s().+-]{7,}\d)', plain)
    headline = ''
    for line in lines[1:8]:
        if line.lower().startswith(('email:', 'phone:', 'location:', 'website:', 'linkedin:')):
            continue
        if re.search(r'\b(Engineer|Developer|Manager|Analyst|Designer|Scientist|Architect|Consultant|Leader|Specialist|Advisor|Director)\b', line, re.I):
            headline = line
            break

    location = ''
    location_match = re.search(r'(?i)\b(?:location|based in|city|country)\s*[:\-]?\s*([A-Za-z ,.-]+)', plain)
    if location_match:
        location = location_match.group(1).strip(', .;')
    if not location:
        for line in lines:
            if re.search(r',\s*(UK|US|USA|Canada|India|Europe|EMEA|APAC|London|Paris|Berlin|Singapore|Dubai|Remote)', line, re.I):
                location = line
                break

    section_map = _split_sections(plain)
    skills_raw = _section_value(section_map, SECTION_HEADERS['skills'])
    soft_raw = _section_value(section_map, SECTION_HEADERS['soft_skills'])
    experience_raw = _section_value(section_map, SECTION_HEADERS['experience'])
    projects_raw = _section_value(section_map, SECTION_HEADERS['projects'])
    education_raw = _section_value(section_map, SECTION_HEADERS['education'])
    certifications_raw = _section_value(section_map, SECTION_HEADERS['certifications'])

    skills = _parse_list_value(skills_raw)
    if not skills:
        for candidate in lines:
            if re.search(r'(?i)(python|sql|postgres|aws|docker|kubernetes|javascript|react|java|azure|tableau|airflow|etl)', candidate):
                skills.extend([part.strip() for part in re.split(r'[,;]|\s*\|\s*', candidate) if part.strip()])
    skills = [s for s in skills if s and len(s) <= 80]

    soft_skills = _parse_list_value(soft_raw, preserve_case=True)
    work_experience = _parse_list_value(experience_raw)
    projects = _parse_list_value(projects_raw)
    education = _parse_list_value(education_raw, preserve_case=True, split_on_commas=False)
    certifications = _parse_list_value(certifications_raw, preserve_case=True, split_on_commas=False)

    summary = ' '.join(part for part in [headline, ' '.join(skills[:5]), ' '.join(soft_skills[:3])])
    summary = re.sub(r'\s+', ' ', summary).strip()

    profile = {
        'full_name': full_name,
        'headline': headline,
        'email': email_match.group(1) if email_match else '',
        'phone': phone_match.group(0).strip() if phone_match else '',
        'location': location,
        'summary': summary,
        'skills': [item.strip() for item in skills],
        'soft_skills': [item.strip() for item in soft_skills],
        'work_experience': [item.strip() for item in work_experience],
        'projects': [item.strip() for item in projects],
        'education': [item.strip() for item in education],
        'certifications': [item.strip() for item in certifications],
    }

    if not profile['full_name'] and profile['email']:
        profile['full_name'] = profile['email'].split('@')[0].replace('.', ' ').title()

    if not profile['headline'] and lines:
        profile['headline'] = lines[1] if len(lines) > 1 else ''

    return profile


def _tokenize(value: str) -> set[str]:
    tokens = set()
    for token in re.split(r'[^a-z0-9]+', _normalize_keyword(value)):
        if token and token not in STOPWORDS:
            tokens.add(token)
    return tokens


def match_profile_to_target(profile: dict[str, Any], job_title: str | None = None, job_description: str | None = None) -> dict[str, Any]:
    profile_skills = {_normalize_keyword(skill) for skill in profile.get('skills', [])}
    soft_skills = {_normalize_keyword(skill) for skill in profile.get('soft_skills', [])}
    target_text = ' '.join(filter(None, [job_title or '', job_description or '']))
    target_tokens = _tokenize(target_text)
    skill_cands = set(target_tokens)

    matched_skills = sorted(profile_skills & skill_cands, key=len)
    soft_matches = sorted(soft_skills & skill_cands, key=len)

    required_keywords = sorted(target_tokens, key=lambda word: (-len(word), word))[:15]
    missing_skills = [keyword for keyword in required_keywords if keyword not in profile_skills and keyword not in soft_skills]

    title_tokens = _tokenize(job_title or '')
    title_overlap = sorted(profile_skills & title_tokens, key=len)

    score = 0
    if matched_skills:
        overlap_ratio = len(matched_skills) / max(1, len(target_tokens))
        score += min(60, int(overlap_ratio * 100 * 1.7))
    if title_overlap:
        score += 15
    if profile.get('headline') and (job_title or '').lower() in (profile.get('headline') or '').lower():
        score += 10
    if profile.get('work_experience') or profile.get('experience'):
        score += 15
    if matched_skills and len(matched_skills) >= 3:
        score += 10
    score = max(0, min(100, score))

    strong_areas = matched_skills[:8] or title_overlap[:8] or ['relevant experience and transferable skills']
    recommendations = []
    if missing_skills:
        recommendations.append(f"Add evidence for the missing keywords: {', '.join(missing_skills[:5])}.")
    if not profile.get('certifications'):
        recommendations.append('Highlight any relevant certifications or credentials to strengthen credibility.')
    if not profile.get('projects'):
        recommendations.append('Add a project example that demonstrates delivery in the target role.')

    if not recommendations:
        recommendations.append('Keep the profile focused on the target role and prioritize the strongest matching experiences.')

    tailored_mini_cv = [
        profile.get('headline') or 'Professional Profile',
        'Core strengths: ' + ', '.join(matched_skills[:6]) if matched_skills else 'Core strengths: relevant industry experience',
        'Experience: ' + ('; '.join(profile.get('work_experience', [])[:2])) if profile.get('work_experience') else 'Experience: demonstrated delivery in relevant domains',
        'Education: ' + ('; '.join(profile.get('education', [])[:2])) if profile.get('education') else '',
    ]

    analysis = {
        'job_title': job_title or '',
        'match_score': score,
        'strong_areas': strong_areas,
        'potential_gaps': missing_skills[:8] or ['No critical gaps detected from the provided job description.'],
        'recommendations': recommendations,
        'tailored_mini_cv': ' | '.join(filter(None, tailored_mini_cv)),
        'search_profile': build_search_profile(profile, job_title=job_title, job_description=job_description),
    }
    if soft_matches:
        analysis['strong_areas'] = sorted(set(strong_areas + soft_matches[:3]), key=str)
    return analysis


def build_search_profile(profile: dict[str, Any], job_title: str | None = None, job_description: str | None = None) -> dict[str, Any]:
    skill_tags = [
        _normalize_keyword(item) for item in profile.get('skills', []) if _normalize_keyword(item)
    ]
    target_title = (job_title or '').strip()
    target_text = ' '.join(filter(None, [job_title or '', job_description or '']))
    tokens = _tokenize(target_text)
    query = ' '.join(sorted(set(skill_tags) | tokens)[:30])

    return {
        'target_role': target_title,
        'skill_tags': [tag for tag in skill_tags if tag][:20],
        'experience_level': 'mid-senior' if profile.get('work_experience') else 'entry-level',
        'search_query': query,
    }


def build_career_intent(
    profile: dict[str, Any],
    current_role: str | None = None,
    target_roles: list[str] | None = None,
    learning_priorities: list[str] | None = None,
    current_intent: str | None = None,
) -> dict[str, Any]:
    def _unique(items: list[str] | tuple[str, ...] | None) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in items or []:
            if not isinstance(item, str):
                continue
            value = item.strip()
            if not value:
                continue
            key = value.lower()
            if key not in seen:
                seen.add(key)
                cleaned.append(value)
        return cleaned

    skill_history = _unique(profile.get('skills', []))
    soft_history = _unique(profile.get('soft_skills', []))
    experience_history = _unique(profile.get('work_experience', []))
    education_history = _unique(profile.get('education', []))
    target_roles_list = _unique(target_roles or [])
    learning_list = _unique(learning_priorities or [])
    explicit_intent = (current_intent or '').strip()
    derived_future_goal = (
        'Move toward ' + ', '.join(target_roles_list[:3]) + '.' if target_roles_list
        else 'Continue building credible evidence and align your experience with the next role you want to target.'
    )

    return {
        'current_role': current_role or profile.get('headline') or '',
        'target_roles': target_roles_list[:5],
        'historical_evidence': {
            'headline': profile.get('headline') or current_role or '',
            'skills': skill_history[:20],
            'soft_skills': soft_history[:10],
            'experience': experience_history[:10],
            'education': education_history[:10],
            'projects': _unique(profile.get('projects', []))[:10],
            'certifications': _unique(profile.get('certifications', []))[:10],
            'source': 'cv',
        },
        'current_intent': explicit_intent,
        'future_goal': derived_future_goal,
        'learning_priorities': learning_list[:10],
        'source_of_truth': 'cv',
        'confidence': 0.8 if skill_history or profile.get('headline') else 0.0,
    }


class CVService:
    def __init__(self, db):
        self.repo = CVRepository(db)
        self.profile_repo = ProfileRepository(db)
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        self.storage = Storage()

    @staticmethod
    def extract_text_from_upload(filename: str, content: bytes, content_type: str | None = None) -> str:
        return _ensure_extracted_text(filename, content, content_type)

    @staticmethod
    def extract_profile_from_text(text: str) -> dict[str, Any]:
        return extract_profile_from_text(text)

    @staticmethod
    def match_profile_to_target(profile: dict[str, Any], job_title: str | None = None, job_description: str | None = None) -> dict[str, Any]:
        return match_profile_to_target(profile, job_title=job_title, job_description=job_description)

    async def save_cv(self, user_id, filename: str, content: bytes, content_type: str | None = None):
        size = str(len(content))
        parsed_text = self.extract_text_from_upload(filename, content, content_type)

        fileobj = BytesIO(content)
        dest_name = f"{user_id}_{filename}"
        path_or_url = self.storage.save(fileobj, dest_name, content_type=content_type)

        cv = await self.repo.create(
            user_id=user_id,
            filename=filename,
            path=path_or_url,
            content_type=content_type,
            size=size,
            extracted_text=parsed_text,
        )

        extracted = self.extract_profile_from_text(parsed_text)
        if extracted.get('full_name') or extracted.get('headline') or extracted.get('summary'):
            existing = await self.profile_repo.get_by_user_id(user_id)
            first_name, last_name = _split_name(extracted.get('full_name'))
            payload = {
                'first_name': first_name or (existing.first_name if existing else ''),
                'last_name': last_name or (existing.last_name if existing else ''),
                'full_name': extracted.get('full_name') or (existing.full_name if existing else ''),
                'headline': extracted.get('headline') or (existing.headline if existing else ''),
                'summary': extracted.get('summary') or (existing.summary if existing else ''),
                'location': extracted.get('location') or (existing.location if existing else ''),
                'phone': extracted.get('phone') or (existing.phone if existing else ''),
            }
            if existing:
                await self.profile_repo.update(existing, **payload)
            else:
                await self.profile_repo.create(user_id=user_id, **payload)

        return cv

    async def get_master_profile(self, user_id):
        return await self.profile_repo.get_by_user_id(user_id)

    async def get_cv_for_user(self, user_id, cv_id):
        return await self.repo.get_for_user(user_id, cv_id)

    async def save_analysis(self, user_id, cv, analysis: dict[str, Any]):
        memory = AIMemory(
            user_id=user_id,
            content=json.dumps(analysis, ensure_ascii=False),
            category='cv_analysis',
            source='cv',
            importance=3,
            is_active=True,
        )
        self.repo.session.add(memory)
        return await self.repo.update_analysis(
            cv,
            analysis_json=analysis,
            status='success',
            error=None,
            analyzed_at=datetime.now(timezone.utc),
        )

    async def mark_analysis_error(self, cv, error: str):
        return await self.repo.update_analysis(
            cv,
            analysis_json=cv.analysis_json,
            status='error',
            error=error,
            analyzed_at=cv.analyzed_at,
        )
