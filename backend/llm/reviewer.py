import json
from typing import List, Dict
import asyncio
from config import get_settings

settings = get_settings()

class LLMReviewer:
    """
    Orchestrates the LLM-based code review process.
    
    Pipeline:
    1. Receive code + language
    2. Generate security-focused review
    3. Generate general quality review
    4. Merge results, remove duplicates
    5. For each issue, generate suggested fix
    6. Classify severity and priority
    7. Return structured report
    """

    def __init__(self):
        self._setup_llm_client()

    def _setup_llm_client(self):
        if settings.LLM_PROVIDER == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        elif settings.LLM_PROVIDER == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=settings.GOOGLE_API_KEY)

    async def review_code(self, code: str, language: str) -> Dict:
        """
        Complete code review using LLM.
        Parallel execution of multiple review types for speed.
        """

        # Run security and quality reviews in parallel
        security_review, quality_review = await asyncio.gather(
            self._security_review(code, language),
            self._quality_review(code, language),
        )

        # Merge results
        all_issues = self._merge_issues(security_review, quality_review)

        # For high-severity issues, generate fixes in parallel
        fixes = await asyncio.gather(*[
            self._generate_fix(code, language, issue)
            for issue in all_issues if issue.get('severity') in ['critical', 'high']
        ])

        # Attach fixes to issues
        for i, fix in enumerate(fixes):
            all_issues[i]['suggested_fix'] = fix

        return {
            'issues': all_issues,
            'summary': self._generate_summary(all_issues),
            'code_metrics': self._analyze_metrics(code),
        }

    async def _security_review(self, code: str, language: str) -> Dict:
        """Security-focused review"""
        from .prompts import ReviewPrompts

        prompt = ReviewPrompts.get_security_focus_prompt(code, language)
        response = await self._call_llm(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {'security_issues': [], 'security_score': 0}

    async def _quality_review(self, code: str, language: str) -> Dict:
        """General code quality review"""
        from .prompts import ReviewPrompts

        prompt = ReviewPrompts.get_code_review_prompt(code, language)
        response = await self._call_llm(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {'issues': [], 'summary': {}}

    async def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM"""
        if settings.LLM_PROVIDER == "openai":
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent, factual output
                max_tokens=4096,
            )
            return response.choices[0].message.content

        elif settings.LLM_PROVIDER == "gemini":
            import google.generativeai as genai
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=4096,
                ),
            )
            return response.text
        return "{}"

    async def _generate_fix(self, code: str, language: str, issue: Dict) -> str:
        """Generate a code fix for a specific issue"""
        from .prompts import ReviewPrompts

        prompt = ReviewPrompts.get_auto_fix_prompt(
            code, language, issue.get('message', ''), issue.get('line_number', 0)
        )
        return await self._call_llm(prompt)

    def _merge_issues(self, security: Dict, quality: Dict) -> List[Dict]:
        """Merge security and quality reviews, remove duplicates"""
        all_issues = []
        all_issues.extend(security.get('security_issues', []))
        all_issues.extend(quality.get('issues', []))

        # Simple deduplication: remove issues at same line with similar messages
        seen = set()
        unique_issues = []
        for issue in all_issues:
            key = (issue.get('line_number'), issue.get('message', '')[:50])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        return unique_issues

    def _calculate_quality_score(self, issues: List[Dict]) -> float:
        score = 100
        for i in issues:
            sev = i.get('severity')
            if sev == 'critical': score -= 15
            elif sev == 'high': score -= 10
            elif sev == 'medium': score -= 5
            elif sev == 'low': score -= 2
        return max(0, score)

    def _generate_summary(self, issues: List[Dict]) -> Dict:
        """Generate summary statistics"""
        return {
            'total_issues': len(issues),
            'critical': len([i for i in issues if i.get('severity') == 'critical']),
            'high': len([i for i in issues if i.get('severity') == 'high']),
            'medium': len([i for i in issues if i.get('severity') == 'medium']),
            'low': len([i for i in issues if i.get('severity') == 'low']),
            'overall_code_quality': self._calculate_quality_score(issues),
        }

    def _analyze_metrics(self, code: str) -> Dict:
        """Calculate code metrics"""
        return {
            'lines_of_code': len(code.split('\\n')),
            'code_lines': len([l for l in code.split('\\n') if l.strip()]),
            'average_line_length': sum(len(l) for l in code.split('\\n')) / max(len(code.split('\\n')), 1),
        }
