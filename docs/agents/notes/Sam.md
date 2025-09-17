Date: 2025-09-16
Agent: Sam
Topic: Auto web build
Summary: Launcher now ensures React dist exists; VS Code task wires prebuild.
Decisions:
- Force rebuild via HEXIOS_REBUILD=1 on debug config
Actions:
- Added preLaunchTask and build helper in launcher
Handoffs:
- To Uma to validate UI loads in desktop mode
