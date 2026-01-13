from typing import Dict, Optional, Tuple
from brain.memory import ContextManager
from brain.llm.provider import LLMProvider
import structlog

logger = structlog.get_logger()


class AutoHealing:
    def __init__(self, context_manager: ContextManager, llm_provider: LLMProvider):
        self.context_manager = context_manager
        self.llm = llm_provider
        self.max_retries = 3
        self.retry_history = []
    
    async def handle_error(
        self, 
        user_request: str,
        failed_command: str,
        error_message: str,
        step_index: int
    ) -> Optional[Dict]:
        logger.info(
            "auto_healing_triggered",
            command=failed_command,
            error_type=self._extract_error_type(error_message)
        )
        
        known_solution = self.context_manager.error_patterns.get_solution_for_error(error_message)
        
        if known_solution and known_solution.get("confidence", 0) > 0.5:
            logger.info(
                "using_known_solution",
                confidence=known_solution["confidence"],
                occurrences=known_solution["occurrences"]
            )
            
            corrected_command = known_solution.get("command_corrected")
            if corrected_command and corrected_command != failed_command:
                return {
                    "corrected_command": corrected_command,
                    "explanation": known_solution.get("solution", "Known solution from error database"),
                    "source": "error_database",
                    "confidence": known_solution["confidence"]
                }
        
        logger.info("analyzing_error_with_llm")
        llm_solution = await self._analyze_with_llm(user_request, failed_command, error_message)
        
        if llm_solution:
            self.context_manager.error_patterns.add_error_pattern(
                error_message=error_message,
                solution=llm_solution.get("explanation", ""),
                command_failed=failed_command,
                command_corrected=llm_solution.get("corrected_command", "")
            )
            
            return {
                "corrected_command": llm_solution.get("corrected_command"),
                "explanation": llm_solution.get("explanation"),
                "source": "llm_analysis",
                "confidence": 0.7
            }
        
        return None
    
    async def _analyze_with_llm(
        self, 
        user_request: str, 
        failed_command: str, 
        error_message: str
    ) -> Optional[Dict]:
        error_context = self.context_manager.get_context_for_error(error_message)
        
        analysis_prompt = f"""
AUTO-CORRECTION AUTONOME

Demande originale: {user_request}

Echec:
- Commande executee: {failed_command}
- Erreur: {error_message}

{error_context}

Mission:
Analyse l'echec et propose une commande corrigee qui reussira a accomplir la demande originale.

Contraintes:
1. La commande corrigee doit etre differente de celle qui a echoue
2. Elle doit directement repondre a la demande de l'utilisateur
3. Utilise ton expertise pour deduire la correction necessaire

Reponds en JSON:
{{
  "explanation": "analyse de l'erreur et correction",
  "corrected_command": "commande corrigee",
  "reasoning": "logique de resolution"
}}
"""
        
        try:
            llm_response = await self.llm.generate(
                prompt=analysis_prompt,
                system_prompt="Tu es un expert en debugging et correction automatique d'erreurs. Reponds uniquement en JSON valide.",
                temperature=0.1,
                max_tokens=500,
                json_mode=True
            )
            
            import json
            result = json.loads(llm_response.content)
            
            corrected_cmd = result.get("corrected_command", "")
            if corrected_cmd and corrected_cmd != failed_command:
                return result
            
            logger.warning("llm_suggested_same_command", command=corrected_cmd)
            return None
            
        except Exception as e:
            logger.error("llm_analysis_failed", error=str(e))
            return None
    
    def _extract_error_type(self, error_message: str) -> str:
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
    
    async def retry_with_correction(
        self,
        correction: Dict,
        slave_manager,
        slave_type: str,
        tool_name: str,
        original_parameters: Dict
    ) -> Tuple[bool, Optional[Dict]]:
        logger.info(
            "retrying_with_correction",
            source=correction["source"],
            confidence=correction["confidence"],
            corrected_command=correction["corrected_command"]
        )
        
        corrected_params = original_parameters.copy()
        corrected_params["command"] = correction["corrected_command"]
        
        try:
            result = await slave_manager.execute_tool(
                slave_type=slave_type,
                tool_name=tool_name,
                parameters=corrected_params
            )
            
            if result.get("success"):
                logger.info("auto_healing_successful")
                self.context_manager.error_patterns.mark_solution_success(
                    error_message=original_parameters.get("command", ""),
                    success=True
                )
                return True, result
            else:
                logger.warning("auto_healing_failed_retry")
                return False, result
                
        except Exception as e:
            logger.error("auto_healing_exception", error=str(e))
            return False, {"success": False, "error": str(e)}
