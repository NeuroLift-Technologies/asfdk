#!/bin/bash

# NeuroLift Agent Solidarity Kit - Manual Upstream Synchronization Script
# Synchronizes components with their upstream repositories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$REPO_ROOT/sync.log"

# Component configurations
declare -A COMPONENTS=(
    ["rrt-advocate"]="rrt-upstream main"
    ["nlt-otoi"]="nlt-otoi-upstream main"
    ["sleepwalker"]="sleepwalker-upstream main"
)

# Functions
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

usage() {
    cat << EOF
NeuroLift Agent Solidarity Kit - Upstream Synchronization Script

Usage: $0 [OPTIONS] [COMPONENT]

OPTIONS:
    -h, --help          Show this help message
    -f, --force         Force synchronization even if no changes detected
    -d, --dry-run       Show what would be done without making changes
    -v, --verbose       Enable verbose output
    --check-only        Only check for changes, don't sync
    --backup           Create backup before syncing

COMPONENTS:
    all                 Sync all components (default)
    rrt-advocate        Sync RRT Advocate only
    nlt-otoi            Sync NLT-OTOI Framework only
    sleepwalker         Sync Sleepwalker Protocol only

EXAMPLES:
    $0                          # Sync all components
    $0 rrt-advocate            # Sync RRT Advocate only
    $0 --force all             # Force sync all components
    $0 --dry-run --verbose     # Show what would be synced
    $0 --check-only            # Check for changes only

EOF
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
        exit 1
    fi
    
    # Check if we're in the correct repository
    if [[ ! -f "$REPO_ROOT/unified-core/neurolift_foundation.py" ]]; then
        error "Not in the Agent Solidarity Kit repository root"
        exit 1
    fi
    
    # Check git configuration
    if [[ -z "$(git config user.name)" ]] || [[ -z "$(git config user.email)" ]]; then
        error "Git user.name and user.email must be configured"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

setup_remotes() {
    log "Setting up upstream remotes..."
    
    # Add upstream remotes if they don't exist
    git remote add rrt-upstream https://github.com/NeuroLift-Technologies/rrt-advocate.git 2>/dev/null || true
    git remote add nlt-otoi-upstream https://github.com/NeuroLift-Technologies/nlt-otoi.git 2>/dev/null || true
    git remote add sleepwalker-upstream https://github.com/NeuroLift-Technologies/sleepwalker.git 2>/dev/null || true
    
    success "Upstream remotes configured"
}

fetch_upstream() {
    log "Fetching upstream changes..."
    
    git fetch rrt-upstream main || warning "Failed to fetch rrt-upstream"
    git fetch nlt-otoi-upstream main || warning "Failed to fetch nlt-otoi-upstream"
    git fetch sleepwalker-upstream main || warning "Failed to fetch sleepwalker-upstream"
    
    success "Upstream fetch completed"
}

check_component_changes() {
    local component="$1"
    local remote_branch="$2"
    
    log "Checking changes for $component..."
    
    # Find last sync commit for this component
    local last_sync=$(git log --grep="Sync $component from upstream" --oneline -1 --format="%H" 2>/dev/null || echo "")
    
    if [[ -z "$last_sync" ]]; then
        echo "initial"
        return 0
    fi
    
    # Check for new commits since last sync
    local new_commits=$(git rev-list --count "$last_sync..$remote_branch" 2>/dev/null || echo "1")
    
    if [[ "$new_commits" -gt "0" ]]; then
        echo "$new_commits"
        return 0
    else
        echo "0"
        return 1
    fi
}

sync_component() {
    local component="$1"
    local remote="$2"
    local branch="$3"
    local force="$4"
    local dry_run="$5"
    
    log "Processing $component..."
    
    # Check for changes
    local changes=$(check_component_changes "$component" "$remote/$branch")
    
    if [[ "$changes" == "0" ]] && [[ "$force" != "true" ]]; then
        success "$component: No changes detected"
        return 0
    fi
    
    if [[ "$changes" == "initial" ]]; then
        log "$component: Initial sync detected"
    else
        log "$component: $changes new commits detected"
    fi
    
    if [[ "$dry_run" == "true" ]]; then
        warning "$component: Would sync (dry run mode)"
        return 0
    fi
    
    # Create backup if requested
    if [[ "$BACKUP" == "true" ]]; then
        local backup_branch="backup-$component-$(date +%Y%m%d-%H%M%S)"
        git branch "$backup_branch"
        log "Created backup branch: $backup_branch"
    fi
    
    # Perform the sync
    log "Syncing $component from $remote/$branch..."
    
    if git subtree pull --prefix="$component" "$remote" "$branch" --squash -m "Sync $component from upstream: $changes new commits"; then
        success "$component: Sync completed successfully"
        return 0
    else
        error "$component: Sync failed"
        return 1
    fi
}

run_integration_tests() {
    log "Running integration tests..."
    
    # Check if tests exist
    if [[ -d "$REPO_ROOT/tests" ]]; then
        cd "$REPO_ROOT"
        
        # Run Python tests if available
        if command -v python3 &> /dev/null && [[ -f "requirements.txt" ]]; then
            python3 -m pytest tests/ -v 2>&1 | tee -a "$LOG_FILE" || warning "Some tests failed"
        fi
        
        # Run any other test scripts
        if [[ -f "scripts/test_integration.sh" ]]; then
            bash scripts/test_integration.sh 2>&1 | tee -a "$LOG_FILE" || warning "Integration tests failed"
        fi
        
        success "Integration tests completed"
    else
        warning "No tests directory found, skipping tests"
    fi
}

update_documentation() {
    log "Updating documentation..."
    
    # Update GEMINI_TOPOGRAPHY if script exists
    if [[ -f "$REPO_ROOT/scripts/update_topography.py" ]]; then
        python3 "$REPO_ROOT/scripts/update_topography.py" --sync-update 2>&1 | tee -a "$LOG_FILE" || warning "Failed to update GEMINI_TOPOGRAPHY"
    fi
    
    # Update README with sync timestamp
    if [[ -f "$REPO_ROOT/README.md" ]]; then
        sed -i "s/Last sync: .*/Last sync: $(date)/" "$REPO_ROOT/README.md" 2>/dev/null || true
    fi
    
    success "Documentation updated"
}

create_sync_summary() {
    local synced_components=("$@")
    
    log "Creating sync summary..."
    
    local summary_file="$REPO_ROOT/SYNC_SUMMARY.md"
    
    cat > "$summary_file" << EOF
# NeuroLift Foundation - Sync Summary

**Date:** $(date)
**Script Version:** 1.0.0

## Components Synced

EOF
    
    for component in "${synced_components[@]}"; do
        echo "- ✅ $component" >> "$summary_file"
    done
    
    if [[ ${#synced_components[@]} -eq 0 ]]; then
        echo "- ⏭️ No components required syncing" >> "$summary_file"
    fi
    
    cat >> "$summary_file" << EOF

## Integration Status

- Tests: $([ -d "$REPO_ROOT/tests" ] && echo "✅ Available" || echo "⚠️ Not found")
- Documentation: ✅ Updated
- GEMINI_TOPOGRAPHY: $([ -f "$REPO_ROOT/scripts/update_topography.py" ] && echo "✅ Updated" || echo "⚠️ Script not found")

## Next Steps

1. Review changes in each synced component
2. Test the unified system functionality
3. Update any integration-specific configurations
4. Commit and push changes if satisfied

---
*Generated by NeuroLift Foundation sync script*
EOF
    
    success "Sync summary created: $summary_file"
}

commit_changes() {
    local synced_components=("$@")
    
    if [[ ${#synced_components[@]} -eq 0 ]]; then
        log "No changes to commit"
        return 0
    fi
    
    log "Committing changes..."
    
    # Add all changes
    git add .
    
    # Create commit message
    local commit_msg="Automated upstream sync: $(date)"
    local commit_body="Synced components: $(IFS=', '; echo "${synced_components[*]}")"
    
    if git commit -m "$commit_msg" -m "$commit_body"; then
        success "Changes committed successfully"
        
        # Ask if user wants to push
        if [[ "$INTERACTIVE" == "true" ]]; then
            read -p "Push changes to origin? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git push origin main
                success "Changes pushed to origin"
            fi
        fi
    else
        warning "No changes to commit"
    fi
}

main() {
    # Parse command line arguments
    COMPONENT="all"
    FORCE="false"
    DRY_RUN="false"
    VERBOSE="false"
    CHECK_ONLY="false"
    BACKUP="false"
    INTERACTIVE="true"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -f|--force)
                FORCE="true"
                shift
                ;;
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -v|--verbose)
                VERBOSE="true"
                set -x
                shift
                ;;
            --check-only)
                CHECK_ONLY="true"
                shift
                ;;
            --backup)
                BACKUP="true"
                shift
                ;;
            --non-interactive)
                INTERACTIVE="false"
                shift
                ;;
            all|rrt-advocate|nlt-otoi|sleepwalker)
                COMPONENT="$1"
                shift
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Initialize log
    echo "=== NeuroLift Agent Solidarity Kit Sync - $(date) ===" > "$LOG_FILE"
    
    log "Starting Agent Solidarity Kit upstream synchronization"
    log "Component: $COMPONENT"
    log "Force: $FORCE"
    log "Dry run: $DRY_RUN"
    log "Check only: $CHECK_ONLY"
    
    # Run prerequisite checks
    check_prerequisites
    
    # Setup and fetch
    setup_remotes
    fetch_upstream
    
    # Determine which components to process
    local components_to_process=()
    if [[ "$COMPONENT" == "all" ]]; then
        components_to_process=("rrt-advocate" "nlt-otoi" "sleepwalker")
    else
        components_to_process=("$COMPONENT")
    fi
    
    # Process each component
    local synced_components=()
    local failed_components=()
    
    for comp in "${components_to_process[@]}"; do
        if [[ -n "${COMPONENTS[$comp]}" ]]; then
            IFS=' ' read -r remote branch <<< "${COMPONENTS[$comp]}"
            
            if [[ "$CHECK_ONLY" == "true" ]]; then
                local changes=$(check_component_changes "$comp" "$remote/$branch")
                if [[ "$changes" != "0" ]]; then
                    log "$comp: $changes changes available"
                else
                    log "$comp: No changes"
                fi
            else
                if sync_component "$comp" "$remote" "$branch" "$FORCE" "$DRY_RUN"; then
                    synced_components+=("$comp")
                else
                    failed_components+=("$comp")
                fi
            fi
        else
            error "Unknown component: $comp"
            failed_components+=("$comp")
        fi
    done
    
    # Post-sync actions
    if [[ "$CHECK_ONLY" != "true" ]] && [[ "$DRY_RUN" != "true" ]] && [[ ${#synced_components[@]} -gt 0 ]]; then
        run_integration_tests
        update_documentation
        create_sync_summary "${synced_components[@]}"
        commit_changes "${synced_components[@]}"
    fi
    
    # Summary
    log "Sync completed"
    log "Synced: $(IFS=', '; echo "${synced_components[*]:-none}")"
    if [[ ${#failed_components[@]} -gt 0 ]]; then
        error "Failed: $(IFS=', '; echo "${failed_components[*]}")"
        exit 1
    fi
    
    success "All operations completed successfully"
}

# Run main function
main "$@"
