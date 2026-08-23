import json
import re
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import requests
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

    if not content:
        raise ValueError("The uploaded CV file is empty.")

    if media_type.startswith('text/') or lower_name.endswith('.txt'):
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('latin-1', errors='replace')

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
        except Exception as exc:
            raise ValueError("AVIS could not read this DOCX file. Upload a valid Word document.") from exc

    if lower_name.endswith('.pdf') or media_type == 'application/pdf':
        if PdfReader is None:
            raise ValueError("PDF extraction is unavailable on this server.")
        try:
            reader = PdfReader(BytesIO(content))
            pages = [(page.extract_text() or '') for page in reader.pages]
            return '\n'.join(pages)
        except Exception as exc:
            raise ValueError("AVIS could not extract readable text from this PDF. Try a text-based PDF.") from exc

    raise ValueError("Unsupported CV format. Upload a PDF or DOCX file.")


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


def _repair_truncated_json(raw: str) -> str:
    """Attempt to salvage a JSON object that was truncated mid-stream.

    Avis truncates long generations.  When this happens the response
    typically ends in the middle of a string value or array.  We close the
    last open string, trim trailing commas, and balance brackets/braces so
    that ``json.loads`` can parse at least a partial result.
    """
    repaired = raw

    # If the last character is an open string (odd number of unescaped quotes),
    # add a closing quote.
    quote_count = repaired.count('"') - repaired.count('\\"')
    if quote_count % 2 == 1:
        repaired += '"'

    # Remove a trailing comma that would break JSON parsing.
    repaired = re.sub(r',\s*$', '', repaired.strip())

    # Count open/close brackets and braces to close any that are still open.
    open_braces = repaired.count('{') - repaired.count('}')
    open_brackets = repaired.count('[') - repaired.count(']')

    suffix = ']' * max(0, open_brackets) + '}' * max(0, open_braces)
    repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
    repaired += suffix

    return repaired


def parse_ai_json_response(raw_response: str) -> dict[str, Any]:
    raw = (raw_response or '').strip()
    if raw.startswith('```'):
        raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.I)
        raw = re.sub(r'\s*```$', '', raw)
    match = re.search(r'\{.*\}', raw, flags=re.S)
    if match:
        raw = match.group(0)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Tolerate trailing commas, a common model slip.
        repaired = re.sub(r',(\s*[}\]])', r'\1', raw)
        try:
            parsed = json.loads(repaired)
        except json.JSONDecodeError:
            # Last resort: try to salvage a truncated response.
            salvaged = _repair_truncated_json(raw)
            parsed = json.loads(salvaged)
    if not isinstance(parsed, dict):
        raise ValueError("Avis returned a non-object JSON response.")
    return parsed


# Avis truncates long generations mid-JSON (its proxy injects a
# "be concise" system prompt we cannot change). Short, focused requests
# complete reliably, so the structured analysis is split into small
# segments that are merged back into the full schema afterwards.
CV_ANALYSIS_SYSTEM_PROMPT = (
    "You are the AVIS CV analysis engine. Convert CV text into strict JSON. "
    "Output ONLY one raw JSON object: no markdown, no code fences, no commentary. "
    "Never stop before the closing brace. Completeness beats brevity here. "
    "Double quotes only, no trailing commas. Write every value in English."
)

_CV_SEGMENT_RULES = (
    "Rules: use double quotes; no trailing commas; every value in English; "
    "each array item is a short phrase (max 12 words) supported by the CV; "
    "never invent credentials or employers."
)


