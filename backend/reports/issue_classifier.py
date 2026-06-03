from enum import Enum
from typing import Dict, List
import re

class IssueSeverity(str, Enum):
    CRITICAL = "critical"  # Production blocker, immediate fix required
    HIGH = "high"           # Significant issue, fix before merge
    MEDIUM = "medium"       # Should be fixed, good for next release
    LOW = "low"             # Nice to have, can be ignored for now

class IssueCategory(str, Enum):
    SECURITY = "security"       # Security vulnerabilities
    BUG = "bug"                # Potential bugs / logic errors
    PERFORMANCE = "performance" # Performance issues
    QUALITY = "quality"        # Code quality / maintainability
    BEST_PRACTICE = "best_practice"  # Coding best practices
    STYLE = "style"            # Formatting / naming conventions

class IssueClassifier:
    """
    Classifies issues into categories and assigns appropriate severity levels.
    
    Severity assignment rules:
    - CRITICAL: Security vulnerabilities (RCE, SQL injection, hardcoded secrets)
    - HIGH: Memory leaks, potential crashes, dangerous patterns
    - MEDIUM: Code quality issues, performance problems
    - LOW: Style issues, minor improvements
    """

    SEVERITY_MAP = {
        # Security issues
        'hardcoded.*password': IssueSeverity.CRITICAL,
        'hardcoded.*api.*key': IssueSeverity.CRITICAL,
        'sql.*injection': IssueSeverity.CRITICAL,
        'eval\(\)': IssueSeverity.CRITICAL,
        'shell=True': IssueSeverity.CRITICAL,
        'command.*injection': IssueSeverity.CRITICAL,
        'xss': IssueSeverity.CRITICAL,

        # High severity bugs
        'nullpointerexception': IssueSeverity.HIGH,
        'zerodivision': IssueSeverity.HIGH,
        'memory.*leak': IssueSeverity.HIGH,
        'infinite.*loop': IssueSeverity.HIGH,

        # Medium severity
        'complexity.*high': IssueSeverity.MEDIUM,
        'performance': IssueSeverity.MEDIUM,
        'duplicate.*code': IssueSeverity.MEDIUM,

        # Low severity
        'naming.*convention': IssueSeverity.LOW,
        'style': IssueSeverity.LOW,
        'formatting': IssueSeverity.LOW,
    }

    @staticmethod
    def classify(issue: Dict) -> Dict:
        """
        Classify an issue by:
        1. Message content
        2. Category tag
        3. Severity pattern matching
        """
        message = issue.get('message', '').lower()
        category = issue.get('category', '').lower()

        # Determine severity
        severity = IssueSeverity.MEDIUM  # Default

        for pattern, sev in IssueClassifier.SEVERITY_MAP.items():
            if re.search(pattern, message + ' ' + category):
                severity = sev
                break

        # Determine category
        if 'security' in message or 'vulnerable' in message:
            classified_category = IssueCategory.SECURITY
        elif 'bug' in message or 'error' in message or 'exception' in message:
            classified_category = IssueCategory.BUG
        elif 'performance' in message or 'slow' in message or 'optimize' in message:
            classified_category = IssueCategory.PERFORMANCE
        elif 'complexity' in message or 'maintainab' in message or 'readable' in message:
            classified_category = IssueCategory.QUALITY
        elif 'style' in message or 'convention' in message or 'naming' in message:
            classified_category = IssueCategory.STYLE
        else:
            classified_category = IssueCategory.BEST_PRACTICE

        return {
            **issue,
            'severity': severity.value,
            'category': classified_category.value,
        }

    @staticmethod
    def prioritize_issues(issues: List[Dict]) -> List[Dict]:
        """Sort issues by severity (most critical first) and category"""
        severity_order = {
            'critical': 0,
            'high': 1,
            'medium': 2,
            'low': 3,
        }

        return sorted(
            issues,
            key=lambda x: (severity_order.get(x.get('severity'), 99), x.get('line_number', 0))
        )
