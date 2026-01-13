import json
from typing import Optional, Any
from datetime import datetime
from brain.llm.provider import LLMProvider, get_llm_provider
from brain.llm.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT_TEMPLATE
from brain.models.task import Task, TaskStatus, ReasoningStep, ExecutionPlan
from brain.orchestrator.slave_manager import SlaveManager
from brain.orchestrator.auto_healing_resilient import ResilientAutoHealing
from brain.memory import ContextManager
from brain.config import settings
import structlog

logger = structlog.get_logger()


class MCPBrain:
    def __init__(self):
        self.llm: LLMProvider = get_llm_provider()
        self.slave_manager = SlaveManager()
        self.tasks: dict[str, Task] = {}
        self.context_manager = ContextManager(max_history=100)
        self.auto_healing = ResilientAutoHealing(self.context_manager, self.llm)
    
    async def process_request(self, user_request: str, dry_run: bool = False) -> Task:
        task = Task(user_request=user_request)
        self.tasks[task.task_id] = task
        
        logger.info("task_created", task_id=task.task_id, request=user_request)
        
        try:
            task.status = TaskStatus.ANALYZING
            await self._analyze_request(task)
            
            task.status = TaskStatus.PLANNING
            await self._create_execution_plan(task, dry_run)
            
            if not dry_run and not settings.enable_kill_switch:
                task.status = TaskStatus.EXECUTING
                await self._execute_plan(task)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error("task_failed", task_id=task.task_id, error=str(e))
            task.status = TaskStatus.FAILED
            task.error = str(e)
        
        task.updated_at = datetime.utcnow()
        
        # Sauvegarder la tâche dans l'historique pour apprentissage
        self.context_manager.add_completed_task(task.model_dump())
        
        return task
    
    async def _analyze_request(self, task: Task):
        # Récupérer le contexte de l'historique
        historical_context = self.context_manager.get_context_for_request(task.user_request)
        
        # Enrichir le prompt avec le contexte si disponible
        if historical_context:
            enriched_request = f"{task.user_request}\n\n{historical_context}"
        else:
            enriched_request = task.user_request
        
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(user_request=enriched_request)
        
        llm_response = await self.llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            json_mode=True
        )
        
        # Stocker les metriques LLM dans le task
        if llm_response.metrics:
            task.metadata["llm_metrics_analysis"] = llm_response.metrics
        
        try:
            analysis = json.loads(llm_response.content)
            
            for idx, reasoning in enumerate(analysis.get("reasoning", [])):
                step = ReasoningStep(
                    thought=reasoning,
                    action=f"analysis_step_{idx}"
                )
                task.reasoning_steps.append(step)
            
            task.metadata["analysis"] = analysis.get("analysis", "")
            
            logger.info(
                "analysis_completed",
                task_id=task.task_id,
                steps=len(task.reasoning_steps),
                tokens_per_second=llm_response.metrics.get("tokens_per_second")
            )
            
        except json.JSONDecodeError as e:
            logger.error("invalid_json_response", error=str(e), response=llm_response.content)
            raise ValueError(f"LLM returned invalid JSON: {e}")
    
    async def _create_execution_plan(self, task: Task, dry_run: bool = False):
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(user_request=task.user_request)
        
        llm_response = await self.llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            json_mode=True
        )
        
        # Stocker les metriques LLM dans le task
        if llm_response.metrics:
            task.metadata["llm_metrics_planning"] = llm_response.metrics
        
        try:
            plan_data = json.loads(llm_response.content)
            plan_info = plan_data.get("plan", {})
            
            task.execution_plan = ExecutionPlan(
                steps=plan_info.get("steps", []),
                estimated_duration=plan_info.get("estimated_duration"),
                requires_approval=plan_info.get("requires_approval", False),
                dry_run=dry_run
            )
            
            logger.info(
                "plan_created",
                task_id=task.task_id,
                plan_id=task.execution_plan.plan_id,
                steps=len(task.execution_plan.steps),
                dry_run=dry_run,
                tokens_per_second=llm_response.metrics.get("tokens_per_second")
            )
            
        except json.JSONDecodeError as e:
            logger.error("invalid_plan_json", error=str(e), response=llm_response.content)
            raise ValueError(f"Failed to parse execution plan: {e}")
    
    async def _execute_plan(self, task: Task):
        if not task.execution_plan:
            raise ValueError("No execution plan available")
        
        results = []
        
        for idx, step in enumerate(task.execution_plan.steps):
            slave_type = step.get("slave_type")
            tool_name = step.get("tool")
            
            logger.info(
                "executing_step",
                task_id=task.task_id,
                step_index=idx,
                slave_type=slave_type,
                tool=tool_name
            )
            
            try:
                # Récupérer les outils disponibles depuis le Slave
                available_tools = await self.slave_manager.get_slave_tools(slave_type)
                
                # Trouver le nom réel de l'outil
                real_tool_name = self.slave_manager.find_tool_name(slave_type, tool_name, available_tools)
                
                if not real_tool_name:
                    logger.warning(
                        "tool_mapping_failed",
                        requested_tool=tool_name,
                        available_tools=[t.get("name") for t in available_tools]
                    )
                    real_tool_name = tool_name  # Utiliser le nom original si pas de mapping trouvé
                else:
                    logger.info(
                        "tool_mapped",
                        requested_tool=tool_name,
                        real_tool=real_tool_name
                    )
                
                result = await self.slave_manager.execute_tool(
                    slave_type=slave_type,
                    tool_name=real_tool_name,
                    parameters=step.get("parameters", {}),
                    dry_run=task.execution_plan.dry_run
                )
                
                results.append({
                    "step": idx,
                    "success": result.get("success", False),
                    "output": result.get("output"),
                    "error": result.get("error")
                })
                
                reasoning_step = ReasoningStep(
                    thought=step.get("justification", ""),
                    action=f"{slave_type}.{real_tool_name}",
                    observation=json.dumps(result)
                )
                task.reasoning_steps.append(reasoning_step)
                
                if not result.get("success", False):
                    logger.warning(
                        "step_failed",
                        task_id=task.task_id,
                        step_index=idx,
                        error=result.get("error")
                    )
                    
                    # AUTO-HEALING RESILIENT: Retry jusqu'au succès ou max retries
                    error_message = result.get("error", "")
                    failed_command = step.get("parameters", {}).get("command", "")
                    
                    if error_message and failed_command:
                        logger.info("attempting_resilient_auto_healing", step=idx)
                        
                        success, healed_result, corrected_command = await self.auto_healing.heal_and_retry(
                            user_request=task.user_request,
                            failed_command=failed_command,
                            error_message=error_message,
                            slave_manager=self.slave_manager,
                            slave_type=slave_type,
                            tool_name=real_tool_name,
                            original_parameters=step.get("parameters", {}),
                            step_index=idx
                        )
                        
                        if success:
                            # Remplacer le résultat échoué par le résultat corrigé
                            results[-1] = {
                                "step": idx,
                                "success": True,
                                "output": healed_result.get("output"),
                                "error": None,
                                "auto_healed": True,
                                "correction_source": "resilient_auto_healing",
                                "original_error": error_message,
                                "corrected_command": corrected_command,
                                "healing_attempts": self.auto_healing.healing_history
                            }
                            
                            logger.info("resilient_auto_healing_success", step=idx)
                            
                            # Continuer l'exécution
                            continue
                        else:
                            logger.error("resilient_auto_healing_exhausted", step=idx)
                            # Ajouter l'historique même en cas d'échec
                            results[-1]["healing_attempts"] = self.auto_healing.healing_history
                    
                    break
                    
            except Exception as e:
                logger.error(
                    "step_execution_error",
                    task_id=task.task_id,
                    step_index=idx,
                    error=str(e)
                )
                results.append({
                    "step": idx,
                    "success": False,
                    "error": str(e)
                })
                break
        
        task.result = {"steps": results}
        logger.info("plan_execution_completed", task_id=task.task_id, total_steps=len(results))
    
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
