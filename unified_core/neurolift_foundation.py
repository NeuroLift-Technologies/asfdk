"""
NeuroLift Agent Solidarity Kit - Unified Agent Development Framework
Main implementation integrating RRT Advocate, NLT-OTOI Framework, and Sleepwalker Protocol

This module provides the central coordination hub for the complete NeuroLift agent ecosystem,
combining crisis intervention (RRTA), interaction governance (OTOI), and emotional continuity (SWP).
All agents developed by NeuroLift Technologies require this as the layer between the model and the agent.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pathlib import Path

# Import component integrations
from .integration.rrt_integration import RRTAdvocateIntegration
from .integration.toi_otoi_integration import TOIOTOIIntegration
from .integration.sleepwalker_integration import SleepwalkerIntegration
from .integration.vibevoice_integration import VibeVoiceIntegration
from .supervisor.supervisor_ai import SupervisorAI
from .core_coordination.state_manager import UnifiedStateManager
from .core_coordination.component_communication import ComponentCommunication

class FoundationMode(Enum):
    """Operating modes for the NeuroLift Agent Solidarity Kit"""
    UNIFIED = "unified"           # All components active
    CRISIS_ONLY = "crisis_only"   # RRT Advocate only
    CONTINUITY_ONLY = "continuity"  # Sleepwalker Protocol only
    FRAMEWORK_ONLY = "framework"  # NLT-OTOI only
    DEVELOPMENT = "development"   # Development mode with debugging

class InteractionType(Enum):
    """Types of user interactions supported by the Agent Solidarity Kit"""
    EMOTIONAL_ASSESSMENT = "emotional_assessment"
    CRISIS_ALERT = "crisis_alert"
    PREFERENCE_UPDATE = "preference_update"
    OPTIMIZATION_REQUEST = "optimization_request"
    STATUS_INQUIRY = "status_inquiry"
    EMERGENCY_ESCALATION = "emergency_escalation"

@dataclass
class FoundationConfig:
    """Configuration for the Agent Solidarity Framework Development Kit (ASFDK)"""
    user_id: str
    mode: FoundationMode
    components: Dict[str, bool] = field(default_factory=lambda: {
        "rrt_advocate": True,
        "toi_otoi_framework": True,
        "sleepwalker_protocol": True,
        "supervisor_ai": True,
        "vibevoice": False,  # opt-in only; requires pip install asfdk[voice]
    })
    privacy_settings: Dict[str, Any] = field(default_factory=dict)
    performance_settings: Dict[str, Any] = field(default_factory=dict)
    integration_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserInteraction:
    """Represents a user interaction with the foundation"""
    timestamp: datetime
    interaction_type: InteractionType
    data: Dict[str, Any]
    user_id: str
    session_id: Optional[str] = None
    priority: int = 1  # 1-5, where 5 is highest priority
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FoundationResponse:
    """Response from the Agent Solidarity Framework Development Kit (ASFDK)"""
    timestamp: datetime
    response_type: str
    content: Dict[str, Any]
    components_involved: List[str]
    success: bool
    execution_time: float
    follow_up_required: bool = False
    user_feedback_requested: bool = False

class NeuroLiftFoundation:
    """
    NeuroLift Agent Solidarity Kit - Unified Agent Development Framework
    
    Central coordination hub integrating RRT Advocate, NLT-OTOI Framework,
    and Sleepwalker Protocol into a cohesive agent governance layer.
    All NLT agents use this as the layer between the model and the agent.
    """
    
    def __init__(self, config: FoundationConfig):
        """
        Initialize the NeuroLift Agent Solidarity Kit
        
        Args:
            config: Foundation configuration including user ID and component settings
        """
        self.config = config
        self.user_id = config.user_id
        self.mode = config.mode
        
        # Initialize logging
        self.logger = logging.getLogger(f"NeuroLiftFoundation-{self.user_id}")
        self._setup_logging()
        
        # Core components (initialized as None, loaded during startup)
        self.rrt: Optional[RRTAdvocateIntegration] = None
        self.framework: Optional[TOIOTOIIntegration] = None
        self.sleepwalker: Optional[SleepwalkerIntegration] = None
        self.supervisor: Optional[SupervisorAI] = None
        self.voice: Optional[VibeVoiceIntegration] = None
        
        # Coordination systems
        self.state_manager: Optional[UnifiedStateManager] = None
        self.communication: Optional[ComponentCommunication] = None
        
        # System state
        self.is_initialized = False
        self.is_running = False
        self.startup_time: Optional[datetime] = None
        self.interaction_history: List[UserInteraction] = []
        self.response_history: List[FoundationResponse] = []
        
        # Performance tracking
        self.performance_metrics = {
            "total_interactions": 0,
            "avg_response_time": 0.0,
            "component_usage": {},
            "error_count": 0,
            "uptime": timedelta(0)
        }
        
        self.logger.info(f"Agent Solidarity Framework Development Kit (ASFDK) created for user {self.user_id} in {self.mode.value} mode")

    def _setup_logging(self):
        """Configure logging for the foundation"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    async def initialize(self) -> bool:
        """
        Initialize all foundation components
        
        Returns:
            bool: True if initialization successful
        """
        if self.is_initialized:
            self.logger.warning("Foundation already initialized")
            return True
            
        try:
            self.logger.info("Initializing Agent Solidarity Framework Development Kit (ASFDK)...")
            start_time = datetime.now()
            
            # Initialize state management first
            self.state_manager = UnifiedStateManager(self.user_id)
            await self.state_manager.initialize()
            
            # Initialize component communication
            self.communication = ComponentCommunication(self.state_manager)
            
            # Initialize components based on configuration
            if self.config.components.get("rrt_advocate", True):
                self.rrt = RRTAdvocateIntegration(self)
                await self.rrt.initialize()
                self.logger.info("RRT Advocate integration initialized")
            
            if self.config.components.get("toi_otoi_framework", True):
                self.framework = TOIOTOIIntegration(self)
                await self.framework.initialize()
                self.logger.info("TOI-OTOI Framework integration initialized")
            
            if self.config.components.get("sleepwalker_protocol", True):
                self.sleepwalker = SleepwalkerIntegration(self)
                await self.sleepwalker.initialize()
                self.logger.info("Sleepwalker Protocol integration initialized")
            
            if self.config.components.get("supervisor_ai", True):
                self.supervisor = SupervisorAI(self)
                await self.supervisor.initialize()
                await self.supervisor.start()
                self.logger.info("Supervisor AI initialized")

            if self.config.components.get("vibevoice", False):
                from .integration.vibevoice_integration import _VIBEVOICE_AVAILABLE
                if not _VIBEVOICE_AVAILABLE:
                    raise RuntimeError(
                        "vibevoice was enabled in components but its dependencies are not installed. "
                        "Run: pip install asfdk[voice]"
                    )
                self.voice = VibeVoiceIntegration(self)
                await self.voice.initialize()
                self.logger.info("VibeVoice integration initialized")
            
            # Establish inter-component communication
            await self._establish_component_communication()
            
            # Perform system health check
            health_status = await self.health_check()
            if not health_status["overall_healthy"]:
                self.logger.warning(f"System health check reported issues at startup: {health_status}")
            
            # Mark as initialized
            self.is_initialized = True
            self.startup_time = datetime.now()
            
            initialization_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Agent Solidarity Framework Development Kit (ASFDK) initialized successfully in {initialization_time:.2f}s")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Foundation initialization failed: {e}")
            await self._cleanup_partial_initialization()
            return False

    async def _establish_component_communication(self):
        """Establish communication channels between components"""
        if self.rrt and self.sleepwalker:
            await self.communication.link_rrt_sleepwalker(self.rrt, self.sleepwalker)
            
        if self.sleepwalker and self.framework:
            await self.communication.link_sleepwalker_framework(self.sleepwalker, self.framework)
            
        if self.framework and self.rrt:
            await self.communication.link_framework_rrt(self.framework, self.rrt)
            
        if self.supervisor:
            await self.communication.link_supervisor(
                self.supervisor, [self.rrt, self.framework, self.sleepwalker]
            )

    async def start(self) -> bool:
        """
        Start the Agent Solidarity Framework Development Kit (ASFDK)
        
        Returns:
            bool: True if startup successful
        """
        if not self.is_initialized:
            self.logger.error("Cannot start foundation - not initialized")
            return False
            
        if self.is_running:
            self.logger.warning("Foundation already running")
            return True
            
        try:
            self.logger.info("Starting Agent Solidarity Framework Development Kit (ASFDK)...")
            
            # Start all active components
            if self.rrt:
                await self.rrt.start()
                
            if self.framework:
                await self.framework.start()
                
            if self.sleepwalker:
                await self.sleepwalker.start()
                
            if self.supervisor:
                await self.supervisor.start()

            if self.voice:
                await self.voice.start()
            
            # Start background tasks
            asyncio.create_task(self._performance_monitoring_loop())
            asyncio.create_task(self._health_monitoring_loop())
            
            self.is_running = True
            self.logger.info("Agent Solidarity Framework Development Kit (ASFDK) started successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Foundation startup failed: {e}")
            return False

    async def process_interaction(self, interaction: UserInteraction) -> FoundationResponse:
        """
        Process a user interaction through the appropriate components
        
        Args:
            interaction: User interaction to process
            
        Returns:
            FoundationResponse: Response from the system
        """
        if not self.is_running:
            return FoundationResponse(
                timestamp=datetime.now(),
                response_type="error",
                content={"error": "Foundation not running"},
                components_involved=[],
                success=False,
                execution_time=0.0
            )
        
        start_time = datetime.now()
        components_involved = []
        
        try:
            self.logger.info(f"Processing {interaction.interaction_type.value} interaction")
            
            # Add to interaction history
            self.interaction_history.append(interaction)
            
            # Route interaction based on type and priority
            response_content = {}
            
            if interaction.interaction_type == InteractionType.EMOTIONAL_ASSESSMENT:
                if self.sleepwalker:
                    response_content = await self.sleepwalker.assess_emotional_state(
                        interaction.data.get("user_input", ""),
                        interaction.data.get("session_history")
                    )
                    components_involved.append("sleepwalker_protocol")
                else:
                    raise Exception("Sleepwalker Protocol not available")
                    
            elif interaction.interaction_type == InteractionType.CRISIS_ALERT:
                if self.rrt:
                    response_content = await self.rrt.handle_crisis(interaction.data)
                    components_involved.append("rrt_advocate")
                    
                    # Notify sleepwalker for emotional continuity tracking
                    if self.sleepwalker:
                        await self.sleepwalker.assess_emotional_state(
                            str(interaction.data),
                            []
                        )
                        components_involved.append("sleepwalker_protocol")
                else:
                    raise Exception("RRT Advocate not available")
                    
            elif interaction.interaction_type == InteractionType.PREFERENCE_UPDATE:
                if self.framework:
                    response_content = await self.framework.update_preferences(interaction.data)
                    components_involved.append("toi_otoi_framework")
                else:
                    raise Exception("TOI-OTOI Framework not available")
                    
            elif interaction.interaction_type == InteractionType.OPTIMIZATION_REQUEST:
                if self.framework:
                    response_content = await self.framework.optimize_system(interaction.data)
                    components_involved.append("toi_otoi_framework")
                else:
                    raise Exception("TOI-OTOI Framework not available")
                    
            elif interaction.interaction_type == InteractionType.STATUS_INQUIRY:
                response_content = await self.get_system_status()
                components_involved.append("foundation_core")
                
            elif interaction.interaction_type == InteractionType.EMERGENCY_ESCALATION:
                # Emergency escalation involves all available components
                if self.rrt:
                    crisis_response = await self.rrt.emergency_escalation(interaction.data)
                    response_content.update(crisis_response)
                    components_involved.append("rrt_advocate")
                    
                if self.sleepwalker:
                    swp_response = await self.sleepwalker.assess_emotional_state(
                        str(interaction.data), []
                    )
                    response_content.update(swp_response)
                    components_involved.append("sleepwalker_protocol")
                    
                if self.supervisor:
                    supervisor_response = await self.supervisor.coordinate_emergency(interaction.data)
                    response_content.update(supervisor_response)
                    components_involved.append("supervisor_ai")
            
            else:
                # Route to supervisor for coordination
                if self.supervisor:
                    response_content = await self.supervisor.coordinate_response(
                        interaction.interaction_type, interaction.data
                    )
                    components_involved.append("supervisor_ai")
                else:
                    raise Exception(f"Unknown interaction type: {interaction.interaction_type}")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = FoundationResponse(
                timestamp=datetime.now(),
                response_type=interaction.interaction_type.value,
                content=response_content,
                components_involved=components_involved,
                success=True,
                execution_time=execution_time
            )
            
            # Add to response history
            self.response_history.append(response)
            
            # Update performance metrics
            self._update_performance_metrics(response)
            
            # Check if optimization is needed
            if self.framework:
                await self.framework.analyze_interaction_for_optimization(interaction, response)
            
            self.logger.info(f"Interaction processed successfully in {execution_time:.3f}s")
            
            return response
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Interaction processing failed: {e}")
            
            # Create error response
            error_response = FoundationResponse(
                timestamp=datetime.now(),
                response_type="error",
                content={"error": str(e), "interaction_type": interaction.interaction_type.value},
                components_involved=components_involved,
                success=False,
                execution_time=execution_time
            )
            
            self.response_history.append(error_response)
            self.performance_metrics["error_count"] += 1
            
            return error_response

    async def assess_emotional_state(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess emotional state through the Sleepwalker Protocol
        
        Args:
            user_input: User input text to assess
            context: Additional context for the assessment
            
        Returns:
            Dict containing emotional state assessment
        """
        interaction = UserInteraction(
            timestamp=datetime.now(),
            interaction_type=InteractionType.EMOTIONAL_ASSESSMENT,
            data={"user_input": user_input, "context": context or {}},
            user_id=self.user_id
        )
        
        response = await self.process_interaction(interaction)
        
        if response.success:
            return response.content
        else:
            return {"error": "Assessment failed", "details": response.content}

    async def crisis_alert(self, crisis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle crisis alert
        
        Args:
            crisis_data: Crisis information and context
            
        Returns:
            Dict containing crisis response information
        """
        interaction = UserInteraction(
            timestamp=datetime.now(),
            interaction_type=InteractionType.CRISIS_ALERT,
            data=crisis_data,
            user_id=self.user_id,
            priority=5  # Highest priority
        )
        
        response = await self.process_interaction(interaction)
        return response.content

    async def update_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences
        
        Args:
            preferences: User preference updates
            
        Returns:
            bool: True if preferences updated successfully
        """
        interaction = UserInteraction(
            timestamp=datetime.now(),
            interaction_type=InteractionType.PREFERENCE_UPDATE,
            data=preferences,
            user_id=self.user_id
        )
        
        response = await self.process_interaction(interaction)
        return response.success

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        
        Returns:
            Dict containing system status information
        """
        status = {
            "foundation": {
                "initialized": self.is_initialized,
                "running": self.is_running,
                "mode": self.mode.value,
                "uptime": (datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0
            },
            "components": {},
            "performance": self.performance_metrics.copy(),
            "health": await self.health_check()
        }
        
        # Get component statuses
        if self.rrt:
            status["components"]["rrt_advocate"] = await self.rrt.get_status()
            
        if self.framework:
            status["components"]["toi_otoi_framework"] = await self.framework.get_status()
            
        if self.sleepwalker:
            status["components"]["sleepwalker_protocol"] = await self.sleepwalker.get_status()
            
        if self.supervisor:
            status["components"]["supervisor_ai"] = await self.supervisor.get_status()
        
        return status

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Returns:
            Dict containing health check results
        """
        health_status = {
            "overall_healthy": True,
            "components": {},
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Check each component
        if self.rrt:
            rrt_health = await self.rrt.health_check()
            health_status["components"]["rrt_advocate"] = rrt_health
            if not rrt_health.get("healthy", False):
                health_status["overall_healthy"] = False
                health_status["issues"].extend(rrt_health.get("issues", []))
        
        if self.framework:
            framework_health = await self.framework.health_check()
            health_status["components"]["toi_otoi_framework"] = framework_health
            if not framework_health.get("healthy", False):
                health_status["overall_healthy"] = False
                health_status["issues"].extend(framework_health.get("issues", []))
        
        if self.sleepwalker:
            swp_health = await self.sleepwalker.health_check()
            health_status["components"]["sleepwalker_protocol"] = swp_health
            if not swp_health.get("healthy", False):
                health_status["overall_healthy"] = False
                health_status["issues"].extend(swp_health.get("issues", []))
        
        if self.supervisor:
            supervisor_health = await self.supervisor.health_check()
            health_status["components"]["supervisor_ai"] = supervisor_health
            if not supervisor_health.get("healthy", False):
                health_status["overall_healthy"] = False
                health_status["issues"].extend(supervisor_health.get("issues", []))
        
        return health_status

    def _update_performance_metrics(self, response: FoundationResponse):
        """Update performance metrics based on response"""
        self.performance_metrics["total_interactions"] += 1
        
        # Update average response time
        total_time = (self.performance_metrics["avg_response_time"] * 
                     (self.performance_metrics["total_interactions"] - 1) + 
                     response.execution_time)
        self.performance_metrics["avg_response_time"] = total_time / self.performance_metrics["total_interactions"]
        
        # Update component usage
        for component in response.components_involved:
            if component not in self.performance_metrics["component_usage"]:
                self.performance_metrics["component_usage"][component] = 0
            self.performance_metrics["component_usage"][component] += 1
        
        # Update uptime
        if self.startup_time:
            self.performance_metrics["uptime"] = datetime.now() - self.startup_time

    async def _performance_monitoring_loop(self):
        """Background task for performance monitoring"""
        while self.is_running:
            try:
                # Log performance metrics every 5 minutes
                await asyncio.sleep(300)
                
                if self.performance_metrics["total_interactions"] > 0:
                    self.logger.info(
                        f"Performance: {self.performance_metrics['total_interactions']} interactions, "
                        f"avg response time: {self.performance_metrics['avg_response_time']:.3f}s, "
                        f"errors: {self.performance_metrics['error_count']}"
                    )
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")

    async def _health_monitoring_loop(self):
        """Background task for health monitoring"""
        while self.is_running:
            try:
                # Health check every 10 minutes
                await asyncio.sleep(600)
                
                health_status = await self.health_check()
                if not health_status["overall_healthy"]:
                    self.logger.warning(f"Health issues detected: {health_status['issues']}")
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")

    async def _cleanup_partial_initialization(self):
        """Clean up partially initialized components"""
        try:
            if self.rrt:
                await self.rrt.shutdown()
            if self.framework:
                await self.framework.shutdown()
            if self.sleepwalker:
                await self.sleepwalker.shutdown()
            if self.supervisor:
                await self.supervisor.shutdown()
            if self.state_manager:
                await self.state_manager.shutdown()
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    async def shutdown(self):
        """Gracefully shutdown the NeuroLift Agent Solidarity Kit"""
        self.logger.info("Shutting down NeuroLift Agent Solidarity Kit...")
        
        try:
            self.is_running = False
            
            # Shutdown components in reverse order
            if self.supervisor:
                await self.supervisor.shutdown()
                
            if self.sleepwalker:
                await self.sleepwalker.shutdown()
                
            if self.framework:
                await self.framework.shutdown()
                
            if self.rrt:
                await self.rrt.shutdown()
                
            if self.state_manager:
                await self.state_manager.shutdown()
            
            # Log final statistics
            final_status = await self.get_system_status()
            self.logger.info(f"Final status: {json.dumps(final_status, indent=2, default=str)}")
            
            self.logger.info("NeuroLift Agent Solidarity Kit shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

async def create_foundation(user_id: str, 
                          mode: FoundationMode = FoundationMode.UNIFIED,
                          config_path: Optional[str] = None) -> NeuroLiftFoundation:
    """
    Factory function to create and initialize the Agent Solidarity Framework Development Kit (ASFDK)
    
    Args:
        user_id: Unique identifier for the user
        mode: Operating mode for the foundation
        config_path: Path to configuration file
        
    Returns:
        Initialized Agent Solidarity Framework Development Kit (ASFDK) instance
    """
    # Load configuration
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
    else:
        config_data = {}
    
    # Create configuration
    config = FoundationConfig(
        user_id=user_id,
        mode=mode,
        components=config_data.get("components", {}),
        privacy_settings=config_data.get("privacy", {}),
        performance_settings=config_data.get("performance", {}),
        integration_settings=config_data.get("integration", {})
    )
    
    # Create and initialize foundation
    foundation = NeuroLiftFoundation(config)
    
    if await foundation.initialize():
        await foundation.start()
        return foundation
    else:
        raise Exception("Failed to initialize Agent Solidarity Framework Development Kit (ASFDK)")


# ============================================================================
# MAIN EXECUTION (for testing)
# ============================================================================

async def main():
    """Main function for testing NeuroLift Agent Solidarity Kit"""
    print("NeuroLift Agent Solidarity Kit - Unified Agent Development Framework")
    print("=" * 60)
    
    try:
        # Create foundation
        foundation = await create_foundation("test_user_001", FoundationMode.UNIFIED)
        
        # Test emotional state assessment via Sleepwalker Protocol
        assessment = await foundation.assess_emotional_state(
            "I'm feeling a bit overwhelmed with work today",
            {"mood": "anxious", "energy": "low"}
        )
        print(f"Emotional Assessment: {assessment}")
        
        # Test system status
        status = await foundation.get_system_status()
        print(f"System Status: {json.dumps(status, indent=2, default=str)}")
        
        # Run for a short test period
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        if 'foundation' in locals():
            await foundation.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
