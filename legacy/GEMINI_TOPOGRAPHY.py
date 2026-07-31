"""
GEMINI_TOPOGRAPHY.py - NeuroLift Agent Solidarity Kit Repository Structure and Metadata

This file provides comprehensive information about the Agent Solidarity Kit repository
structure, component integration, and data relationships for AI system understanding.

Repository: solidarity-framework
Purpose: Unified agent development platform — ASFDK core layer (RRT Advocate, NLT-OTOI Framework,
         Sleepwalker Protocol, VibeVoice), coding-agent operations hub (agents, SOPs, governance
         workflows), and Cloudflare agent development resources (links, MCP configs, hosting)
Owner: NeuroLift Technologies
Organization: NeuroLift Technologies
Governance: ORG-DEV-OTOI-1.0.2
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ComponentInfo:
    """Information about a kit component"""
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
    repository_name: str = "solidarity-framework"
    repository_url: str = "https://github.com/NeuroLift-Technologies/solidarity-framework"
    owner: str = "NeuroLift-Technologies"
    organization: str = "NeuroLift Technologies"
    
    # Project Information
    project_title: str = "NeuroLift Agent Solidarity Kit"
    project_description: str = """
    The unified agent development platform for NeuroLift Technologies. Combines four core ASFDK
    components — RRT Advocate (crisis intervention), NLT-OTOI Framework (interaction governance),
    Sleepwalker Protocol (emotional continuity), and VibeVoice (voice AI) — as the required layer
    between the model and the agent. Also serves as the org-wide coding-agent operations hub
    (agent profiles, SOPs, governance workflows) and Cloudflare agent development reference
    (Agents SDK resources, MCP server configs, and hosting infrastructure).
    """
    
    # Governance
    governance_contract: str = "ORG-DEV-OTOI-1.0.2"
    authority: str = "Joshua W. Dorsey, Sr."
    escalation_email: str = "info@neuroliftsolutions.com"
    
    # Technical Specifications
    primary_language: str = "Python"
    python_version: str = "3.10+"
    framework: str = "AsyncIO-based unified architecture"
    architecture_pattern: str = "Solidarity Framework with Component Integration"
    
    # Component Integration
    components: Dict[str, ComponentInfo] = field(default_factory=lambda: {
        "rrt_advocate": ComponentInfo(
            name="RRT Advocate",
            source_repository="https://github.com/NeuroLift-Technologies/rrt-advocate",
            source_branch="main",
            local_path="rrt-advocate/",
            description="Rapid Response Team for crisis intervention and immediate safety",
            capabilities=[
                "Crisis detection and assessment",
                "Emergency intervention protocols", 
                "Multi-level crisis response (Green→Yellow→Orange→Red→Black)",
                "Agency preservation constraints",
                "Shame-resistant design",
                "Sub-5-second response time"
            ],
            dependencies=[
                "asyncio", "datetime", "yaml", "logging"
            ],
            integration_points=[
                "unified_core.integration.rrt_integration",
                "Sleepwalker Protocol (RRTA handoff)",
                "NLT-OTOI Framework (crisis optimization)",
                "Supervisor AI (coordination)"
            ]
        ),
        
        "nlt_otoi": ComponentInfo(
            name="NLT-OTOI Framework",
            source_repository="https://github.com/NeuroLift-Technologies/nlt-otoi",
            source_branch="main", 
            local_path="nlt-otoi/",
            description="Terms of Interaction and Orchestrated Terms of Interaction governance",
            capabilities=[
                "TOI document parsing and management",
                "OTOI multi-agent orchestration",
                "Privacy-first governance (PrivacyGuardian)",
                "User preference learning and adaptation",
                "System-wide optimization coordination",
                "Continuous improvement algorithms"
            ],
            dependencies=[
                "asyncio", "json", "datetime", "typing"
            ],
            integration_points=[
                "unified_core.integration.toi_otoi_integration",
                "Sleepwalker Protocol (emotional preferences)",
                "RRT Advocate (crisis optimization)",
                "Supervisor AI (system optimization)"
            ]
        ),
        
        "sleepwalker": ComponentInfo(
            name="Sleepwalker Protocol (SWP)",
            source_repository="https://github.com/NeuroLift-Technologies/sleepwalker",
            source_branch="main",
            local_path="sleepwalker/",
            description="Emotional continuity governance for sustained safety across sessions",
            capabilities=[
                "Emotional state detection (dissociation, numbing, avoidance, detachment)",
                "Graduated consent management",
                "Session continuity preservation",
                "RRTA crisis handoff integration",
                "TOI-based user preference loading",
                "Privacy-first local processing"
            ],
            dependencies=[
                "pyyaml", "asyncio", "typing"
            ],
            integration_points=[
                "unified_core.integration.sleepwalker_integration",
                "RRT Advocate (crisis handoff)",
                "NLT-OTOI Framework (TOI preferences)",
                "Supervisor AI (coordination)"
            ]
        )
    })
    
    # Directory Structure
    directory_structure: Dict[str, Any] = field(default_factory=lambda: {
        "root": {
            "README.md": "Agent Solidarity Kit documentation and usage guide",
            "GEMINI_TOPOGRAPHY.py": "Repository structure and metadata (this file)",
            "AGENTS.md": "Agent coordination protocol (ORG-DEV-OTOI-1.0.2)",
            "CLAUDE.md": "AI assistant guide for OTOI compliance",
            "CONTRIBUTING.md": "Contribution guidelines",
            "CODE_OF_CONDUCT.md": "Community code of conduct",
            "SECURITY.md": "Security policy",
            "SUPPORT.md": "Support information",
            "LICENSE": "Apache License 2.0",
            "requirements.txt": "Python dependencies",
            "Dockerfile": "Container build configuration"
        },
        
        "rrt-advocate/": {
            "description": "Crisis intervention component",
            "src/rrt_advocate.py": "Core crisis intervention engine",
            "config/crisis_thresholds.yaml": "Crisis detection thresholds",
            "tests/test_rrt_advocate.py": "RRT test suite",
            "docs/": "RRT documentation"
        },
        
        "nlt-otoi/": {
            "description": "Interaction governance framework",
            "src/fusion/toi_parser.py": "TOI document parser",
            "src/fusion/otoi_orchestrator.py": "OTOI multi-agent orchestrator",
            "src/fusion/privacy_guardian.py": "Privacy-first governance",
            "schemas/": "JSON schemas for TOI/OTOI",
            "templates/": "TOI and charter templates",
            "docs/": "OTOI documentation"
        },
        
        "sleepwalker/": {
            "description": "Emotional continuity protocol",
            "sleepwalker_protocol/": "Python implementation",
            "src/": "TypeScript implementation",
            "examples/": "Usage examples",
            "tests/": "SWP test suite"
        },
        
        "unified-core/": {
            "description": "Integration layer and unified coordination",
            "neurolift_foundation.py": "Main foundation class",
            "integration/": {
                "rrt_integration.py": "RRT Advocate integration",
                "toi_otoi_integration.py": "NLT-OTOI Framework integration", 
                "sleepwalker_integration.py": "Sleepwalker Protocol integration"
            },
            "supervisor/supervisor_ai.py": "Supervisor AI coordination",
            "coordination/": "Cross-component coordination"
        },
        
        "docs/": {
            "active-threads.md": "Current work state tracker",
            "agent-log/": "Agent session audit trail"
        },
        
        "SOPs/": {
            "new-agent-onboarding.md": "SOP-NLT-001",
            "repo-governance-setup.md": "SOP-NLT-002",
            "incident-response.md": "SOP-NLT-003"
        },
        
        "templates/": {
            "agent-registration.json": "Agent self-registration",
            "handoff-record.json": "Session handoff",
            "escalation.md": "Escalation notice",
            "intent-log.md": "Intent tracking"
        },
        
        ".nltotoi/": {
            "index/governance-files.md": "Governance file registry",
            "scripts/validate-governance.sh": "Compliance validation"
        }
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

def generate_repository_summary() -> str:
    """Generate a comprehensive repository summary"""
    summary = f"""
# {REPOSITORY_INFO.project_title}

**Repository:** {REPOSITORY_INFO.repository_name}
**Owner:** {REPOSITORY_INFO.owner}
**Organization:** {REPOSITORY_INFO.organization}
**Governance:** {REPOSITORY_INFO.governance_contract}
**Authority:** {REPOSITORY_INFO.authority}

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

## Solidarity Framework Principles
- Transparency — All agent actions are logged and auditable
- Minimal Footprint — Agents only modify what is necessary
- Escalation Culture — When in doubt, escalate to human authority
- Human Flourishing — Technology serves people
- Privacy First — Local-only processing wherever possible
- Agency Preservation — User autonomy is never overridden

Generated: {datetime.now().isoformat()}
"""
    
    return summary

# Export key information
__all__ = [
    'REPOSITORY_INFO',
    'get_repository_structure', 
    'get_component_info',
    'get_all_components',
    'generate_repository_summary'
]

if __name__ == "__main__":
    print(generate_repository_summary())
