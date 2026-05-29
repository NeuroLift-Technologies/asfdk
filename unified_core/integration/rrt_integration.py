"""
RRT Advocate Integration Module
Integrates the RRT Advocate with the Agent Solidarity Framework Development Kit (ASFDK)
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os

# Add RRT Advocate to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../rrt-advocate/src'))

try:
    from rrt_advocate import RRTAdvocate, CrisisAssessment, CrisisLevel
except ImportError:
    # Fallback for development
    class RRTAdvocate:
        def __init__(self, *args, **kwargs):
            pass
    class CrisisAssessment:
        pass
    class CrisisLevel:
        GREEN = "green"

class RRTAdvocateIntegration:
    """Integration wrapper for RRT Advocate within the unified foundation"""
    
    def __init__(self, foundation):
        self.foundation = foundation
        self.user_id = foundation.user_id
        self.rrt_advocate: Optional[RRTAdvocate] = None
        self.is_initialized = False
        self.is_monitoring = False
        
        self.logger = logging.getLogger(f"RRTIntegration-{self.user_id}")
        
    async def initialize(self) -> bool:
        """Initialize the RRT Advocate integration"""
        try:
            # Initialize RRT Advocate with foundation context
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '../../rrt-advocate/config/crisis_thresholds.yaml'
            )
            
            self.rrt_advocate = RRTAdvocate(
                user_id=self.user_id,
                config_path=config_path,
                supervisor_interface=self.foundation.supervisor if hasattr(self.foundation, 'supervisor') else None
            )
            
            self.is_initialized = True
            self.logger.info("RRT Advocate integration initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"RRT Advocate integration initialization failed: {e}")
            return False
    
    async def start(self) -> bool:
        """Start RRT Advocate monitoring"""
        if not self.is_initialized:
            return False
            
        try:
            if self.rrt_advocate:
                await self.rrt_advocate.start_monitoring()
                self.is_monitoring = True
                self.logger.info("RRT Advocate monitoring started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start RRT Advocate: {e}")
            return False
    
    async def handle_crisis(self, crisis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle crisis through RRT Advocate"""
        if not self.rrt_advocate:
            return {"error": "RRT Advocate not available"}
            
        try:
            # If the caller supplied message text, evaluate it directly via the
            # text entrypoint; otherwise fall back to ambient-state assessment.
            message = crisis_data.get("text") or crisis_data.get("message")
            if message and hasattr(self.rrt_advocate, "assess_message"):
                assessment = await self.rrt_advocate.assess_message(
                    message, messages=crisis_data.get("messages")
                )
            else:
                assessment = await self.rrt_advocate.assess_current_state()

            # Handle based on crisis level
            if assessment.crisis_level != CrisisLevel.GREEN:
                await self.rrt_advocate._handle_crisis(assessment)
                
                # Notify other components if needed
                if hasattr(self.foundation, 'voice') and self.foundation.voice:
                    await self._notify_voice_interface(assessment)
                    
                if hasattr(self.foundation, 'framework') and self.foundation.framework:
                    await self._notify_framework(assessment)
            
            return {
                "crisis_level": assessment.crisis_level.value,
                "confidence": assessment.confidence_score,
                "interventions_deployed": len(self.rrt_advocate.active_interventions),
                "status": "handled"
            }
            
        except Exception as e:
            self.logger.error(f"Crisis handling failed: {e}")
            return {"error": str(e)}
    
    async def emergency_escalation(self, emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency escalation"""
        if not self.rrt_advocate:
            return {"error": "RRT Advocate not available"}
            
        try:
            # Create emergency assessment
            assessment = CrisisAssessment(
                timestamp=datetime.now(),
                crisis_level=CrisisLevel.BLACK,
                primary_indicators=emergency_data.get("indicators", []),
                secondary_indicators=[],
                confidence_score=1.0,
                estimated_duration=None,
                recommended_interventions=["emergency_stabilization"],
                escalation_threshold=0.0,
                user_safety_score=0.1
            )
            
            await self.rrt_advocate._emergency_escalation(assessment)
            
            return {
                "status": "emergency_escalated",
                "timestamp": assessment.timestamp.isoformat(),
                "protocols_activated": True
            }
            
        except Exception as e:
            self.logger.error(f"Emergency escalation failed: {e}")
            return {"error": str(e)}
    
    async def _notify_voice_interface(self, assessment: CrisisAssessment):
        """Notify voice interface of crisis for voice support"""
        try:
            if hasattr(self.foundation, 'communication'):
                await self.foundation.communication.rrt_to_voice({
                    "crisis_level": assessment.crisis_level.value,
                    "confidence": assessment.confidence_score,
                    "support_needed": True
                })
        except Exception as e:
            self.logger.error(f"Failed to notify voice interface: {e}")
    
    async def _notify_framework(self, assessment: CrisisAssessment):
        """Notify TOI-OTOI framework for optimization"""
        try:
            if hasattr(self.foundation, 'communication'):
                await self.foundation.communication.rrt_to_framework({
                    "crisis_data": assessment,
                    "optimization_request": True
                })
        except Exception as e:
            self.logger.error(f"Failed to notify framework: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get RRT Advocate status"""
        if not self.rrt_advocate:
            return {"available": False}
            
        try:
            status = await self.rrt_advocate.get_status_report()
            status["integration_status"] = {
                "initialized": self.is_initialized,
                "monitoring": self.is_monitoring
            }
            return status
            
        except Exception as e:
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        health = {
            "healthy": True,
            "issues": [],
            "component": "rrt_advocate"
        }
        
        if not self.is_initialized:
            health["healthy"] = False
            health["issues"].append("Not initialized")
            
        if self.is_initialized and not self.is_monitoring:
            health["healthy"] = False
            health["issues"].append("Not monitoring")
            
        if self.rrt_advocate:
            try:
                rrt_status = await self.rrt_advocate.get_status_report()
                history_count = rrt_status.get("crisis_history_count", 0)
                success_rate = rrt_status.get("performance", {}).get("success_rate", 1.0)
                if history_count > 0 and success_rate < 0.5:
                    health["healthy"] = False
                    health["issues"].append("Low success rate")
            except Exception as e:
                health["healthy"] = False
                health["issues"].append(f"Status check failed: {e}")
        
        return health
    
    async def shutdown(self):
        """Shutdown RRT Advocate integration"""
        try:
            if self.rrt_advocate:
                await self.rrt_advocate.shutdown()
            self.is_monitoring = False
            self.logger.info("RRT Advocate integration shutdown")
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
