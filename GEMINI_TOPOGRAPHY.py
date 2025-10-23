"""
GEMINI_TOPOGRAPHY.py - NeuroLift Foundation Repository Structure and Metadata

This file provides comprehensive information about the NeuroLift Foundation repository
structure, component integration, and data relationships for AI system understanding.

Repository: neurolift-foundation
Purpose: Unified ADHD Support System combining RRT Advocate, TOI-OTOI Framework, and Aimybox Voice Interface
Owner: JDUB1216 (Joshua Dorsey)
Organization: NeuroLift Technologies
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ComponentInfo:
    """Information about a foundation component"""
    name: str
    source_repository: str
    source_branch: str
    local_path: str
    description: str
    capabilities: List[str]
    dependencies: List[str]
    integration_points: List[str]
    last_sync: Optional[str] = None

@dataclass
class RepositoryTopography:
    """Complete repository structure and metadata"""
    
    # Repository Metadata
    repository_name: str = "neurolift-foundation"
    repository_url: str = "https://github.com/JDUB1216/neurolift-foundation"
    owner: str = "JDUB1216"
    organization: str = "NeuroLift Technologies"
    
    # Project Information
    project_title: str = "NeuroLift Foundation - Unified ADHD Support System"
    project_description: str = """
    Comprehensive unified platform integrating three core components into a single,
    cohesive ADHD support system: RRT Advocate (crisis intervention), TOI-OTOI Framework
    (intelligent optimization), and Aimybox Voice Interface (natural voice interaction).
    """
    
    # Notion Integration
    notion_project_url: str = "https://www.notion.so/27a555e42dea818a9f4dd6178a92c38f"
    notion_workspace: str = "NeuroLift Technologies"
    
    # Technical Specifications
    primary_language: str = "Python"
    python_version: str = "3.11+"
    framework: str = "AsyncIO-based unified architecture"
    architecture_pattern: str = "Component Integration with Supervisor Coordination"
    
    # Component Integration
    components: Dict[str, ComponentInfo] = field(default_factory=lambda: {
        "rrt_advocate": ComponentInfo(
            name="RRT Advocate",
            source_repository="https://github.com/JDUB1216/rrt-advocate",
            source_branch="main",
            local_path="rrt-advocate/",
            description="Rapid Response Team for crisis intervention and immediate ADHD support",
            capabilities=[
                "Crisis detection and assessment",
                "Emergency intervention protocols", 
                "Multi-level crisis response (Green→Yellow→Orange→Red→Black)",
                "External resource coordination",
                "Real-time monitoring",
                "Sub-5-second response time"
            ],
            dependencies=[
                "asyncio", "datetime", "yaml", "logging"
            ],
            integration_points=[
                "unified_core.integration.rrt_integration",
                "Voice Interface (crisis support)",
                "TOI-OTOI Framework (optimization)",
                "Supervisor AI (coordination)"
            ]
        ),
        
        "toi_otoi_framework": ComponentInfo(
            name="TOI-OTOI Framework",
            source_repository="https://github.com/JDUB1216/nlt-otoi",
            source_branch="main", 
            local_path="toi-otoi-framework/",
            description="Terms of Interaction and Orchestrated Terms of Interaction",
            capabilities=[
                "Terms of Interaction (TOI) management",
                "Orchestrated Terms of Interaction (OTOI)",
                "User preference learning and adaptation",
                "System-wide optimization coordination",
                "Privacy-first personalization",
                "Continuous improvement algorithms"
            ],
            dependencies=[
                "asyncio", "json", "datetime", "typing"
            ],
            integration_points=[
                "unified_core.integration.toi_otoi_integration",
                "Voice Interface (preference capture)",
                "RRT Advocate (crisis optimization)",
                "Supervisor AI (system optimization)"
            ]
        ),
        
        "aimybox_voice": ComponentInfo(
            name="Aimybox Voice Interface",
            source_repository="https://github.com/JDUB1216/aimybox-android-assistant",
            source_branch="master",
            local_path="aimybox-voice/",
            description="Natural language voice interaction capabilities with stress detection",
            capabilities=[
                "Speech-to-text processing",
                "Text-to-speech synthesis",
                "Natural language understanding",
                "Voice stress pattern analysis",
                "Emotional tone detection",
                "Crisis voice support"
            ],
            dependencies=[
                "Android SDK", "Kotlin", "Aimybox SDK", "Yandex Speech Services"
            ],
            integration_points=[
                "unified_core.integration.voice_integration",
                "RRT Advocate (stress detection)",
                "TOI-OTOI Framework (voice preferences)",
                "Supervisor AI (voice coordination)"
            ]
        )
    })
    
    # Directory Structure
    directory_structure: Dict[str, Any] = field(default_factory=lambda: {
        "root": {
            "README.md": "Comprehensive project documentation and usage guide",
            "GEMINI_TOPOGRAPHY.py": "Repository structure and metadata (this file)",
            "requirements.txt": "Python dependencies for unified core",
            "package.json": "Node.js dependencies for voice interface",
            ".gitignore": "Git ignore patterns",
            "LICENSE": "MIT License"
        },
        
        "rrt-advocate/": {
            "description": "Crisis intervention component (synced from upstream)",
            "src/": {
                "rrt_advocate.py": "Main RRT Advocate implementation",
                "crisis_assessment.py": "Crisis detection and assessment logic",
                "intervention_protocols.py": "Crisis intervention strategies"
            },
            "config/": {
                "crisis_thresholds.yaml": "Crisis detection thresholds and settings"
            },
            "docs/": {
                "integration_guide.md": "Integration documentation"
            },
            "README.md": "RRT Advocate specific documentation",
            "GEMINI_TOPOGRAPHY.py": "RRT Advocate repository metadata"
        },
        
        "toi-otoi-framework/": {
            "description": "Optimization framework (synced from upstream)",
            "GEMINI_TOPOGRAPHY.py": "TOI-OTOI Framework repository metadata",
            "README.md": "Framework documentation"
        },
        
        "aimybox-voice/": {
            "description": "Voice interface component (synced from upstream)",
            "app/": {
                "src/main/java/com/justai/aimybox/assistant/": "Android application source",
                "src/main/res/": "Android resources and configurations"
            },
            "gradle/": "Gradle build system files",
            "README.md": "Aimybox voice interface documentation",
            "build.gradle.kts": "Kotlin build configuration"
        },
        
        "unified-core/": {
            "description": "Integration layer and unified system coordination",
            "neurolift_foundation.py": "Main foundation class and factory functions",
            
            "integration/": {
                "description": "Component integration modules",
                "rrt_integration.py": "RRT Advocate integration wrapper",
                "toi_otoi_integration.py": "TOI-OTOI Framework integration wrapper", 
                "voice_integration.py": "Voice Interface integration wrapper"
            },
            
            "supervisor/": {
                "description": "Supervisor AI coordination",
                "supervisor_ai.py": "Central coordination hub for all Advocates"
            },
            
            "coordination/": {
                "description": "Cross-component coordination systems",
                "component_communication.py": "Inter-component messaging and coordination",
                "state_manager.py": "Unified state management with privacy controls"
            }
        },
        
        "docs/": {
            "description": "Comprehensive documentation",
            "unified_architecture.md": "Detailed architecture and integration design",
            "api/": "API documentation for each component",
            "integration_patterns.md": "Component integration patterns",
            "state_management.md": "State management guide",
            "communication.md": "Communication protocols"
        },
        
        "scripts/": {
            "description": "Automation and utility scripts",
            "sync_upstream.sh": "Manual upstream synchronization script",
            "update_topography.py": "GEMINI_TOPOGRAPHY update automation",
            "test_integration.sh": "Integration testing script"
        },
        
        ".github/workflows/": {
            "description": "GitHub Actions automation",
            "upstream-sync.yml": "Automated daily upstream synchronization"
        },
        
        "config/": {
            "description": "Configuration files",
            "foundation.yml": "Foundation-wide configuration",
            "components.yml": "Component-specific settings"
        },
        
        "tests/": {
            "description": "Test suites",
            "test_rrt_integration.py": "RRT Advocate integration tests",
            "test_voice_integration.py": "Voice Interface integration tests", 
            "test_toi_otoi_integration.py": "TOI-OTOI Framework integration tests",
            "test_foundation.py": "Unified foundation tests",
            "manual/": "Manual testing scripts"
        }
    })
    
    # Data Flow and Integration Patterns
    data_flow: Dict[str, Any] = field(default_factory=lambda: {
        "user_interaction_flow": [
            "User Input → Voice Interface → Natural Language Processing",
            "Intent Recognition → Component Routing → Specialized Processing", 
            "RRT Advocate ← → TOI-OTOI Framework ← → Voice Interface",
            "Unified Response Generation → Voice Output → User Feedback",
            "OTOI Optimization → System Learning → Improved Responses"
        ],
        
        "crisis_response_flow": [
            "Crisis Detection (Voice/Behavioral) → RRT Advocate Assessment",
            "Crisis Level Determination → Intervention Protocol Selection",
            "Voice Interface Notification → Calming Support Delivery",
            "TOI-OTOI Optimization → Response Personalization",
            "Supervisor AI Coordination → Multi-component Response"
        ],
        
        "optimization_flow": [
            "User Interaction Data → TOI-OTOI Analysis",
            "Pattern Recognition → Optimization Opportunities",
            "Component Performance Analysis → Improvement Recommendations",
            "User Preference Learning → System Adaptation",
            "Continuous Feedback Loop → Enhanced Effectiveness"
        ]
    })
    
    # Synchronization Configuration
    synchronization: Dict[str, Any] = field(default_factory=lambda: {
        "strategy": "Git Subtree with Upstream Tracking",
        "automation": "GitHub Actions (daily at 2 AM UTC)",
        "manual_sync": "scripts/sync_upstream.sh",
        
        "upstream_repositories": {
            "rrt-advocate": {
                "url": "https://github.com/JDUB1216/rrt-advocate",
                "branch": "main",
                "sync_prefix": "rrt-advocate",
                "remote_name": "rrt-upstream"
            },
            "toi-otoi-framework": {
                "url": "https://github.com/JDUB1216/nlt-otoi", 
                "branch": "main",
                "sync_prefix": "toi-otoi-framework",
                "remote_name": "toi-otoi-upstream"
            },
            "aimybox-voice": {
                "url": "https://github.com/JDUB1216/aimybox-android-assistant",
                "branch": "master",
                "sync_prefix": "aimybox-voice", 
                "remote_name": "aimybox-upstream"
            }
        },
        
        "sync_commands": {
            "setup_remotes": [
                "git remote add rrt-upstream https://github.com/JDUB1216/rrt-advocate.git",
                "git remote add toi-otoi-upstream https://github.com/JDUB1216/nlt-otoi.git", 
                "git remote add aimybox-upstream https://github.com/JDUB1216/aimybox-android-assistant.git"
            ],
            "sync_all": [
                "git subtree pull --prefix=rrt-advocate rrt-upstream main --squash",
                "git subtree pull --prefix=toi-otoi-framework toi-otoi-upstream main --squash",
                "git subtree pull --prefix=aimybox-voice aimybox-upstream master --squash"
            ]
        }
    })
    
    # Development and Deployment
    development: Dict[str, Any] = field(default_factory=lambda: {
        "development_approach": "Component-first development with unified integration",
        "testing_strategy": "Component isolation + integration testing",
        "deployment_model": "Local-first with optional cloud deployment",
        
        "key_principles": [
            "Privacy-first design with local processing",
            "User agency and complete control",
            "Modular architecture with clear separation",
            "Async processing for responsiveness", 
            "Comprehensive error handling and recovery",
            "Extensive logging and monitoring"
        ],
        
        "integration_guidelines": [
            "Maintain backward compatibility with upstream components",
            "Follow established communication patterns",
            "Update integration tests for new features",
            "Document configuration changes",
            "Ensure privacy and security standards"
        ]
    })
    
    # Performance and Monitoring
    performance: Dict[str, Any] = field(default_factory=lambda: {
        "benchmarks": {
            "initialization_time": "< 3 seconds for full foundation",
            "voice_response_time": "< 500ms for voice interactions", 
            "crisis_detection_time": "< 100ms for crisis assessment",
            "memory_usage": "< 512MB for unified operation"
        },
        
        "monitoring": {
            "component_health": "Individual component health checks",
            "performance_metrics": "Response times, success rates, error counts",
            "user_interaction_tracking": "Interaction patterns and effectiveness",
            "system_optimization": "Continuous performance optimization"
        }
    })
    
    # Security and Privacy
    security: Dict[str, Any] = field(default_factory=lambda: {
        "privacy_features": [
            "Local processing for sensitive data",
            "Encrypted storage for user information",
            "Minimal data collection principles",
            "User-controlled data sharing",
            "Transparent data usage policies"
        ],
        
        "security_measures": [
            "Component-based access control",
            "Input validation and sanitization", 
            "Secure inter-component communication",
            "Audit logging for all operations",
            "Regular security assessments"
        ]
    })

# Repository Metadata Instance
REPOSITORY_INFO = RepositoryTopography()

def get_repository_structure() -> Dict[str, Any]:
    """Get the complete repository structure"""
    return REPOSITORY_INFO.directory_structure

def get_component_info(component_name: str) -> Optional[ComponentInfo]:
    """Get information about a specific component"""
    return REPOSITORY_INFO.components.get(component_name)

def get_all_components() -> Dict[str, ComponentInfo]:
    """Get information about all components"""
    return REPOSITORY_INFO.components

def get_synchronization_config() -> Dict[str, Any]:
    """Get synchronization configuration"""
    return REPOSITORY_INFO.synchronization

def get_data_flow_patterns() -> Dict[str, Any]:
    """Get data flow and integration patterns"""
    return REPOSITORY_INFO.data_flow

def update_last_sync(component_name: str, sync_timestamp: str):
    """Update the last sync timestamp for a component"""
    if component_name in REPOSITORY_INFO.components:
        REPOSITORY_INFO.components[component_name].last_sync = sync_timestamp

def generate_repository_summary() -> str:
    """Generate a comprehensive repository summary"""
    summary = f"""
