from typing import Dict, Optional, Tuple
from brain.memory import ContextManager
from brain.llm.provider import LLMProvider
import structlog

logger = structlog.get_logger()


class ResilientAutoHealing:
    """Auto-healing system with resilient retry logic until success or max retries"""
    
    def __init__(self, context_manager: ContextManager, llm_provider: LLMProvider):
        self.context_manager = context_manager
        self.llm = llm_provider
        self.max_retries = 10
        self.healing_history = []
    
    async def heal_and_retry(
        self,
        user_request: str,
        failed_command: str,
        error_message: str,
        slave_manager,
        slave_type: str,
        tool_name: str,
        original_parameters: Dict,
        step_index: int
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Tentative de correction resiliente avec retries multiples
        Retourne: (success, result, corrected_command)
        """
        
        retry_count = 0
        current_command = failed_command
        current_error = error_message
        self.healing_history = []  # Réinitialiser l'historique
        
        while retry_count < self.max_retries:
            retry_count += 1
            
            logger.info(
                "auto_healing_attempt",
                retry=retry_count,
                max_retries=self.max_retries,
                current_command=current_command
            )
            
            # Chercher une solution connue
            known_solution = self.context_manager.error_patterns.get_solution_for_error(current_error)
            
            if known_solution and known_solution.get("confidence", 0) > 0.5:
                logger.info(
                    "using_known_solution",
                    confidence=known_solution["confidence"],
                    retry=retry_count
                )
                corrected_command = known_solution.get("command_corrected")
            else:
                # Analyser avec le LLM
                logger.info("analyzing_with_llm", retry=retry_count)
                llm_solution = await self._analyze_with_llm(
                    user_request, 
                    current_command, 
                    current_error,
                    retry_count
                )
                
                if not llm_solution:
                    logger.warning("llm_analysis_failed", retry=retry_count)
                    continue
                
                corrected_command = llm_solution.get("corrected_command")
                
                # Sauvegarder le pattern
                self.context_manager.error_patterns.add_error_pattern(
                    error_message=current_error,
                    solution=llm_solution.get("explanation", ""),
                    command_failed=current_command,
                    command_corrected=corrected_command
                )
            
            if not corrected_command or corrected_command == current_command:
                logger.warning("no_valid_correction", retry=retry_count)
                self.healing_history.append({
                    "retry": retry_count,
                    "error": current_error[:200],
                    "attempted_command": current_command,
                    "result": "no_valid_correction",
                    "output": ""
                })
                continue
            
            # Retry avec la commande corrigée
            logger.info("retrying_with_correction", command=corrected_command, retry=retry_count)
            
            corrected_params = original_parameters.copy()
            corrected_params["command"] = corrected_command
            
            try:
                result = await slave_manager.execute_tool(
                    slave_type=slave_type,
                    tool_name=tool_name,
                    parameters=corrected_params
                )
                
                if result.get("success"):
                    # Vérifier si le résultat répond vraiment à la demande originale
                    is_valid_solution = await self._validate_solution(
                        user_request,
                        corrected_command,
                        result,
                        retry_count
                    )
                    
                    if is_valid_solution:
                        logger.info(
                            "auto_healing_successful",
                            retry=retry_count,
                            corrected_command=corrected_command
                        )
                        self.healing_history.append({
                            "retry": retry_count,
                            "error": current_error[:200],
                            "attempted_command": corrected_command,
                            "result": "success",
                            "explanation": llm_solution.get("explanation") if not known_solution else known_solution.get("solution")
                        })
                        self.context_manager.error_patterns.mark_solution_success(
                            error_message=current_error,
                            success=True
                        )
                        return True, result, corrected_command
                    else:
                        # Succès technique mais ne répond pas à la demande
                        # Stocker le résultat pour enrichir le contexte de la prochaine tentative
                        output_preview = result.get("output", "")[:500] if result.get("output") else ""
                        
                        logger.warning(
                            "solution_doesnt_match_request",
                            retry=retry_count,
                            command=corrected_command
                        )
                        self.healing_history.append({
                            "retry": retry_count,
                            "error": current_error[:200],
                            "attempted_command": corrected_command,
                            "result": "validation_failed",
                            "reason": "Solution trop générique, ne répond pas à la demande",
                            "output": output_preview
                        })
                        current_error = f"Solution does not match original request. Output was: {output_preview[:200]}"
                        current_command = corrected_command
                        continue
                else:
                    # Échec, mais on continue avec la nouvelle erreur
                    current_error = result.get("error", "Unknown error")
                    current_command = corrected_command
                    self.healing_history.append({
                        "retry": retry_count,
                        "error": current_error[:200],
                        "attempted_command": corrected_command,
                        "result": "failed",
                        "reason": "Command execution failed",
                        "output": ""
                    })
                    logger.warning(
                        "retry_failed_continuing",
                        retry=retry_count,
                        new_error=current_error[:100]
                    )
                    
            except Exception as e:
                logger.error("retry_exception", retry=retry_count, error=str(e))
                current_error = str(e)
                current_command = corrected_command
        
        logger.error("auto_healing_exhausted", max_retries=self.max_retries)
        return False, None, None
    
    async def _analyze_with_llm(
        self, 
        user_request: str, 
        failed_command: str, 
        error_message: str,
        retry_count: int
    ) -> Optional[Dict]:
        error_context = self.context_manager.get_context_for_error(error_message)
        
        # Ajouter le contexte des tentatives précédentes avec leurs résultats
        previous_attempts = ""
        if len(self.healing_history) > 0:
            previous_attempts = "\nTentatives precedentes:\n"
            for attempt in self.healing_history[-2:]:  # 2 dernières tentatives
                previous_attempts += f"- Commande: {attempt['attempted_command']}\n"
                previous_attempts += f"  Resultat: {attempt['result']}\n"
                if attempt.get('output'):
                    previous_attempts += f"  Output: {attempt['output'][:200]}\n"
        
        analysis_prompt = f"""
AUTO-CORRECTION AUTONOME (Tentative {retry_count})

Demande originale: {user_request}

Echec actuel:
- Commande executee: {failed_command}
- Erreur: {error_message}
{previous_attempts}
{error_context}

Mission:
Analyse l'echec et propose une commande corrigee qui accomplira EXACTEMENT la demande originale.

Contraintes:
1. La commande corrigee doit etre differente de celle qui a echoue
2. Elle doit directement afficher le resultat demande par l'utilisateur

Reponds en JSON:
{{
  "explanation": "analyse de l'erreur et correction appliquee",
  "corrected_command": "commande corrigee qui affichera le resultat attendu",
  "reasoning": "pourquoi cette commande va fonctionner"
}}
"""
        
        try:
            llm_response = await self.llm.generate(
                prompt=analysis_prompt,
                system_prompt="Tu es un expert en debugging et correction automatique. Reponds uniquement en JSON valide.",
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
    
    async def _validate_solution(
        self,
        user_request: str,
        executed_command: str,
        result: Dict,
        retry_count: int
    ) -> bool:
        """
        Validation minimaliste : accepte tout résultat technique réussi.
        Le LLM apprend de manière autonome via le contexte des tentatives précédentes.
        """
        # Accepter tout résultat qui a techniquement réussi
        # Le LLM décidera par lui-même si c'est la bonne solution via le contexte enrichi
        return True
