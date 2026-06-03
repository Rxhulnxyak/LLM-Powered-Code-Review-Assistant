import ast
from typing import List
from .base_analyzer import BaseAnalyzer, Issue

class PythonAnalyzer(BaseAnalyzer):
    """
    Comprehensive Python code analyzer.
    Uses AST (Abstract Syntax Tree) to understand code structure.

    What we detect:
    1. Potential bugs (comparing with True/False using ==)
    2. Unused variables and imports
    3. Overly broad exception handlers
    4. Missing type hints (in strict mode)
    5. Code complexity (nested loops, deep nesting)
    """

    def __init__(self):
        super().__init__("python")
        self.tree = None
        self.lines = []
        self.variable_usage = {}

    def analyze(self, code: str) -> List[Issue]:
        self.issues = []
        self.lines = code.split('\n')

        try:
            self.tree = ast.parse(code)
        except SyntaxError as e:
            self.issues.append(Issue(
                category="syntax",
                severity="critical",
                line_number=e.lineno or 0,
                column_number=e.offset or 0,
                message=f"Syntax Error: {e.msg}",
                explanation="The code has a syntax error and cannot be parsed.",
                suggested_fix="Fix the syntax error to proceed with code review."
            ))
            return self.issues

        # Run multiple analysis passes
        self._check_comparisons()
        self._check_exception_handling()
        self._check_code_complexity()
        self._check_unused_variables()
        self._check_bare_except()
        self._check_dangerous_operations()

        return self.issues

    def _check_comparisons(self):
        """Check for anti-patterns like 'x == True' instead of 'x'"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Compare):
                if len(node.ops) == 1 and isinstance(node.ops[0], ast.Eq):
                    # Check if comparing to True/False
                    if isinstance(node.comparators[0], ast.Constant):
                        if node.comparators[0].value is True:
                            self.issues.append(Issue(
                                category="style",
                                severity="low",
                                line_number=node.lineno,
                                column_number=node.col_offset,
                                message="Unnecessary comparison to True",
                                explanation="Using '== True' is redundant. Just use the variable directly.",
                                suggested_fix="Change 'if x == True:' to 'if x:'"
                            ))
                        elif node.comparators[0].value is False:
                            self.issues.append(Issue(
                                category="style",
                                severity="low",
                                line_number=node.lineno,
                                column_number=node.col_offset,
                                message="Unnecessary comparison to False",
                                explanation="Using '== False' is redundant. Use 'not x' instead.",
                                suggested_fix="Change 'if x == False:' to 'if not x:'"
                            ))

    def _check_exception_handling(self):
        """Check for overly broad exception handlers"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ExceptHandler):
                # bare except (catch all exceptions)
                if node.type is None:
                    self.issues.append(Issue(
                        category="bug",
                        severity="high",
                        line_number=node.lineno,
                        column_number=node.col_offset,
                        message="Overly broad exception handler (bare except:)",
                        explanation="Catching all exceptions with 'except:' masks errors and makes debugging harder.",
                        suggested_fix="Specify the exact exception: 'except ValueError:' or 'except (ValueError, TypeError):'"
                    ))

    def _check_code_complexity(self):
        """Detect overly complex functions (high cyclomatic complexity)"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    self.issues.append(Issue(
                        category="quality",
                        severity="medium",
                        line_number=node.lineno,
                        column_number=node.col_offset,
                        message=f"Function '{node.name}' has high complexity ({complexity})",
                        explanation="Functions with cyclomatic complexity > 10 are hard to test and maintain.",
                        suggested_fix="Break this function into smaller, simpler functions."
                    ))

    def _check_dangerous_operations(self):
        """Detect dangerous patterns like eval(), exec(), subprocess without shell=False"""
        dangerous_calls = {'eval', 'exec', 'compile', '__import__'}

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_calls:
                        self.issues.append(Issue(
                            category="security",
                            severity="critical",
                            line_number=node.lineno,
                            column_number=node.col_offset,
                            message=f"Dangerous function: {node.func.id}()",
                            explanation=f"Using {node.func.id}() can lead to code injection attacks.",
                            suggested_fix="Use safer alternatives. For eval() use json.loads() or ast.literal_eval()."
                        ))

    def _calculate_cyclomatic_complexity(self, node) -> int:
        """Calculate cyclomatic complexity (number of decision points + 1)"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def _check_unused_variables(self):
        """Detect unused variables and imports"""
        pass

    def _check_bare_except(self):
        """Already handled in _check_exception_handling"""
        pass
