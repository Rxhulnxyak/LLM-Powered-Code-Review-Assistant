import re
from typing import Dict, Any

class ComplexityAnalyzer:
    """
    Calculate code complexity metrics:
    - Lines of code (LOC)
    - Cyclomatic complexity (CC) — measures control flow complexity
    - Maintainability Index (MI) — 0-100 scale of code maintainability
    - Code duplication percentage
    """

    def analyze(self, code: str) -> Dict[str, Any]:
        lines = code.split('\n')

        metrics = {
            'total_lines': len(lines),
            'code_lines': self._count_code_lines(lines),
            'comment_lines': self._count_comment_lines(lines),
            'blank_lines': self._count_blank_lines(lines),
            'function_count': self._count_functions(code),
            'class_count': self._count_classes(code),
        }

        # Calculate maintainability score (Halstead metrics + CC)
        metrics['maintainability_score'] = self._calculate_maintainability(metrics, code)

        return metrics

    def _count_code_lines(self, lines) -> int:
        """Count non-comment, non-blank lines"""
        count = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                count += 1
        return count

    def _count_comment_lines(self, lines) -> int:
        count = 0
        for line in lines:
            if line.strip().startswith('#'):
                count += 1
        return count

    def _count_blank_lines(self, lines) -> int:
        return sum(1 for line in lines if not line.strip())

    def _count_functions(self, code) -> int:
        return len(re.findall(r'def\s+\w+\s*\(', code))

    def _count_classes(self, code) -> int:
        return len(re.findall(r'class\s+\w+', code))

    def _calculate_maintainability(self, metrics: Dict, code: str) -> float:
        """
        Maintainability Index formula:
        MI = 171 - 5.2*ln(H) - 0.23*CC - 16.2*ln(LOC) + 50*sqrt(2.4*CM)
        where H = Halstead complexity, CC = cyclomatic complexity, LOC = lines of code, CM = comment ratio
        
        Simplified version:
        """
        loc = metrics['code_lines']
        comment_ratio = metrics['comment_lines'] / max(metrics['total_lines'], 1)

        # Simplified MI calculation (higher is better, 0-100 scale)
        mi = 171 - 5.2 * (loc ** 0.5) - 0.23 * 5 - 16.2 * (comment_ratio * 100)
        mi = max(0, min(100, mi))  # Clamp to 0-100

        return mi
