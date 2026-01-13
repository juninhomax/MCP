from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
import re


class ErrorPattern:
    def __init__(self, error_type: str, error_message: str, solution: str, 
                 command_failed: str = "", command_corrected: str = ""):
        self.error_type = error_type
        self.error_message = error_message
        self.solution = solution
        self.command_failed = command_failed
        self.command_corrected = command_corrected
        self.occurrences = 1
        self.last_seen = datetime.utcnow()
        self.success_rate = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "solution": self.solution,
            "command_failed": self.command_failed,
            "command_corrected": self.command_corrected,
            "occurrences": self.occurrences,
            "last_seen": self.last_seen.isoformat(),
            "success_rate": self.success_rate
        }


class ErrorPatternDatabase:
    def __init__(self):
        self.patterns: List[ErrorPattern] = []
        self.error_type_index: Dict[str, List[ErrorPattern]] = defaultdict(list)
    
    def extract_error_type(self, error_message: str) -> str:
        if "PathNotFound" in error_message or "n'existe pas" in error_message:
            return "PathNotFound"
        elif "Access" in error_message and "denied" in error_message.lower():
            return "AccessDenied"
        elif "CommandNotFound" in error_message:
            return "CommandNotFound"
        elif "ParameterBinding" in error_message:
            return "InvalidParameter"
        else:
            return "Unknown"
    
    def add_error_pattern(self, error_message: str, solution: str, 
                         command_failed: str = "", command_corrected: str = "") -> None:
        error_type = self.extract_error_type(error_message)
        
        existing_pattern = self.find_similar_pattern(error_message)
        
        if existing_pattern:
            existing_pattern.occurrences += 1
            existing_pattern.last_seen = datetime.utcnow()
            if command_corrected and not existing_pattern.command_corrected:
                existing_pattern.command_corrected = command_corrected
        else:
            pattern = ErrorPattern(
                error_type=error_type,
                error_message=error_message[:200],
                solution=solution,
                command_failed=command_failed,
                command_corrected=command_corrected
            )
            self.patterns.append(pattern)
            self.error_type_index[error_type].append(pattern)
    
    def find_similar_pattern(self, error_message: str) -> Optional[ErrorPattern]:
        error_type = self.extract_error_type(error_message)
        
        for pattern in self.error_type_index.get(error_type, []):
            if self._similarity_score(pattern.error_message, error_message) > 0.7:
                return pattern
        
        return None
    
    def _similarity_score(self, text1: str, text2: str) -> float:
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def get_solution_for_error(self, error_message: str) -> Optional[Dict]:
        pattern = self.find_similar_pattern(error_message)
        
        if pattern:
            return {
                "solution": pattern.solution,
                "command_corrected": pattern.command_corrected,
                "confidence": min(pattern.occurrences / 10.0, 1.0),
                "occurrences": pattern.occurrences
            }
        
        return None
    
    def get_top_errors(self, limit: int = 10) -> List[Dict]:
        sorted_patterns = sorted(self.patterns, key=lambda p: p.occurrences, reverse=True)
        return [p.to_dict() for p in sorted_patterns[:limit]]
    
    def mark_solution_success(self, error_message: str, success: bool) -> None:
        pattern = self.find_similar_pattern(error_message)
        
        if pattern:
            total_attempts = pattern.occurrences
            if success:
                pattern.success_rate = (pattern.success_rate * (total_attempts - 1) + 1.0) / total_attempts
            else:
                pattern.success_rate = (pattern.success_rate * (total_attempts - 1)) / total_attempts
    
    def get_context_for_llm(self, error_message: str) -> str:
        solution = self.get_solution_for_error(error_message)
        
        if solution:
            return f"""
Known solution found in error database:
- Solution: {solution['solution']}
- Corrected command: {solution['command_corrected']}
- Confidence: {solution['confidence']:.0%}
- Times seen: {solution['occurrences']}

You can use this as a reference for your analysis.
"""
        
        return "No known solution found in database. Analyze the error and propose a new solution."
