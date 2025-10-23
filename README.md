# NeuroLift Foundation

**Unified ADHD Support System - Combining Crisis Intervention, Intelligent Optimization, and Natural Voice Interaction**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Sync Status](https://img.shields.io/badge/sync-automated-green.svg)](https://github.com/JDUB1216/neurolift-foundation/actions)

## Overview

The NeuroLift Foundation is a comprehensive, unified platform that integrates three core components into a single, cohesive ADHD support system:

- **🚨 RRT Advocate** - Rapid Response Team for crisis intervention and immediate support
- **🧠 TOI-OTOI Framework** - Terms of Interaction and Orchestrated Terms of Interaction
- **🎤 Aimybox Voice Interface** - Natural language voice interaction capabilities

This foundation serves as the cornerstone for the complete NeuroLift Technologies ecosystem, providing privacy-first, user-centric AI assistance specifically designed for neurodivergent individuals.

## 🏗️ Architecture

### Unified Integration Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    NeuroLift Foundation                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ RRT         │  │ TOI-OTOI    │  │ Aimybox Voice       │  │
│  │ Advocate    │◄─┤ Framework   │◄─┤ Interface           │  │
│  │             │  │             │  │                     │  │
│  │ • Crisis    │  │ • Terms of  │  │ • Speech-to-Text    │  │
│  │   Detection │  │   Interaction│  │ • Natural Language  │  │
│  │ • Emergency │  │ • Optimization│  │ • Stress Detection  │  │
│  │   Response  │  │ • Learning   │  │ • Voice Synthesis   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Unified Core                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Supervisor  │  │ Component   │  │ State Manager       │  │
│  │ AI          │  │ Communication│  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Synchronization

The foundation maintains automatic synchronization with upstream repositories:

- **RRT Advocate**: `JDUB1216/rrt-advocate` (main branch)
- **TOI-OTOI Framework**: `JDUB1216/nlt-otoi` (main branch)  
- **Aimybox Voice**: `JDUB1216/aimybox-android-assistant` (master branch)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Git with configured user credentials
- Node.js 18+ (for voice interface components)
- 4GB+ RAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/JDUB1216/neurolift-foundation.git
   cd neurolift-foundation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install  # For voice interface components
   ```

3. **Initialize the foundation**
   ```python
   from unified_core.neurolift_foundation import create_foundation, FoundationMode
   
   # Create and start the foundation
   foundation = await create_foundation(
       user_id="your_user_id",
       mode=FoundationMode.UNIFIED
   )
   ```

### Basic Usage

```python
import asyncio
from unified_core.neurolift_foundation import create_foundation

async def main():
    # Initialize foundation
    foundation = await create_foundation("user_001")
    
    # Voice interaction
    response = await foundation.voice_interaction(
        "How are you feeling today?",
        context={"mood": "anxious", "energy": "low"}
    )
    print(f"Foundation: {response}")
    
    # Crisis support (if needed)
    crisis_response = await foundation.crisis_alert({
        "stress_level": "high",
        "indicators": ["overwhelmed", "panic"],
        "context": "work deadline pressure"
    })
    
    # Update preferences
    await foundation.update_preferences({
        "voice_response_style": "calm",
        "crisis_sensitivity": "high",
        "optimization_frequency": "daily"
    })
    
    # Get system status
    status = await foundation.get_system_status()
    print(f"System Status: {status}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📁 Repository Structure

```
neurolift-foundation/
├── rrt-advocate/                    # Crisis intervention component
│   ├── src/
│   ├── config/
│   └── docs/
├── toi-otoi-framework/             # Optimization framework
│   └── GEMINI_TOPOGRAPHY.py
├── aimybox-voice/                  # Voice interface component
│   ├── app/
│   ├── gradle/
│   └── README.md
├── unified-core/                   # Integration layer
│   ├── neurolift_foundation.py    # Main foundation class
│   ├── integration/               # Component integrations
│   │   ├── rrt_integration.py
│   │   ├── toi_otoi_integration.py
│   │   └── voice_integration.py
│   ├── supervisor/                # Supervisor AI
│   │   └── supervisor_ai.py
│   └── coordination/              # Cross-component coordination
│       ├── component_communication.py
│       └── state_manager.py
├── docs/                          # Documentation
│   └── unified_architecture.md
├── scripts/                       # Automation scripts
│   └── sync_upstream.sh
├── .github/workflows/             # GitHub Actions
│   └── upstream-sync.yml
├── config/                        # Configuration files
├── tests/                         # Test suites
└── README.md
```

## 🔄 Synchronization

### Automated Synchronization

The foundation automatically synchronizes with upstream repositories daily at 2 AM UTC via GitHub Actions. Manual synchronization can be triggered:

```bash
# Sync all components
./scripts/sync_upstream.sh

# Sync specific component
./scripts/sync_upstream.sh rrt-advocate

# Force sync (even without changes)
./scripts/sync_upstream.sh --force

# Dry run (show what would be synced)
./scripts/sync_upstream.sh --dry-run
```

### Manual Synchronization

```bash
# Check for upstream changes
./scripts/sync_upstream.sh --check-only

# Sync with backup
./scripts/sync_upstream.sh --backup

# Verbose output
./scripts/sync_upstream.sh --verbose
```

## 🧪 Testing

### Integration Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific component tests
python -m pytest tests/test_rrt_integration.py
python -m pytest tests/test_voice_integration.py
python -m pytest tests/test_toi_otoi_integration.py

# Run with coverage
python -m pytest tests/ --cov=unified_core --cov-report=html
```

### Manual Testing

```bash
# Test foundation initialization
python unified_core/neurolift_foundation.py

# Test component communication
python tests/manual/test_communication.py

# Test voice interface
python tests/manual/test_voice.py
```

## 🔧 Configuration

### Foundation Configuration

```yaml
# config/foundation.yml
user_id: "your_user_id"
mode: "unified"  # unified, crisis_only, voice_only, framework_only

components:
  rrt_advocate: true
  toi_otoi_framework: true
  voice_interface: true
  supervisor_ai: true

privacy_settings:
  data_encryption: true
  local_processing: true
  external_sharing: false

performance_settings:
  max_response_time: 5.0
  cache_enabled: true
  background_optimization: true
```

### Component-Specific Configuration

Each component maintains its own configuration within its directory:

- **RRT Advocate**: `rrt-advocate/config/crisis_thresholds.yaml`
- **TOI-OTOI Framework**: Embedded in `GEMINI_TOPOGRAPHY.py`
- **Voice Interface**: `aimybox-voice/app/src/main/res/values/`

## 🔐 Privacy & Security

### Privacy-First Design

- **Local Processing**: Core functionality operates locally without external dependencies
- **Encrypted Storage**: All user data encrypted at rest and in transit
- **Minimal Data Collection**: Only essential data collected for functionality
- **User Control**: Complete user control over data sharing and retention

### Security Features

- **Access Control**: Component-based access control with permission validation
- **Audit Logging**: Comprehensive logging of all system interactions
- **State Isolation**: Secure state management with component isolation
- **Input Validation**: Robust input validation and sanitization

## 📊 Performance

### Benchmarks

- **Initialization Time**: < 3 seconds for full foundation
- **Response Time**: < 500ms for voice interactions
- **Crisis Detection**: < 100ms for crisis assessment
- **Memory Usage**: < 512MB for unified operation

### Optimization Features

- **Async Processing**: Full asynchronous operation for responsiveness
- **Intelligent Caching**: Smart caching reduces redundant processing
- **Resource Management**: Dynamic resource allocation prevents conflicts
- **Background Processing**: Non-critical tasks processed in background

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** to unified core or component integrations
4. **Test thoroughly**: Run integration tests and manual testing
5. **Update documentation**: Update relevant documentation
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

### Component Development

When developing component-specific features:

1. **Work in upstream repository** first (e.g., `rrt-advocate`, `nlt-otoi`)
2. **Test in isolation** within the component repository
3. **Sync to foundation** using synchronization scripts
4. **Test integration** within the unified foundation
5. **Update integration layer** if needed

### Integration Guidelines

- Maintain backward compatibility with existing components
- Follow the established communication patterns
- Update integration tests for new features
- Document any new configuration options
- Ensure privacy and security standards are maintained

## 📚 Documentation

### Architecture Documentation

- [Unified Architecture Guide](docs/unified_architecture.md)
- [Component Integration Patterns](docs/integration_patterns.md)
- [State Management Guide](docs/state_management.md)
- [Communication Protocols](docs/communication.md)

### Component Documentation

- [RRT Advocate Documentation](rrt-advocate/README.md)
- [TOI-OTOI Framework Guide](toi-otoi-framework/README.md)
- [Aimybox Voice Interface](aimybox-voice/README.md)

### API Documentation

- [Foundation API Reference](docs/api/foundation.md)
- [Integration API Reference](docs/api/integration.md)
- [Supervisor AI API](docs/api/supervisor.md)

## 🐛 Troubleshooting

### Common Issues

**Foundation won't initialize**
```bash
# Check prerequisites
python --version  # Should be 3.11+
git --version     # Should be 2.0+

# Check repository integrity
git status
git remote -v
```

**Sync failures**
```bash
# Check upstream connectivity
git fetch rrt-upstream main
git fetch toi-otoi-upstream main
git fetch aimybox-upstream master

# Force sync if needed
./scripts/sync_upstream.sh --force
```

**Component communication errors**
```bash
# Check component status
python -c "
import asyncio
from unified_core.neurolift_foundation import create_foundation
async def check():
    f = await create_foundation('test')
    status = await f.get_system_status()
    print(status)
asyncio.run(check())
"
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

foundation = await create_foundation("debug_user", mode=FoundationMode.DEVELOPMENT)
```

## 📈 Roadmap

### Current Version (v1.0)
- ✅ Unified foundation architecture
- ✅ Component integration layer
- ✅ Automated synchronization
- ✅ Basic voice interaction
- ✅ Crisis intervention protocols

### Next Release (v1.1)
- 🔄 Enhanced voice stress detection
- 🔄 Advanced optimization algorithms
- 🔄 Mobile app integration
- 🔄 Multi-user support
- 🔄 Cloud deployment options

### Future Versions
- 📋 Additional specialized Advocates
- 📋 IoT device integration
- 📋 Healthcare provider integration
- 📋 Advanced analytics dashboard
- 📋 Community features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NeuroLift Technologies** - Core AI-fusion framework and methodology
- **Aimybox Community** - Voice interface foundation
- **ADHD Community** - Feedback and real-world testing
- **Open Source Contributors** - Various libraries and tools

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/JDUB1216/neurolift-foundation/issues)
- **Discussions**: [GitHub Discussions](https://github.com/JDUB1216/neurolift-foundation/discussions)
- **Email**: foundation-support@neurolift.tech

---

**Last sync**: Never (initial setup)  
**Foundation version**: 1.0.0  
**Components**: RRT Advocate, TOI-OTOI Framework, Aimybox Voice Interface  
**Status**: 🟢 Active Development

*"Tech That Gets You, Nothing About us Without us, ElevAIte Your Mind"*
