# Prompt: Generate Project Updates from Linear Initiative

## Objective
Generate comprehensive project updates for all projects in development status tied to a specific Linear initiative, formatted according to the project update template and supplemented with relevant meeting notes from the codebase.

## Inputs
1. **Initiative Name**: The Linear initiative to pull projects from (e.g., "Intelligence Q4 2025 - Accuracy Explainability")
2. **Date**: The date for these updates (defaults to today)
3. **Template Path**: `/Users/conner.beckwith/workplace/granola/templates/project_update.md`

## Process Steps

### 1. Query Linear for Projects
- Find all projects with status "development" tied to the specified initiative
- For each project, retrieve:
  - Project metadata (name, description, lead, target date, URL)
  - All issues/tickets with their status, assignees, due dates, and descriptions
  - Break down by status: Released, In Progress, In Review, Todo, Backlog

### 2. Pull Relevant Meeting Notes
- Search the codebase (`/Users/conner.beckwith/workplace/granola/daily_outputs/`) for meeting notes that mention:
  - The project name
  - Related keywords (e.g., for "Dimension-Level Accuracy": dimension, accuracy, schema)
  - Key team members working on the project
- Prioritize recent meetings (last 2-4 weeks)
- Focus on: sprint planning, standups, project-specific syncs, WBR/QBR meetings

### 3. Calculate Accurate Completion Percentage
**CRITICAL**: Do NOT estimate completion percentage. Calculate it based on Linear ticket status:
- Count tickets by status: Released, In Progress, In Review, Todo, Backlog
- Formula: `(Released tickets / Total substantive tickets) * 100`
- Exclude test tickets or obviously non-substantive tickets from denominator
- Be conservative - if only 3 of 11 tickets are complete, that's ~27%, not 75%
- Consider work significance: core implementation vs. documentation/cleanup

### 4. Generate Project Updates Using Template

For each project, create a file named: `{project_name_snake_case}_update_{YYYY-MM-DD}.md`

Use this structure from the template:

```markdown
# Project Update: {Project Name}

**Date:** {Date}
**Project Lead:** {Lead Name}
**Target Completion:** {Target Date}

## Overview
- **Status:** 🟢 On Track / 🟡 At Risk / 🔴 Blocked
- **Overall Progress:** {X}% complete - {Brief description of current state}

## What Was Done (Completed This Period)
- List all Released tickets and key accomplishments
- Include ticket IDs and release dates
- Highlight major milestones reached

## What Needs to Be Done (Next Steps)
- List In Progress, In Review, and high-priority Todo tickets
- Include ticket IDs and target dates
- Prioritize by importance/urgency

## Blockers / Surprises / Impact on Delivery
- **Blockers:** {What's stopping progress}
- **Surprises:** {Unexpected discoveries or changes}
- **Timeline Impact:** None / Minor / Significant - {explain if not None}

## Key Metrics
- Relevant metrics from the project
- **Linear Completion:** {Released} of {Total} tickets complete ({%})
  - **Released:** {count} tickets ({list ticket IDs})
  - **In Progress/Review:** {count} tickets ({list ticket IDs})
  - **Todo:** {count} tickets ({list ticket IDs})
  - **Backlog:** {count} tickets ({list ticket IDs if relevant})

## Help Needed (optional)
- Decisions needed from stakeholders
- Resources or support required

## Learnings / Notes (optional)
- Insights from meeting notes
- Process improvements identified
- Strategic context from discussions
```

### 5. Validation & Accuracy Checks

For each project update, verify:

1. **Completion % matches Linear ticket count**
   - Count Released tickets vs Total tickets
   - If estimate doesn't match calculation, use the calculated value

2. **Meeting notes are incorporated**
   - Check that strategic context from meetings is included in Learnings/Notes
   - Verify blockers/surprises from meetings are captured
   - Confirm next steps align with sprint planning discussions

3. **Linear ticket IDs are referenced**
   - All completed work should reference ticket IDs (e.g., INTL-108, QUA-143)
   - In Progress and Todo items should include ticket IDs and due dates

4. **Status is realistic**
   - 🟢 On Track: No blockers, timeline achievable
   - 🟡 At Risk: Some concerns, may need adjustment
   - 🔴 Blocked: Significant blockers preventing progress

### 6. Generate Summary README

Create a `README.md` in the output directory with:
- Initiative name and date
- Summary table of all projects with status and completion %
- Overall initiative health assessment
- Links to individual project updates
- Data sources used (Linear query date, meeting notes referenced)

## Output Location
`/Users/conner.beckwith/workplace/granola/project_updates/`

Files:
- `{project_name}_update_{YYYY-MM-DD}.md` (one per project)
- `README.md` (summary of all projects)

## Example Usage

**Input:**
```
Initiative: "Intelligence Q4 2025 - Accuracy Explainability"
Date: 2025-10-31
```

**Expected Output:**
- `dimension_level_accuracy_update_2025-10-31.md`
- `bug_tickets_to_accuracy_measurement_update_2025-10-31.md`
- `qa_data_ingestion_update_2025-10-31.md`
- `population_estimation_update_2025-10-31.md`
- `README.md`

## Key Guidelines

### DO:
- ✅ Calculate completion % from Linear tickets (don't estimate)
- ✅ Reference specific ticket IDs (INTL-109, QUA-160, etc.)
- ✅ Include insights from meeting notes in Learnings section
- ✅ Be accurate about completion status (35% is better than inflating to 75%)
- ✅ Include both completed work AND remaining work with ticket IDs
- ✅ Add date to all output filenames
- ✅ Cross-reference meeting notes for strategic context, blockers, next steps

### DON'T:
- ❌ Estimate completion percentage subjectively
- ❌ Say "75% complete" when only 3 of 11 tickets are done
- ❌ Ignore Linear ticket status in favor of qualitative assessment
- ❌ Leave out ticket IDs from accomplishments and next steps
- ❌ Skip validation of completion % against Linear data
- ❌ Forget to incorporate meeting note insights into the update

## Quality Checklist

Before finalizing each project update, verify:

- [ ] Completion percentage = (Released tickets / Total tickets) * 100
- [ ] All Released tickets are listed in "What Was Done"
- [ ] All In Progress/Todo tickets are listed in "What Needs to Be Done"
- [ ] Ticket IDs are included for all work items
- [ ] Meeting notes insights are in Learnings/Notes section
- [ ] Status emoji matches actual project health
- [ ] Timeline impact is accurately assessed
- [ ] Help Needed section includes actionable items
- [ ] Output filename includes date (YYYY-MM-DD format)

## Tools Required
- Linear MCP server (for querying projects and issues)
- File system access (for reading meeting notes and template)
- Glob/Grep (for searching meeting notes)
- File writing capabilities

## Success Criteria
- Accurate completion percentages based on Linear ticket data
- Comprehensive coverage of work done and remaining
- Strategic insights from meeting notes incorporated
- All output files follow naming convention with dates
- README provides clear summary and navigation
