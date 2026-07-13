#!/bin/bash

# Nirvana IQ - Complete Issue Creation Script
# This script creates all 20 issues for the Nirvana IQ project and adds them to the project board

set -e

REPO="Krishna47/AI-experiments-kinetic"
PROJECT_ID="1"

echo "🚀 Starting Nirvana IQ Issue Creation..."

# Create Milestones
echo "📅 Creating milestones..."
gh milestone create "Sprint 1" -R "$REPO" 2>/dev/null || echo "Sprint 1 already exists"
gh milestone create "Sprint 2" -R "$REPO" 2>/dev/null || echo "Sprint 2 already exists"
gh milestone create "Sprint 3" -R "$REPO" 2>/dev/null || echo "Sprint 3 already exists"

echo ""
echo "📝 Creating issues..."

# EPIC-001: Project Foundation & MVP
echo "Creating EPIC-001..."
EPIC001=$(gh issue create --title "EPIC-001: Project Foundation & MVP" \
  --body "Epic for establishing repository, project structure, and MVP foundation.

## Acceptance Criteria
- Repository, project structure, and MVP foundation complete." \
  --label "epic" -R "$REPO" --json number -q '.number')

# NIQ-001: Initialize GitHub Repository
echo "Creating NIQ-001..."
NIQ001=$(gh issue create --title "NIQ-001: Initialize GitHub Repository" \
  --body "Set up the GitHub repository with essential configuration files and documentation.

## Acceptance Criteria
- Repository created with README, MIT license, Python .gitignore." \
  --label "foundation" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-002: Create Python Virtual Environment
echo "Creating NIQ-002..."
NIQ002=$(gh issue create --title "NIQ-002: Create Python Virtual Environment" \
  --body "Set up a Python virtual environment for the project.

## Acceptance Criteria
- Virtual environment created and activated." \
  --label "foundation" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-003: Install Core Dependencies
echo "Creating NIQ-003..."
NIQ003=$(gh issue create --title "NIQ-003: Install Core Dependencies" \
  --body "Install and configure all core Python dependencies for the project.

## Acceptance Criteria
- requirements.txt created and packages installed." \
  --label "python" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-004: Create Standard Folder Structure
echo "Creating NIQ-004..."
NIQ004=$(gh issue create --title "NIQ-004: Create Standard Folder Structure" \
  --body "Establish a well-organized folder structure following best practices.

## Acceptance Criteria
- Folders follow agreed project layout." \
  --label "architecture" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-005: Configure Environment Variables
echo "Creating NIQ-005..."
NIQ005=$(gh issue create --title "NIQ-005: Configure Environment Variables" \
  --body "Set up environment variable configuration for secure credential management.

## Acceptance Criteria
- OpenAI key loaded from .env." \
  --label "config" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-006: Build Streamlit Landing Page
echo "Creating NIQ-006..."
NIQ006=$(gh issue create --title "NIQ-006: Build Streamlit Landing Page" \
  --body "Create a landing page using Streamlit for the MVP.

## Acceptance Criteria
- Landing page launches successfully." \
  --label "frontend" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# EPIC-002: Retail Data Platform
echo "Creating EPIC-002..."
EPIC002=$(gh issue create --title "EPIC-002: Retail Data Platform" \
  --body "Epic for building retail database and preparing sample data.

## Acceptance Criteria
- Retail database and sample data ready." \
  --label "epic" -R "$REPO" --json number -q '.number')

# NIQ-007: Design Retail Database Schema
echo "Creating NIQ-007..."
NIQ007=$(gh issue create --title "NIQ-007: Design Retail Database Schema" \
  --body "Design and finalize the entity-relationship model for the retail database.

## Acceptance Criteria
- ER model finalized." \
  --label "database" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-008: Create Products Table
echo "Creating NIQ-008..."
NIQ008=$(gh issue create --title "NIQ-008: Create Products Table" \
  --body "Create the Products table in the retail database.

## Acceptance Criteria
- Products table created." \
  --label "database" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-009: Create Customers Table
echo "Creating NIQ-009..."
NIQ009=$(gh issue create --title "NIQ-009: Create Customers Table" \
  --body "Create the Customers table in the retail database.

## Acceptance Criteria
- Customers table created." \
  --label "database" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-010: Create Orders Table
echo "Creating NIQ-010..."
NIQ010=$(gh issue create --title "NIQ-010: Create Orders Table" \
  --body "Create the Orders and OrderItems tables in the retail database.

## Acceptance Criteria
- Orders and OrderItems tables created." \
  --label "database" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# NIQ-011: Seed Sample Retail Data
echo "Creating NIQ-011..."
NIQ011=$(gh issue create --title "NIQ-011: Seed Sample Retail Data" \
  --body "Populate the retail database with realistic sample data.

## Acceptance Criteria
- At least 1000 realistic rows inserted." \
  --label "database" --milestone "Sprint 1" -R "$REPO" --json number -q '.number')

# EPIC-003: Enterprise AI Core
echo "Creating EPIC-003..."
EPIC003=$(gh issue create --title "EPIC-003: Enterprise AI Core" \
  --body "Epic for implementing core AI services and agent systems.

## Acceptance Criteria
- Core AI services implemented." \
  --label "epic" -R "$REPO" --json number -q '.number')

# NIQ-012: Implement SQL Agent
echo "Creating NIQ-012..."
NIQ012=$(gh issue create --title "NIQ-012: Implement SQL Agent" \
  --body "Build an AI agent that converts natural language queries to SQL and executes them safely.

## Acceptance Criteria
- Natural language converted to SQL and executed safely." \
  --label "agent,sql" --milestone "Sprint 2" -R "$REPO" --json number -q '.number')

# NIQ-013: Implement RAG Agent
echo "Creating NIQ-013..."
NIQ013=$(gh issue create --title "NIQ-013: Implement RAG Agent" \
  --body "Build a Retrieval-Augmented Generation agent that answers questions from company documents with citations.

## Acceptance Criteria
- Answers generated from company documents with citations." \
  --label "agent,rag" --milestone "Sprint 2" -R "$REPO" --json number -q '.number')

# NIQ-014: Implement Supervisor Agent
echo "Creating NIQ-014..."
NIQ014=$(gh issue create --title "NIQ-014: Implement Supervisor Agent" \
  --body "Build a supervisor agent that routes requests to the appropriate agent (SQL, RAG, etc.) using LangGraph.

## Acceptance Criteria
- Supervisor routes requests to correct agent." \
  --label "agent,langgraph" --milestone "Sprint 2" -R "$REPO" --json number -q '.number')

# NIQ-015: Generate Business Charts
echo "Creating NIQ-015..."
NIQ015=$(gh issue create --title "NIQ-015: Generate Business Charts" \
  --body "Create functionality to generate business analytics charts from SQL query results.

## Acceptance Criteria
- Charts generated from SQL results." \
  --label "analytics" --milestone "Sprint 2" -R "$REPO" --json number -q '.number')

# NIQ-016: Generate Executive PDF Report
echo "Creating NIQ-016..."
NIQ016=$(gh issue create --title "NIQ-016: Generate Executive PDF Report" \
  --body "Implement PDF report generation for executive management summaries.

## Acceptance Criteria
- Downloadable management report generated." \
  --label "reports" --milestone "Sprint 2" -R "$REPO" --json number -q '.number')

# EPIC-004: Production Readiness
echo "Creating EPIC-004..."
EPIC004=$(gh issue create --title "EPIC-004: Production Readiness" \
  --body "Epic for deployment, documentation, and production-ready operations.

## Acceptance Criteria
- Deployment and documentation complete." \
  --label "epic" -R "$REPO" --json number -q '.number')

# NIQ-017: Dockerize Application
echo "Creating NIQ-017..."
NIQ017=$(gh issue create --title "NIQ-017: Dockerize Application" \
  --body "Create Docker configuration for containerized application deployment.

## Acceptance Criteria
- Application runs via Docker." \
  --label "devops" --milestone "Sprint 3" -R "$REPO" --json number -q '.number')

# NIQ-018: Deploy to Azure
echo "Creating NIQ-018..."
NIQ018=$(gh issue create --title "NIQ-018: Deploy to Azure" \
  --body "Deploy the application to Microsoft Azure cloud platform.

## Acceptance Criteria
- Application deployed successfully." \
  --label "azure" --milestone "Sprint 3" -R "$REPO" --json number -q '.number')

# NIQ-019: Write Project Documentation
echo "Creating NIQ-019..."
NIQ019=$(gh issue create --title "NIQ-019: Write Project Documentation" \
  --body "Create comprehensive project documentation including README and architecture guides.

## Acceptance Criteria
- README and architecture docs completed." \
  --label "docs" --milestone "Sprint 3" -R "$REPO" --json number -q '.number')

# NIQ-020: Record Demo Video
echo "Creating NIQ-020..."
NIQ020=$(gh issue create --title "NIQ-020: Record Demo Video" \
  --body "Record a professional demonstration video showcasing the application's features and capabilities.

## Acceptance Criteria
- 5-10 minute demo available." \
  --label "demo" --milestone "Sprint 3" -R "$REPO" --json number -q '.number')

echo ""
echo "✅ All 20 issues created successfully!"
echo ""
echo "Issue Numbers:"
echo "  EPIC-001: #$EPIC001"
echo "  NIQ-001: #$NIQ001"
echo "  NIQ-002: #$NIQ002"
echo "  NIQ-003: #$NIQ003"
echo "  NIQ-004: #$NIQ004"
echo "  NIQ-005: #$NIQ005"
echo "  NIQ-006: #$NIQ006"
echo "  EPIC-002: #$EPIC002"
echo "  NIQ-007: #$NIQ007"
echo "  NIQ-008: #$NIQ008"
echo "  NIQ-009: #$NIQ009"
echo "  NIQ-010: #$NIQ010"
echo "  NIQ-011: #$NIQ011"
echo "  EPIC-003: #$EPIC003"
echo "  NIQ-012: #$NIQ012"
echo "  NIQ-013: #$NIQ013"
echo "  NIQ-014: #$NIQ014"
echo "  NIQ-015: #$NIQ015"
echo "  NIQ-016: #$NIQ016"
echo "  EPIC-004: #$EPIC004"
echo "  NIQ-017: #$NIQ017"
echo "  NIQ-018: #$NIQ018"
echo "  NIQ-019: #$NIQ019"
echo "  NIQ-020: #$NIQ020"

echo ""
echo "📌 Now adding issues to Nirvana IQ project..."

# Add all issues to project
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $EPIC001 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ001 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ002 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ003 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ004 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ005 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ006 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $EPIC002 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ007 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ008 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ009 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ010 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ011 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $EPIC003 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ012 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ013 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ014 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ015 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ016 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $EPIC004 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ017 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ018 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ019 2>/dev/null || true
gh project item-add "$PROJECT_ID" --owner Krishna47 --id $NIQ020 2>/dev/null || true

echo "✅ Issues added to Nirvana IQ project!"
echo ""
echo "🎉 Setup complete! Visit your project board at:"
echo "   https://github.com/users/Krishna47/projects/1/views/1"
