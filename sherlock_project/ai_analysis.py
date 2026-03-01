"""Sherlock AI Analysis Module

This module provides AI-powered analysis to enhance username detection accuracy
and reduce false positives/negatives. It uses response content analysis,
pattern recognition, confidence scoring, and optional LLM integration for
intelligent result verification.
"""

import re
import json
import os
import hashlib
import logging
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

import requests as http_requests

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence level for AI analysis results."""
    VERY_HIGH = "very_high"   # 90-100%
    HIGH = "high"             # 70-89%
    MEDIUM = "medium"         # 50-69%
    LOW = "low"               # 30-49%
    VERY_LOW = "very_low"     # 0-29%

    def __str__(self):
        return self.value


@dataclass
class AIAnalysisResult:
    """Result from AI analysis of a query response."""
    confidence_score: float          # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    is_genuine_profile: bool
    analysis_details: dict = field(default_factory=dict)
    username_suggestions: list = field(default_factory=list)
    risk_indicators: list = field(default_factory=list)
    site_category: str = ""
    llm_reasoning: str = ""          # LLM explanation (when enabled)

    def __str__(self):
        return f"[AI: {self.confidence_score:.0%} {self.confidence_level}]"


# ─── Profile Page Indicators ───────────────────────────────────────────────────
# Patterns commonly found on genuine profile pages

PROFILE_POSITIVE_PATTERNS = [
    # Social indicators
    r'(?i)(followers?|following|friends?|connections?)\s*[:\s]*[\d,.]+[kKmM]?',
    r'(?i)(posts?|tweets?|photos?|videos?|media)\s*[:\s]*[\d,.]+[kKmM]?',
    r'(?i)(bio|about\s*me|description|summary)',
    r'(?i)(joined|member\s*since|created)\s*[:\s]*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4})',
    r'(?i)(profile\s*picture|avatar|user-?avatar|profile-?img)',
    # Activity indicators
    r'(?i)(last\s*active|last\s*seen|online|activity)',
    r'(?i)(reputation|karma|points|score|level)\s*[:\s]*[\d,.]+',
    # Content indicators
    r'(?i)(timeline|feed|wall|stream)',
    r'(?i)(send\s*message|follow|add\s*friend|connect)',
]

PROFILE_NEGATIVE_PATTERNS = [
    # Error pages
    r'(?i)(page\s*not\s*found|404\s*error|not\s*found)',
    r'(?i)(this\s*page\s*doesn.?t\s*exist)',
    r'(?i)(user\s*not\s*found|no\s*such\s*user|account\s*not\s*found)',
    r'(?i)(account\s*(has\s*been\s*)?(suspended|banned|deleted|deactivated|removed))',
    r'(?i)(this\s*account\s*is\s*private)',
    r'(?i)(sign\s*up|register|create\s*(an?\s*)?account)',
    r'(?i)(the\s*link\s*you\s*followed\s*may\s*be\s*broken)',
    # Generic error indicators
    r'(?i)(something\s*went\s*wrong|error\s*occurred|unavailable)',
    r'(?i)(access\s*denied|forbidden|unauthorized)',
    # Bot detection
    r'(?i)(captcha|recaptcha|hcaptcha|challenge)',
    r'(?i)(verify\s*you.?re\s*(a\s*)?human|bot\s*detection)',
    r'(?i)(cloudflare|incapsula|akamai|sucuri)',
]

# Common false positive patterns (parked domains, default pages, etc.)
FALSE_POSITIVE_PATTERNS = [
    r'(?i)(domain\s*(is\s*)?(for\s*sale|parked|expired))',
    r'(?i)(buy\s*this\s*domain|register\s*this\s*domain)',
    r'(?i)(under\s*construction|coming\s*soon|maintenance)',
    r'(?i)(default\s*web\s*page|welcome\s*to\s*nginx|apache.*default)',
    r'(?i)(this\s*site\s*can.?t\s*be\s*reached)',
]

# Category patterns for site classification
SITE_CATEGORIES = {
    "social_media": [r'(?i)(facebook|twitter|instagram|tiktok|snapchat|linkedin|mastodon|bluesky)'],
    "developer": [r'(?i)(github|gitlab|bitbucket|stackoverflow|codepen|replit|hackernoon)'],
    "creative": [r'(?i)(deviantart|behance|dribbble|artstation|flickr|500px|soundcloud|bandcamp)'],
    "gaming": [r'(?i)(steam|xbox|playstation|twitch|discord|battle\.net|origin|epic)'],
    "professional": [r'(?i)(linkedin|indeed|glassdoor|angellist|crunchbase)'],
    "forum": [r'(?i)(reddit|quora|discourse|phpbb|vbulletin)'],
    "messaging": [r'(?i)(telegram|signal|whatsapp|keybase|matrix)'],
    "blogging": [r'(?i)(medium|wordpress|blogger|tumblr|substack|ghost)'],
    "ecommerce": [r'(?i)(ebay|amazon|etsy|shopify|mercado)'],
    "video": [r'(?i)(youtube|vimeo|dailymotion|rumble|odysee)'],
}


class AIAnalyzer:
    """AI-powered analyzer for enhancing Sherlock's detection accuracy.
    
    Uses pattern recognition, content fingerprinting, and optional LLM
    integration to provide confidence scores and reduce false results.
    """

    def __init__(self, enable_llm: bool = False, api_key: Optional[str] = None,
                 api_url: Optional[str] = None, model: Optional[str] = None):
        """Initialize AI Analyzer.
        
        Args:
            enable_llm: Whether to use external LLM API for enhanced analysis.
            api_key: API key for LLM service (OpenAI-compatible).
            api_url: Base URL for LLM API endpoint.
            model: Model name to use for LLM queries.
        """
        self.enable_llm = enable_llm
        self.api_key = api_key or os.environ.get("SHERLOCK_AI_API_KEY", "")
        self.api_url = api_url or os.environ.get("SHERLOCK_AI_API_URL", "https://api.openai.com/v1")
        self.model = model or os.environ.get("SHERLOCK_AI_MODEL", "gpt-4o-mini")
        self._response_cache: dict[str, AIAnalysisResult] = {}
        self._site_fingerprints: dict[str, dict] = {}

    def analyze_response(
        self,
        username: str,
        site_name: str,
        url: str,
        response_text: str,
        http_status: int,
        error_type: str,
        query_status_str: str,
    ) -> AIAnalysisResult:
        """Analyze an HTTP response to determine if a username profile is genuine.
        
        Performs multi-layer analysis:
        1. Pattern matching against known profile/error indicators
        2. Content structure analysis (HTML structure, JSON responses)
        3. Username presence verification in response
        4. False positive detection
        5. Optional LLM verification for ambiguous cases
        
        Args:
            username: The username being searched.
            site_name: Name of the social network.
            url: The URL that was probed.
            response_text: The HTTP response body text.
            http_status: The HTTP status code.
            error_type: The detection method used (status_code, message, response_url).
            query_status_str: The current query status as determined by Sherlock.
        
        Returns:
            AIAnalysisResult with confidence score and analysis details.
        """
        # Check cache first
        cache_key = self._cache_key(username, site_name)
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]

        # Run all analysis layers
        pattern_score = self._pattern_analysis(response_text)
        structure_score = self._structure_analysis(response_text, http_status)
        username_score = self._username_presence_analysis(username, response_text)
        false_positive_score = self._false_positive_detection(response_text)
        site_category = self._categorize_site(site_name, url)

        # Weight the scores based on detection method
        weights = self._get_weights(error_type)
        
        raw_score = (
            pattern_score * weights["pattern"]
            + structure_score * weights["structure"]
            + username_score * weights["username"]
            + (1.0 - false_positive_score) * weights["false_positive"]
        )
        
        # Normalize to 0-1 range
        confidence_score = max(0.0, min(1.0, raw_score))

        # Determine if the profile appears genuine
        is_genuine = (
            confidence_score >= 0.5
            and query_status_str == "Claimed"
            and false_positive_score < 0.5
        )

        # Build risk indicators
        risk_indicators = self._build_risk_indicators(
            pattern_score, structure_score, username_score,
            false_positive_score, http_status
        )

        # Generate username suggestions
        suggestions = self._generate_username_suggestions(username)

        # Determine confidence level
        confidence_level = self._score_to_level(confidence_score)

        # ── LLM Verification for ambiguous results ───────────────────────
        llm_reasoning = ""
        is_ambiguous = 0.35 <= confidence_score <= 0.75
        if self.enable_llm and self.api_key and is_ambiguous:
            llm_result = self._llm_verify_profile(
                username=username,
                site_name=site_name,
                url=url,
                response_text=response_text[:4000],  # Limit tokens sent
                http_status=http_status,
                heuristic_score=confidence_score,
                query_status_str=query_status_str,
            )
            if llm_result is not None:
                llm_score, llm_reasoning = llm_result
                # Blend LLM score with heuristic score (LLM gets 60% weight)
                confidence_score = (confidence_score * 0.4) + (llm_score * 0.6)
                confidence_score = max(0.0, min(1.0, confidence_score))
                confidence_level = self._score_to_level(confidence_score)
                is_genuine = (
                    confidence_score >= 0.5
                    and query_status_str == "Claimed"
                    and false_positive_score < 0.5
                )

        result = AIAnalysisResult(
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            is_genuine_profile=is_genuine,
            analysis_details={
                "pattern_score": round(pattern_score, 3),
                "structure_score": round(structure_score, 3),
                "username_in_response": round(username_score, 3),
                "false_positive_risk": round(false_positive_score, 3),
                "http_status": http_status,
                "detection_method": error_type,
                "original_status": query_status_str,
                "llm_used": bool(llm_reasoning),
            },
            username_suggestions=suggestions,
            risk_indicators=risk_indicators,
            site_category=site_category,
            llm_reasoning=llm_reasoning,
        )

        # Cache the result
        self._response_cache[cache_key] = result

        return result

    def get_ai_summary(self, results: dict) -> dict:
        """Generate an AI-powered summary of all search results.
        
        Args:
            results: Dictionary of all site results from sherlock().
        
        Returns:
            Dictionary with summary statistics and insights.
        """
        total_sites = len(results)
        claimed_sites = []
        high_confidence_sites = []
        low_confidence_sites = []
        suspicious_sites = []
        categories: dict[str, int] = {}

        for site_name, site_data in results.items():
            status = site_data.get("status")
            ai_result: Optional[AIAnalysisResult] = site_data.get("ai_analysis")

            if status and str(status.status) == "Claimed":
                claimed_sites.append(site_name)
                
                if ai_result:
                    if ai_result.confidence_score >= 0.7:
                        high_confidence_sites.append(site_name)
                    elif ai_result.confidence_score < 0.4:
                        low_confidence_sites.append(site_name)
                    
                    if ai_result.risk_indicators:
                        suspicious_sites.append(site_name)

                    cat = ai_result.site_category or "uncategorized"
                    categories[cat] = categories.get(cat, 0) + 1

        summary_data = {
            "total_sites_checked": total_sites,
            "accounts_found": len(claimed_sites),
            "high_confidence": len(high_confidence_sites),
            "high_confidence_sites": high_confidence_sites,
            "low_confidence": len(low_confidence_sites),
            "low_confidence_sites": low_confidence_sites,
            "suspicious_results": len(suspicious_sites),
            "suspicious_sites": suspicious_sites,
            "categories": categories,
            "confidence_rate": (
                len(high_confidence_sites) / len(claimed_sites)
                if claimed_sites else 0.0
            ),
        }

        # If LLM is enabled, generate a natural-language summary
        if self.enable_llm and self.api_key and claimed_sites:
            llm_summary = self._llm_generate_summary(summary_data, claimed_sites)
            if llm_summary:
                summary_data["llm_summary"] = llm_summary

        return summary_data

    def suggest_related_usernames(self, username: str) -> list[str]:
        """Suggest related usernames based on common patterns.
        
        Args:
            username: The original username to analyze.
        
        Returns:
            List of suggested variant usernames.
        """
        return self._generate_username_suggestions(username)

    # ─── Private Analysis Methods ───────────────────────────────────────────

    def _pattern_analysis(self, response_text: str) -> float:
        """Analyze response for profile-related patterns.
        
        Returns a score from 0.0 (no profile indicators) to 1.0 (many indicators).
        """
        if not response_text:
            return 0.0

        # Limit analysis to first 50KB for performance
        text = response_text[:51200]

        positive_hits = sum(
            1 for pattern in PROFILE_POSITIVE_PATTERNS
            if re.search(pattern, text)
        )
        negative_hits = sum(
            1 for pattern in PROFILE_NEGATIVE_PATTERNS
            if re.search(pattern, text)
        )

        max_positive = len(PROFILE_POSITIVE_PATTERNS)
        max_negative = len(PROFILE_NEGATIVE_PATTERNS)

        # Positive patterns increase score, negative patterns decrease it
        positive_ratio = positive_hits / max_positive if max_positive else 0
        negative_ratio = negative_hits / max_negative if max_negative else 0

        score = (positive_ratio * 0.7) + ((1 - negative_ratio) * 0.3)
        return max(0.0, min(1.0, score))

    def _structure_analysis(self, response_text: str, http_status: int) -> float:
        """Analyze response structure for profile-like characteristics.
        
        Returns a score from 0.0 to 1.0.
        """
        score = 0.0
        factors = 0

        # HTTP status code analysis
        if 200 <= http_status < 300:
            score += 0.8
        elif 300 <= http_status < 400:
            score += 0.4  # Redirect — might be okay
        else:
            score += 0.1
        factors += 1

        if not response_text:
            return score / factors if factors else 0.0

        text = response_text[:51200]

        # Content length heuristic: genuine profiles usually have substantial content
        content_length = len(text)
        if content_length > 10000:
            score += 0.8
        elif content_length > 5000:
            score += 0.6
        elif content_length > 1000:
            score += 0.4
        else:
            score += 0.2
        factors += 1

        # JSON response analysis (APIs)
        if text.strip().startswith('{') or text.strip().startswith('['):
            try:
                json_data = json.loads(text)
                if isinstance(json_data, dict):
                    # Check for user-like keys
                    user_keys = {'username', 'user', 'name', 'display_name', 'bio',
                                'avatar', 'profile', 'id', 'created_at', 'followers'}
                    matching_keys = user_keys & set(str(k).lower() for k in json_data.keys())
                    if matching_keys:
                        score += min(1.0, len(matching_keys) * 0.15)
                        factors += 1
            except (json.JSONDecodeError, ValueError):
                pass

        # HTML structure analysis
        if '<html' in text.lower():
            # Check for structured data (Schema.org, OpenGraph)
            if 'og:profile' in text or '"Person"' in text or 'schema.org' in text.lower():
                score += 0.9
                factors += 1

            # Meta tags referencing a user/profile
            meta_profile = re.findall(r'<meta[^>]*(?:profile|user|author)[^>]*>', text, re.I)
            if meta_profile:
                score += 0.6
                factors += 1

            # Title tag analysis
            title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.I | re.S)
            if title_match:
                title = title_match.group(1).strip()
                if any(err in title.lower() for err in ['404', 'not found', 'error', 'page not found']):
                    score += 0.1
                else:
                    score += 0.5
                factors += 1

        return score / factors if factors else 0.0

    def _username_presence_analysis(self, username: str, response_text: str) -> float:
        """Check if the username appears in the response in meaningful contexts.
        
        Returns a score from 0.0 to 1.0.
        """
        if not response_text or not username:
            return 0.0

        text = response_text[:51200]
        username_lower = username.lower()
        text_lower = text.lower()

        # Count occurrences
        occurrences = text_lower.count(username_lower)

        if occurrences == 0:
            return 0.1  # Username not found at all — low confidence

        score = 0.0
        factors = 0

        # Basic presence
        if occurrences >= 1:
            score += min(0.5, occurrences * 0.1)
            factors += 1

        # Username in title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.I | re.S)
        if title_match and username_lower in title_match.group(1).lower():
            score += 0.9
            factors += 1

        # Username in heading tags
        heading_matches = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', text, re.I | re.S)
        for heading in heading_matches:
            if username_lower in heading.lower():
                score += 0.8
                factors += 1
                break

        # Username in meta tags
        if re.search(rf'content=["\'][^"\']*{re.escape(username)}[^"\']*["\']', text, re.I):
            score += 0.7
            factors += 1

        # Username in JSON data
        if re.search(rf'"(?:username|user|login|screen_name)"[:\s]*"[^"]*{re.escape(username)}[^"]*"', text, re.I):
            score += 0.9
            factors += 1

        return min(1.0, score / factors) if factors else 0.0

    def _false_positive_detection(self, response_text: str) -> float:
        """Detect likely false positive responses.
        
        Returns a score from 0.0 (not a false positive) to 1.0 (very likely false positive).
        """
        if not response_text:
            return 0.5

        text = response_text[:51200]

        fp_hits = sum(
            1 for pattern in FALSE_POSITIVE_PATTERNS
            if re.search(pattern, text)
        )

        # WAF/bot detection indicators
        waf_patterns = [
            r'(?i)(cloudflare|incapsula|akamai|sucuri|imperva)',
            r'(?i)(challenge-platform|ray\s*id)',
            r'(?i)(enable\s*javascript|browser\s*check)',
            r'(?i)(captcha|recaptcha)',
        ]
        waf_hits = sum(1 for p in waf_patterns if re.search(p, text))

        # Very short responses are suspicious
        length_suspicion = 0.0
        if len(text) < 200:
            length_suspicion = 0.6
        elif len(text) < 500:
            length_suspicion = 0.3

        fp_score = (
            (fp_hits / len(FALSE_POSITIVE_PATTERNS)) * 0.4
            + (waf_hits / len(waf_patterns)) * 0.4
            + length_suspicion * 0.2
        )

        return max(0.0, min(1.0, fp_score))

    def _categorize_site(self, site_name: str, url: str) -> str:
        """Categorize a site based on its name and URL."""
        combined = f"{site_name} {url}".lower()
        for category, patterns in SITE_CATEGORIES.items():
            for pattern in patterns:
                if re.search(pattern, combined):
                    return category
        return "other"

    def _get_weights(self, error_type: str) -> dict[str, float]:
        """Get analysis weights based on the detection method."""
        if error_type == "message":
            return {
                "pattern": 0.30,
                "structure": 0.20,
                "username": 0.30,
                "false_positive": 0.20,
            }
        elif error_type == "status_code":
            return {
                "pattern": 0.25,
                "structure": 0.35,
                "username": 0.20,
                "false_positive": 0.20,
            }
        elif error_type == "response_url":
            return {
                "pattern": 0.20,
                "structure": 0.40,
                "username": 0.20,
                "false_positive": 0.20,
            }
        else:
            return {
                "pattern": 0.25,
                "structure": 0.25,
                "username": 0.25,
                "false_positive": 0.25,
            }

    def _build_risk_indicators(
        self,
        pattern_score: float,
        structure_score: float,
        username_score: float,
        false_positive_score: float,
        http_status: int,
    ) -> list[str]:
        """Build a list of risk indicators based on analysis scores."""
        risks = []

        if pattern_score < 0.3:
            risks.append("Few profile indicators found in response")
        if structure_score < 0.3:
            risks.append("Response structure doesn't match typical profile page")
        if username_score < 0.2:
            risks.append("Username not prominently featured in response")
        if false_positive_score > 0.5:
            risks.append("Response matches known false positive patterns")
        if false_positive_score > 0.3 and false_positive_score <= 0.5:
            risks.append("Some false positive indicators detected")
        if http_status >= 400:
            risks.append(f"HTTP error status {http_status}")
        if http_status >= 300 and http_status < 400:
            risks.append(f"HTTP redirect status {http_status}")

        return risks

    def _generate_username_suggestions(self, username: str) -> list[str]:
        """Generate related username variations."""
        suggestions = set()
        
        if not username:
            return []

        # Common separators
        separators = ['_', '-', '.', '']
        
        # If username has separators, try other separator variants
        for sep in ['_', '-', '.']:
            if sep in username:
                parts = username.split(sep)
                for new_sep in separators:
                    if new_sep != sep:
                        variant = new_sep.join(parts)
                        if variant != username:
                            suggestions.add(variant)

        # Number variations
        if username[-1].isdigit():
            # Strip trailing numbers and suggest base
            base = username.rstrip('0123456789')
            if base and base != username:
                suggestions.add(base)
        else:
            # Add common number suffixes
            for suffix in ['1', '2', '123', '_']:
                suggestions.add(f"{username}{suffix}")

        # Case variations
        if username != username.lower():
            suggestions.add(username.lower())
        if username != username.upper() and len(username) <= 6:
            suggestions.add(username.upper())

        # The/Real prefix (common on social media)
        if not username.lower().startswith(('the', 'real', 'official')):
            suggestions.add(f"the{username}")
            suggestions.add(f"real{username}")

        # Remove existing prefixes
        for prefix in ['the', 'real', 'official', 'its', 'im']:
            if username.lower().startswith(prefix) and len(username) > len(prefix):
                suggestions.add(username[len(prefix):])

        # Limit to most relevant suggestions
        suggestions.discard(username)
        return sorted(list(suggestions))[:10]

    def _score_to_level(self, score: float) -> ConfidenceLevel:
        """Convert a numeric score to a confidence level."""
        if score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.7:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    # ─── LLM API Methods ────────────────────────────────────────────────

    def _llm_call(self, system_prompt: str, user_prompt: str, max_tokens: int = 300) -> Optional[str]:
        """Make a call to an OpenAI-compatible chat completions API.
        
        Args:
            system_prompt: The system message for the LLM.
            user_prompt: The user message for the LLM.
            max_tokens: Maximum tokens in the response.
        
        Returns:
            The LLM's response text, or None if the call failed.
        """
        if not self.api_key:
            return None

        url = f"{self.api_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.1,
        }

        try:
            resp = http_requests.post(url, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.debug(f"LLM API call failed: {e}")
            return None

    def _llm_verify_profile(
        self,
        username: str,
        site_name: str,
        url: str,
        response_text: str,
        http_status: int,
        heuristic_score: float,
        query_status_str: str,
    ) -> Optional[tuple[float, str]]:
        """Ask the LLM to verify whether a response is a genuine user profile.
        
        Returns:
            Tuple of (confidence_score 0.0-1.0, reasoning_text) or None on failure.
        """
        system_prompt = (
            "You are an OSINT analysis assistant. Your task is to determine if an HTTP response "
            "represents a genuine user profile page for a given username on a social network. "
            "Respond ONLY with valid JSON: {\"confidence\": <0.0-1.0>, \"genuine\": <true/false>, "
            "\"reasoning\": \"<brief explanation>\"}"
        )

        # Truncate response for token efficiency
        snippet = response_text[:2000] if response_text else "(empty response)"

        user_prompt = (
            f"Username: {username}\n"
            f"Site: {site_name}\n"
            f"URL: {url}\n"
            f"HTTP Status: {http_status}\n"
            f"Sherlock Detection Result: {query_status_str}\n"
            f"Heuristic Confidence: {heuristic_score:.2f}\n"
            f"\n--- Response Body (truncated) ---\n{snippet}\n---\n\n"
            f"Is this a genuine profile page for the user '{username}' on {site_name}? "
            f"Consider: Does the page contain profile-specific content? Could this be a false positive "
            f"(error page, bot detection, parked domain, generic page)? "
            f"Reply with JSON only."
        )

        raw = self._llm_call(system_prompt, user_prompt, max_tokens=200)
        if not raw:
            return None

        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{[^}]+\}', raw, re.S)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                parsed = json.loads(raw)

            confidence = float(parsed.get("confidence", heuristic_score))
            confidence = max(0.0, min(1.0, confidence))
            reasoning = parsed.get("reasoning", "")
            return (confidence, reasoning)
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.debug(f"Failed to parse LLM verification response: {e}")
            return None

    def _llm_generate_summary(
        self,
        summary_data: dict,
        claimed_sites: list[str],
    ) -> Optional[str]:
        """Use the LLM to generate a natural-language summary of search results.
        
        Returns:
            Summary text string, or None on failure.
        """
        system_prompt = (
            "You are an OSINT analysis assistant. Summarize username search results "
            "in 2-4 concise sentences. Focus on notable findings, patterns, and "
            "confidence levels. Be factual and professional."
        )

        user_prompt = (
            f"Search results summary:\n"
            f"- Total sites checked: {summary_data['total_sites_checked']}\n"
            f"- Accounts found: {summary_data['accounts_found']}\n"
            f"- High confidence matches: {summary_data['high_confidence']} "
            f"({', '.join(summary_data['high_confidence_sites'][:10])})\n"
            f"- Low confidence matches: {summary_data['low_confidence']} "
            f"({', '.join(summary_data['low_confidence_sites'][:10])})\n"
            f"- Suspicious results: {summary_data['suspicious_results']}\n"
            f"- Categories: {summary_data['categories']}\n\n"
            f"Provide a brief professional analysis of these findings."
        )

        return self._llm_call(system_prompt, user_prompt, max_tokens=250)

    def _cache_key(self, username: str, site_name: str) -> str:
        """Generate a cache key for a query."""
        return hashlib.md5(f"{username}:{site_name}".encode()).hexdigest()

    def clear_cache(self):
        """Clear the analysis cache."""
        self._response_cache.clear()


def create_ai_analyzer(
    enable_llm: bool = False,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    model: Optional[str] = None,
) -> AIAnalyzer:
    """Factory function to create an AIAnalyzer instance.
    
    Args:
        enable_llm: Enable LLM-powered analysis.
        api_key: API key for LLM service.
        api_url: Base URL for LLM API.
        model: LLM model name.
    
    Returns:
        Configured AIAnalyzer instance.
    """
    return AIAnalyzer(
        enable_llm=enable_llm,
        api_key=api_key,
        api_url=api_url,
        model=model,
    )