# {REPOSITORY_INFO.project_title}

**Repository:** {REPOSITORY_INFO.repository_name}
**Owner:** {REPOSITORY_INFO.owner}
**Organization:** {REPOSITORY_INFO.organization}

## Description
{REPOSITORY_INFO.project_description.strip()}

## Components ({len(REPOSITORY_INFO.components)})
"""
    
    for name, component in REPOSITORY_INFO.components.items():
        summary += f"""
### {component.name}
- **Source:** {component.source_repository}
- **Local Path:** {component.local_path}
- **Description:** {component.description}
- **Capabilities:** {len(component.capabilities)} features
- **Last Sync:** {component.last_sync or 'Never'}
"""
    
    summary += f"""
## Architecture
- **Pattern:** {REPOSITORY_INFO.architecture_pattern}
- **Language:** {REPOSITORY_INFO.primary_language} {REPOSITORY_INFO.python_version}
- **Framework:** {REPOSITORY_INFO.framework}

## Synchronization
- **Strategy:** {REPOSITORY_INFO.synchronization['strategy']}
- **Automation:** {REPOSITORY_INFO.synchronization['automation']}

## Key Features
- Privacy-first design with local processing
- Real-time crisis intervention (< 100ms response)
- Natural voice interaction with stress detection
- Intelligent optimization through user learning
- Unified component coordination via Supervisor AI

Generated: {datetime.now().isoformat()}
"""
    
    return summary

def get_notion_integration_info() -> Dict[str, str]:
    """Get Notion integration information"""
    return {
        "project_url": REPOSITORY_INFO.notion_project_url,
        "workspace": REPOSITORY_INFO.notion_workspace,
        "change_logging": "All repository changes must be logged in Notion",
        "project_tracking": "Dedicated Notion project for development tracking"
    }

# Export key information for easy access
__all__ = [
    'REPOSITORY_INFO',
    'get_repository_structure', 
    'get_component_info',
    'get_all_components',
    'get_synchronization_config',
    'get_data_flow_patterns',
    'update_last_sync',
    'generate_repository_summary',
    'get_notion_integration_info'
]

if __name__ == "__main__":
    # Generate and print repository summary when run directly
    print(generate_repository_summary())
