#!/bin/bash
# Script to test GitHub Actions workflows locally using act

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo -e "${RED}Error: 'act' is not installed${NC}"
    echo "Install it with: brew install act"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Default values
WORKFLOW="claude-code.yml"
EVENT="push"
PYTHON_VERSION="3.12"
NODE_VERSION="20"
DRY_RUN=false
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--workflow)
            WORKFLOW="$2"
            shift 2
            ;;
        -p|--python)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        -n|--node)
            NODE_VERSION="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -w, --workflow    Workflow file name (default: claude-code-integration.yml)"
            echo "  -p, --python      Python version (default: 3.12)"
            echo "  -n, --node        Node.js version (default: 20)"
            echo "  -d, --dry-run     Dry run mode (don't actually execute)"
            echo "  -v, --verbose     Verbose output"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run with defaults"
            echo "  $0 -p 3.10 -n 18                     # Test with Python 3.10 and Node 18"
            echo "  $0 -w pytest.yml                     # Run pytest workflow"
            echo "  $0 -d                                 # Dry run"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Build act command
ACT_CMD="act $EVENT -W .github/workflows/$WORKFLOW"

# Add matrix values for claude-code-integration workflow
if [[ "$WORKFLOW" == "claude-code-integration.yml" ]]; then
    ACT_CMD="$ACT_CMD --matrix python-version:$PYTHON_VERSION --matrix node-version:$NODE_VERSION"
    echo -e "${BLUE}Testing with Python $PYTHON_VERSION and Node.js $NODE_VERSION${NC}"
elif [[ "$WORKFLOW" == "pytest.yml" ]]; then
    ACT_CMD="$ACT_CMD --matrix python-version:$PYTHON_VERSION"
    echo -e "${BLUE}Testing with Python $PYTHON_VERSION${NC}"
fi

# Add optional flags
if [ "$DRY_RUN" = true ]; then
    ACT_CMD="$ACT_CMD -n"
    echo -e "${YELLOW}Running in dry-run mode${NC}"
fi

if [ "$VERBOSE" = true ]; then
    ACT_CMD="$ACT_CMD -v"
fi

# Display command
echo -e "${GREEN}Running:${NC} $ACT_CMD"
echo ""

# Execute
eval $ACT_CMD

# Success message
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Workflow completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Workflow failed${NC}"
    exit 1
fi
