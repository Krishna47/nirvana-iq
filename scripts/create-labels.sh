#!/bin/bash

# Nirvana IQ - Create Labels Script
# This script creates all labels needed for the project

REPO="Krishna47/AI-experiments-kinetic"

echo "🏷️  Creating labels for Nirvana IQ project..."

# Create labels with colors
gh label create "epic" --color "9b59b6" --description "Epic work item" -R "$REPO" 2>/dev/null || echo "✓ epic label already exists"
gh label create "foundation" --color "3498db" --description "Foundation/Setup work" -R "$REPO" 2>/dev/null || echo "✓ foundation label already exists"
gh label create "python" --color "3572A5" --description "Python related" -R "$REPO" 2>/dev/null || echo "✓ python label already exists"
gh label create "architecture" --color "fbca04" --description "Architecture/Design" -R "$REPO" 2>/dev/null || echo "✓ architecture label already exists"
gh label create "config" --color "cccccc" --description "Configuration" -R "$REPO" 2>/dev/null || echo "✓ config label already exists"
gh label create "frontend" --color "1f77b4" --description "Frontend/UI work" -R "$REPO" 2>/dev/null || echo "✓ frontend label already exists"
gh label create "database" --color "108548" --description "Database work" -R "$REPO" 2>/dev/null || echo "✓ database label already exists"
gh label create "agent" --color "ff6b6b" --description "AI Agent related" -R "$REPO" 2>/dev/null || echo "✓ agent label already exists"
gh label create "sql" --color "d4a574" --description "SQL related" -R "$REPO" 2>/dev/null || echo "✓ sql label already exists"
gh label create "rag" --color "fd7e14" --description "RAG/Document retrieval" -R "$REPO" 2>/dev/null || echo "✓ rag label already exists"
gh label create "langgraph" --color "a29bfe" --description "LangGraph orchestration" -R "$REPO" 2>/dev/null || echo "✓ langgraph label already exists"
gh label create "analytics" --color "00b894" --description "Analytics/Charts" -R "$REPO" 2>/dev/null || echo "✓ analytics label already exists"
gh label create "reports" --color "0984e3" --description "Report generation" -R "$REPO" 2>/dev/null || echo "✓ reports label already exists"
gh label create "devops" --color "fab005" --description "DevOps/Infrastructure" -R "$REPO" 2>/dev/null || echo "✓ devops label already exists"
gh label create "azure" --color "0078d4" --description "Azure cloud" -R "$REPO" 2>/dev/null || echo "✓ azure label already exists"
gh label create "docs" --color "8e44ad" --description "Documentation" -R "$REPO" 2>/dev/null || echo "✓ docs label already exists"
gh label create "demo" --color "e74c3c" --description "Demo/Presentation" -R "$REPO" 2>/dev/null || echo "✓ demo label already exists"

echo ""
echo "✅ All labels created successfully!"
