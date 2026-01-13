from typing import Dict, Optional
from .task_history import TaskHistoryManager
from .error_patterns import ErrorPatternDatabase


class ContextManager:
    def __init__(self, max_history: int = 100):
        self.task_history = TaskHistoryManager(max_history)
        self.error_patterns = ErrorPatternDatabase()
    
    def add_completed_task(self, task_data: Dict) -> None:
        self.task_history.add_task(task_data)
        
        if task_data.get("error"):
            error_message = task_data["error"]
            
            if task_data.get("metadata", {}).get("error_analysis"):
                analysis = task_data["metadata"]["error_analysis"]
                solution = analysis.get("solution", "")
                corrected_command = analysis.get("corrected_command", "")
                
                self.error_patterns.add_error_pattern(
                    error_message=error_message,
                    solution=solution,
                    command_failed=task_data.get("execution_plan", {}).get("steps", [{}])[0].get("parameters", {}).get("command", ""),
                    command_corrected=corrected_command
                )
    
    def get_context_for_request(self, user_request: str, include_errors: bool = True) -> str:
        context_parts = []
        
        task_context = self.task_history.get_context_for_llm(user_request)
        if task_context:
            context_parts.append("=== TASK HISTORY CONTEXT ===")
            context_parts.append(task_context)
        
        return "\n\n".join(context_parts) if context_parts else ""
    
    def get_context_for_error(self, error_message: str) -> str:
        error_context = self.error_patterns.get_context_for_llm(error_message)
        return error_context
    
    def get_statistics(self) -> Dict:
        recent_tasks = self.task_history.get_recent_tasks(100)
        
        total_tasks = len(recent_tasks)
        successful_tasks = len([t for t in recent_tasks if t.get("status") == "completed" and not t.get("error")])
        failed_tasks = len([t for t in recent_tasks if t.get("error")])
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0.0,
            "top_errors": self.error_patterns.get_top_errors(5),
            "recent_tasks_count": len(recent_tasks)
        }
    
    def clear_all(self) -> None:
        self.task_history.clear_history()
        self.error_patterns = ErrorPatternDatabase()
