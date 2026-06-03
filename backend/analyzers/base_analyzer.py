from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

@dataclass
class Issue:
    """Represents a single code issue found"""
    category: str          # "bug", "security", "performance", "style"
    severity: str          # "low", "medium", "high", "critical"
    line_number: int
    column_number: int
    message: str
    explanation: str
    suggested_fix: str = ""
    affected_code: str = ""
    rule_id: str = ""

class BaseAnalyzer(ABC):
    """Abstract base for all code analyzers"""

    def __init__(self, language: str):
        self.language = language
        self.issues: List[Issue] = []

    @abstractmethod
    def analyze(self, code: str) -> List[Issue]:
        pass