def _call_cv_segment(prompt: str, retries: int = 3) -> dict[str, Any]:
    """Send a focused prompt to EjoChat and parse the JSON response.

    Retries with exponential backoff handle transient failures (network,
    HTTP 429 rate-limit, or truncated output).  Each retry uses the same
    prompt; the truncation repair in ``parse_ai_json_response`` is what
    salvages responses that EjoChat cuts short.
    """
    import time
    from app.services.ai_service import chat_with_ai

    last_error: Exception | None = None
    for attempt in range(max(1, retries + 1)):
        try:
            raw = chat_with_ai(prompt, system=CV_ANALYSIS_SYSTEM_PROMPT)
            return parse_ai_json_response(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
        except requests.HTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            last_error = RuntimeError(f"EjoChat HTTP {status}: {exc}") if status else exc
        except requests.RequestException as exc:
            last_error = exc
        except Exception as exc:  # pragma: no cover - catch-all safety net
            last_error = exc

        if attempt < retries:
            time.sleep(min(2 ** attempt, 5))

    if isinstance(last_error, (json.JSONDecodeError, ValueError)):
        raise ValueError(f"Avis returned unusable JSON after retries: {last_error}")
    raise RuntimeError(f"Avis request failed after retries: {last_error}")


_MAX_ITEMS_RULE = "Limit: return at most 3 items per array to avoid truncation."


def analyze_cv_with_ejochat(extracted_text: str) -> dict[str, Any]:
    """Run the structured CV analysis through EjoChat in small segments.

    EjoChat truncates long generations, so the analysis is split into
    focused sub-requests (one or two fields each), each with a small
    output cap.  Results are merged back into the full schema afterwards.
    """
    text_slice = extracted_text[:20000]

    core = _call_cv_segment(
        "Extract ONLY these fields from the CV as JSON:\n"
        '{"professional_profile": "<one string, max 4 sentences>", '
        '"skills": ["..."], "experience": ["..."]}\n'
        f"{_CV_SEGMENT_RULES} {_MAX_ITEMS_RULE}\n\nCV text:\n{text_slice}"
    )
    extra = _call_cv_segment(
        "Extract ONLY these fields from the CV as JSON:\n"
        '{"education": ["..."], "projects": ["..."], "certifications": ["..."]}\n'
        f"{_CV_SEGMENT_RULES} {_MAX_ITEMS_RULE}\n\nCV text:\n{text_slice}"
    )
    signals_1 = _call_cv_segment(
        "Extract ONLY these fields from the CV as JSON:\n"
        '{"achievements": ["..."], "career_signals": ["..."]}\n'
        f"{_CV_SEGMENT_RULES} {_MAX_ITEMS_RULE}\n\nCV text:\n{text_slice}"
    )
    signals_2 = _call_cv_segment(
        "Extract ONLY these fields from the CV as JSON:\n"
        '{"target_roles": ["..."], "insights": ["..."]}\n'
        f"{_CV_SEGMENT_RULES} {_MAX_ITEMS_RULE}\n\nCV text:\n{text_slice}"
    )
    interpretation_raw = _call_cv_segment(
        "Based on the CV, return ONLY a JSON object with key 'ai_interpretation' "
        "holding these arrays of short strings: strengths, gaps, "
        "career_signals, career_directions, insights. Return at most 2 items "
        "in each array. These are inferences, not confirmed user choices.\n"
        f"{_CV_SEGMENT_RULES}\n\nCV text:\n{text_slice}"
    )

    interpretation = interpretation_raw.get('ai_interpretation')
    if not isinstance(interpretation, dict):
        interpretation = interpretation_raw

    return {
        'cv_evidence': {
            'professional_profile': core.get('professional_profile') or '',
            'skills': core.get('skills') or [],
            'experience': core.get('experience') or [],
            'education': extra.get('education') or [],
            'projects': extra.get('projects') or [],
            'certifications': extra.get('certifications') or [],
            'achievements': signals_1.get('achievements') or [],
            'career_signals': signals_1.get('career_signals') or [],
            'target_roles': signals_2.get('target_roles') or [],
            'insights': signals_2.get('insights') or [],
        },
        'ai_interpretation': {
            'strengths': interpretation.get('strengths') or [],
            'gaps': interpretation.get('gaps') or [],
            'career_signals': interpretation.get('career_signals') or [],
            'career_directions': interpretation.get('career_directions') or [],
            'insights': interpretation.get('insights') or [],
        },
    }


def validate_cv_analysis(payload: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    evidence_input = payload.get('cv_evidence') if isinstance(payload.get('cv_evidence'), dict) else payload
    interpretation_input = payload.get('ai_interpretation') if isinstance(payload.get('ai_interpretation'), dict) else payload

    raw_profile = evidence_input.get('professional_profile') or ''
    if isinstance(raw_profile, list):
        # Some model runs return the profile as bullet strings; join them
        # instead of stringifying the whole list with brackets.
        raw_profile = ' '.join(str(part).strip() for part in raw_profile if str(part).strip())
    evidence = {
        'professional_profile': str(raw_profile).strip(),
        'skills': _unique_strings(evidence_input.get('skills'), 30),
        'experience': _unique_strings(evidence_input.get('experience'), 20),
        'education': _unique_strings(evidence_input.get('education'), 20),
        'projects': _unique_strings(evidence_input.get('projects'), 20),
        'certifications': _unique_strings(evidence_input.get('certifications'), 20),
        'achievements': _unique_strings(evidence_input.get('achievements'), 20),
        'career_signals': _unique_strings(evidence_input.get('career_signals'), 20),
        'target_roles': _unique_strings(evidence_input.get('target_roles'), 10),
        'insights': _unique_strings(evidence_input.get('insights'), 20),
    }
    if not evidence['professional_profile']:
        evidence['professional_profile'] = str(profile.get('summary') or profile.get('headline') or '').strip()
    if not evidence['skills']:
        evidence['skills'] = _unique_strings(profile.get('skills', []), 30)
    if not evidence['experience']:
        evidence['experience'] = _unique_strings(profile.get('work_experience', []), 20)
    if not evidence['education']:
        evidence['education'] = _unique_strings(profile.get('education', []), 20)
    if not evidence['projects']:
        evidence['projects'] = _unique_strings(profile.get('projects', []), 20)
    if not evidence['certifications']:
        evidence['certifications'] = _unique_strings(profile.get('certifications', []), 20)

    interpretation = {
        'strengths': _unique_strings(interpretation_input.get('strengths'), 20),
        'gaps': _unique_strings(interpretation_input.get('gaps'), 20),
        'career_signals': _unique_strings(interpretation_input.get('career_signals'), 20),
        'career_directions': _unique_strings(
            interpretation_input.get('career_directions') or interpretation_input.get('target_roles'),
            10,
        ),
        'insights': _unique_strings(interpretation_input.get('insights'), 20),
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

    async def get_latest_cv(self, user_id):
        cvs = await self.repo.list_for_user(user_id)
        return cvs[0] if cvs else None

    def read_original_file(self, cv) -> bytes:
        return self.storage.read(cv.path)

    def get_document_page_count(self, filename: str, content: bytes, content_type: str | None = None) -> int | None:
        lower_name = (filename or '').lower()
        media_type = (content_type or '').lower()
        if PdfReader is None:
            return None
        if not (lower_name.endswith('.pdf') or media_type == 'application/pdf'):
            return None
        try:
            reader = PdfReader(BytesIO(content))
            return len(reader.pages)
        except Exception:
            return None

    def render_docx_preview(self, content: bytes) -> str:
        try:
            import mammoth
        except Exception as exc:
            raise ValueError("DOCX preview is unavailable on this server.") from exc
        try:
            result = mammoth.convert_to_html(BytesIO(content))
            html = (result.value or '').strip()
        except Exception as exc:
            raise ValueError("AVIS could not render this DOCX file for preview.") from exc
        if not html:
            raise ValueError("AVIS could not render this DOCX file for preview.")
        return html

    async def get_professional_context(self, user_id) -> dict[str, Any]:
        from app.services.training_service import AITrainingService

        profile = await self.profile_repo.get_by_user_id(user_id)
        cv = await self.get_latest_cv(user_id)
        analysis = cv.analysis_json if cv and isinstance(cv.analysis_json, dict) else {}
        evidence = analysis.get('cv_evidence') if isinstance(analysis.get('cv_evidence'), dict) else {}
        interpretation = analysis.get('ai_interpretation') if isinstance(analysis.get('ai_interpretation'), dict) else {}
        career_intent = analysis.get('career_intent') if isinstance(analysis.get('career_intent'), dict) else {}
        profile_data = analysis.get('profile') if isinstance(analysis.get('profile'), dict) else {}

        # USER-CONFIRMED professional identity (highest priority source).
        raw_confirmation = getattr(profile, 'professional_context', None) if profile else None
        user_confirmation = raw_confirmation if isinstance(raw_confirmation, dict) else {}

        trainings = await AITrainingService(self.repo.session).list_trainings(user_id, active_only=True)
        confirmed_intent = ''
        training_notes = []
        for item in trainings:
            if item.category == 'user_intent' and not confirmed_intent:
                confirmed_intent = item.content.strip()
            if item.category != 'cv_analysis':
                training_notes.append(f"{item.title}: {item.content}")

        # Source priority for intent text:
        # user confirmation (primary role / target roles) > confirmed training note > CV analysis intent.
        confirmation_targets = user_confirmation.get('target_roles') or []
        confirmation_primary = user_confirmation.get('primary_role') or ''
        if not confirmed_intent:
            confirmed_intent = (career_intent.get('current_intent') or '').strip()

        evidence_skills = evidence.get('skills') or profile_data.get('skills') or []
        experience = evidence.get('experience') or profile_data.get('work_experience') or []
        confirmed_skills = user_confirmation.get('confirmed_skills') or []
        # Confirmed skills first (they are verified by the user), then remaining evidence.
        merged_skills = list(confirmed_skills) + [
            skill for skill in evidence_skills
            if str(skill).strip().lower() not in {str(s).strip().lower() for s in confirmed_skills}
        ]

        return {
            'profile': {
                'full_name': (profile.full_name if profile else '') or profile_data.get('full_name') or '',
                'headline': (profile.headline if profile else '') or profile_data.get('headline') or '',
                'summary': (profile.summary if profile else '') or evidence.get('professional_profile') or '',
                'location': (profile.location if profile else '') or '',
            },
            'cv': {
                'id': str(cv.id) if cv else None,
                'filename': cv.filename if cv else None,
                'analyzed': bool(analysis),
                'extracted_text_available': bool(cv and (cv.extracted_text or '').strip()),
            } if cv else None,
            'user_confirmation': user_confirmation,
            'cv_evidence': evidence,
            'ai_interpretation': interpretation,
            'career_intent': {
                **career_intent,
                'current_intent': confirmed_intent,
                'target_roles': confirmation_targets or career_intent.get('target_roles') or [],
                'source_of_truth': 'user' if (confirmed_intent or confirmation_targets or confirmation_primary) else career_intent.get('source_of_truth') or 'cv',
            },
            'skills': merged_skills,
            'experience': experience,
            'training_notes': training_notes[:8],
            'confirmed_user_intent': confirmed_intent,
        }

    @staticmethod
    def format_context_for_ai(context: dict[str, Any]) -> str:
        evidence = context.get('cv_evidence') or {}
        interpretation = context.get('ai_interpretation') or {}
        profile = context.get('profile') or {}
        intent = context.get('career_intent') or {}
        confirmed = (context.get('confirmed_user_intent') or '').strip()
        user_confirmation = context.get('user_confirmation') or {}

        lines = [
            "USER-CONFIRMED PROFESSIONAL IDENTITY (highest priority; overrides everything below):",
            f"- Primary role: {user_confirmation.get('primary_role') or 'not confirmed yet'}",
            f"- Professional level: {user_confirmation.get('professional_level') or 'not confirmed yet'}",
            f"- Target roles: {', '.join(user_confirmation.get('target_roles') or []) or 'not confirmed yet'}",
            f"- Confirmed skills: {', '.join(user_confirmation.get('confirmed_skills') or []) or 'not confirmed yet'}",
            f"- Career interests: {', '.join(user_confirmation.get('career_interests') or []) or 'not confirmed yet'}",
            f"- Preferred locations: {', '.join(user_confirmation.get('preferred_locations') or []) or 'not confirmed yet'}",
            f"- Work preference: {user_confirmation.get('work_preference') or 'not confirmed yet'}",
            "",
            "CV EVIDENCE (facts found in the document):",
            f"Profile: {profile.get('full_name') or 'Unknown'} | {profile.get('headline') or 'No headline'} | {profile.get('location') or 'Location unknown'}",
            f"CV evidence skills: {', '.join(evidence.get('skills') or context.get('skills') or []) or 'none extracted'}",
            f"CV evidence experience: {'; '.join((evidence.get('experience') or [])[:6]) or 'none extracted'}",
            f"CV evidence education: {'; '.join(evidence.get('education') or []) or 'none extracted'}",
            f"CV evidence projects: {'; '.join((evidence.get('projects') or [])[:4]) or 'none extracted'}",
        ]

        ai_lines = (
            ', '.join(interpretation.get('career_directions') or interpretation.get('strengths') or []) or 'none'
        )
        lines.append(f"AI INFERENCE (possible directions, NOT the user's choice): {ai_lines}")
        if confirmed:
            lines.append(f"User-confirmed career intent statement: {confirmed}")
        lines.append(
            f"Historical CV role evidence: {intent.get('current_role') or profile.get('headline') or 'unknown'}"
        )

        notes = context.get('training_notes') or []
        if notes:
            lines.append("User-provided training notes:\n- " + "\n- ".join(notes[:6]))
        return "\n".join(lines)

    async def confirm_career_intent(self, user_id, cv, intent_text: str):
        from app.schemas.ai_training import AITrainingCreate
        from app.services.training_service import AITrainingService

        analysis = dict(cv.analysis_json or {})
        career_intent = dict(analysis.get('career_intent') or {})
        career_intent['current_intent'] = intent_text
        career_intent['source_of_truth'] = 'user'
        analysis['career_intent'] = career_intent
        await self.save_analysis(user_id, cv, analysis)
        await AITrainingService(self.repo.session).create_training(
            user_id,
            AITrainingCreate(
                title='Confirmed career intent',
                content=intent_text,
                category='user_intent',
                is_active=True,
            ),
        )
        return await self.get_cv_for_user(user_id, cv.id)

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
