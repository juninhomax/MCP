from typing import List, Dict, Optional
from datetime import datetime
from collections import deque
import json


class TaskHistoryManager:
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.history = deque(maxlen=max_history)
    
    def add_task(self, task_data: Dict) -> None:
        entry = {
            "task_id": task_data.get("task_id"),
            "user_request": task_data.get("user_request"),
            "status": task_data.get("status"),
            "execution_plan": task_data.get("execution_plan"),
            "result": task_data.get("result"),
            "error": task_data.get("error"),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": task_data.get("metadata", {})
        }
        self.history.append(entry)
    
    def get_recent_tasks(self, limit: int = 10) -> List[Dict]:
        return list(self.history)[-limit:]
    
    def get_successful_tasks(self, limit: int = 10) -> List[Dict]:
        successful = [t for t in self.history if t.get("status") == "completed" and not t.get("error")]
        return successful[-limit:]
    
    def get_failed_tasks(self, limit: int = 10) -> List[Dict]:
        failed = [t for t in self.history if t.get("error")]
        return failed[-limit:]
    
    def search_similar_requests(self, user_request: str, limit: int = 5) -> List[Dict]:
        keywords = set(user_request.lower().split())
        scored_tasks = []
        
        for task in self.history:
            task_request = task.get("user_request", "").lower()
            task_keywords = set(task_request.split())
            similarity = len(keywords & task_keywords) / max(len(keywords), len(task_keywords))
            
            if similarity > 0.3:
                scored_tasks.append((similarity, task))
        
        scored_tasks.sort(reverse=True, key=lambda x: x[0])
        return [task for _, task in scored_tasks[:limit]]
    
    def get_context_for_llm(self, current_request: str, limit: int = 5) -> str:
        recent_tasks = self.get_recent_tasks(limit)
        similar_tasks = self.search_similar_requests(current_request, limit=3)
        
        context_parts = []
        
        if recent_tasks:
            context_parts.append("Recent tasks:")
            for task in recent_tasks[-3:]:
                context_parts.append(f"- Request: {task['user_request']}")
                context_parts.append(f"  Status: {task['status']}")
                if task.get('error'):
                    context_parts.append(f"  Error: {task['error'][:100]}")
        
        if similar_tasks:
            context_parts.append("\nSimilar past tasks:")
            for task in similar_tasks:
                context_parts.append(f"- Request: {task['user_request']}")
                context_parts.append(f"  Status: {task['status']}")
                if task.get('result'):
                    context_parts.append(f"  Result: Success")
        
        return "\n".join(context_parts)
    
    def clear_history(self) -> None:
        self.history.clear()
    
    def export_history(self) -> str:
        return json.dumps(list(self.history), indent=2)
    
    def import_history(self, json_data: str) -> None:
        data = json.loads(json_data)
        self.history.clear()
        self.history.extend(data)
