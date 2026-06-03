from typing import Optional

class ReviewPrompts:
    """
    Carefully engineered prompts for code review.
    
    Why prompt engineering matters:
    - Same LLM, different prompts -> very different quality
    - Good prompts: specific task, examples, output format, role definition
    - Bad prompts: vague, generic "review this code"
    """

    @staticmethod
    def get_code_review_prompt(
        code: str,
        language: str,
        previous_issues: Optional[list] = None,
    ) -> str:
        """
        Main code review prompt.
        Role: You are a senior software engineer
        Task: Comprehensive code review
        Output format: JSON with structured issues
        """

        context = ""
        if previous_issues:
            context = f"\\nAlready identified issues:\\n"
            for issue in previous_issues:
                context += f"- {issue['severity'].upper()}: {issue['message']}\\n"

        return f"""You are an experienced senior software engineer with 15+ years of experience.
Your task is to review code and provide comprehensive feedback.

IMPORTANT: Focus on issues NOT already identified:
{context}

Code Language: {language}
Code to Review:
```{language}
{code}
```

Analyze the code for:
1. **Bugs**: Logic errors, edge cases, incorrect implementations
2. **Security Issues**: Vulnerabilities, unsafe operations, input validation gaps
3. **Performance Issues**: Inefficient algorithms, unnecessary computations, memory leaks
4. **Code Quality**: Maintainability, readability, naming conventions, complexity
5. **Best Practices**: Error handling, type hints, documentation, design patterns

For EACH issue found:
- Line number
- Category (bug/security/performance/quality/best-practice)
- Severity (critical/high/medium/low)
- Clear explanation of why it's a problem
- Exact suggested fix with code example

Return ONLY valid JSON in this format:
{{
  "issues": [
    {{
      "line_number": int,
      "category": str,
      "severity": str,
      "message": str,
      "explanation": str,
      "suggested_fix": str,
      "code_example": str
    }}
  ],
  "summary": {{
    "total_issues": int,
    "critical_count": int,
    "high_count": int,
    "medium_count": int,
    "low_count": int,
    "overall_assessment": str
  }}
}}

Be thorough but efficient. Focus on the most important issues first."""

    @staticmethod
    def get_security_focus_prompt(code: str, language: str) -> str:
        """Specialized prompt focused on security vulnerabilities"""
        return f"""You are a Security Engineer specializing in code security reviews.

Code Language: {language}
Code to Review:
```{language}
{code}
```

FOCUS EXCLUSIVELY ON SECURITY VULNERABILITIES

Check for:
1. **OWASP Top 10** vulnerabilities
   - A01: Broken Access Control
   - A02: Cryptographic Failures
   - A03: Injection (SQL, command, code)
   - A04: Insecure Design
   - A05: Security Misconfiguration
   - A06: Vulnerable and Outdated Components
   - A07: Authentication Failures
   - A08: Software and Data Integrity Failures
   - A09: Logging and Monitoring Failures
   - A10: Server-Side Request Forgery (SSRF)

2. **Common Weakness Enumeration (CWE)** issues
   - CWE-79: Cross-site Scripting (XSS)
   - CWE-89: SQL Injection
   - CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code (Code Injection)
   - CWE-434: Unrestricted Upload of File with Dangerous Type
   - CWE-502: Deserialization of Untrusted Data
   - etc.

3. **Secrets & Credentials**: Hardcoded passwords, API keys, tokens, private keys
4. **Unsafe Dependencies**: Known vulnerable libraries
5. **Authentication & Authorization**: Weak mechanisms, missing checks
6. **Cryptography**: Weak algorithms, improper implementations
7. **Data Protection**: Unencrypted sensitive data, exposed logs

Return JSON with security findings only:
{{
  "security_issues": [
    {{
      "line_number": int,
      "severity": "critical|high|medium|low",
      "vulnerability_type": str,
      "owasp_category": str,
      "cwe_id": int,
      "message": str,
      "risk_explanation": str,
      "remediation": str
    }}
  ],
  "security_score": float (0-100),
  "critical_findings": int,
  "overall_risk_level": "critical|high|medium|low"
}}"""

    @staticmethod
    def get_auto_fix_prompt(
        code: str,
        language: str,
        issue_description: str,
        line_number: int,
    ) -> str:
        """Prompt to generate a fix for a specific issue"""
        return f"""You are a skilled developer. Fix the following code issue.

Language: {language}
Issue (Line {line_number}): {issue_description}

Original Code:
```{language}
{code}
```

Generate a corrected version of ONLY the affected section that:
1. Fixes the issue
2. Maintains the original intent
3. Doesn't introduce new issues
4. Follows {language} best practices

Return ONLY the corrected code snippet, no explanation:
```{language}
[FIXED CODE HERE]
```"""
