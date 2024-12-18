#!/bin/bash

# Function to create an issue
create_issue() {
    local title="$1"
    local body="$2"
    local priority="$3"
    local effort="$4"
    local status="$5"
    local category="$6"

    # Convert priority to label
    local priority_label="priority/${priority,,}"
    local effort_label="effort/${effort,,}"

    # Create the issue with labels
    gh issue create \
        --title "$title" \
        --body "$body" \
        --label "$priority_label" \
        --label "$effort_label" \
        --label "$category"
}

# Core System Issues
create_issue \
    "Implement basic agent lifecycle management" \
    "## Description
- Agent creation and destruction
- State management
- Resource allocation

## Status
Current status: In Progress

## Tasks
- [ ] Implement agent creation mechanism
- [ ] Implement agent destruction cleanup
- [ ] Develop state management system
- [ ] Create resource allocation manager" \
    "p0" "l" "In Progress" "core-system"

create_issue \
    "Develop core communication protocol" \
    "## Description
- Message routing
- Error handling
- State synchronization

## Status
Current status: Planning

## Tasks
- [ ] Design message routing system
- [ ] Implement error handling mechanisms
- [ ] Develop state synchronization protocol" \
    "p0" "l" "Planning" "core-system"

create_issue \
    "Create basic swarm coordination" \
    "## Description
- Task distribution
- Resource sharing
- Collective decision making

## Status
Current status: Not Started

## Tasks
- [ ] Design task distribution system
- [ ] Implement resource sharing mechanism
- [ ] Develop collective decision making algorithms" \
    "p0" "xl" "Not Started" "core-system"

# Security Issues
create_issue \
    "Implement authentication system" \
    "## Description
- User authentication
- Agent authentication
- Token management

## Status
Current status: Not Started

## Tasks
- [ ] Design authentication flow
- [ ] Implement user authentication
- [ ] Implement agent authentication
- [ ] Develop token management system" \
    "p0" "m" "Not Started" "security"

create_issue \
    "Develop authorization framework" \
    "## Description
- Role-based access control
- Permission management
- Policy enforcement

## Status
Current status: Not Started

## Tasks
- [ ] Design RBAC system
- [ ] Implement permission management
- [ ] Develop policy enforcement mechanism" \
    "p0" "l" "Not Started" "security"

# Development Tools Issues
create_issue \
    "Create agent development SDK" \
    "## Description
- API documentation
- Code examples
- Development guides

## Status
Current status: Planning

## Tasks
- [ ] Create API documentation
- [ ] Develop code examples
- [ ] Write development guides" \
    "p1" "m" "Planning" "development-tools"

create_issue \
    "Build debugging tools" \
    "## Description
- Log analysis
- State inspection
- Performance profiling

## Status
Current status: Not Started

## Tasks
- [ ] Implement log analysis system
- [ ] Create state inspection tools
- [ ] Develop performance profiling utilities" \
    "p1" "m" "Not Started" "development-tools"

# Integration Issues
create_issue \
    "Implement REST API" \
    "## Description
- Endpoint definitions
- Request/response handling
- Error handling

## Status
Current status: Not Started

## Tasks
- [ ] Define API endpoints
- [ ] Implement request/response handlers
- [ ] Create error handling system" \
    "p1" "m" "Not Started" "integration"

create_issue \
    "Create webhook system" \
    "## Description
- Event definitions
- Delivery management
- Retry logic

## Status
Current status: Not Started

## Tasks
- [ ] Define webhook events
- [ ] Implement delivery management
- [ ] Create retry mechanism" \
    "p1" "s" "Not Started" "integration"

# Analytics Issues
create_issue \
    "Develop basic metrics system" \
    "## Description
- Data collection
- Storage
- Basic visualization

## Status
Current status: Not Started

## Tasks
- [ ] Design metrics collection system
- [ ] Implement data storage
- [ ] Create basic visualization tools" \
    "p2" "m" "Not Started" "analytics"

create_issue \
    "Create reporting system" \
    "## Description
- Report templates
- Data aggregation
- Export functionality

## Status
Current status: Not Started

## Tasks
- [ ] Design report templates
- [ ] Implement data aggregation
- [ ] Create export functionality" \
    "p2" "m" "Not Started" "analytics"
