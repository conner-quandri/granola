#!/usr/bin/python3
"""
Script to extract meeting notes from Granola cache file.
Usage: python extract_meeting_notes.py [--format json|markdown] [--output filename]
"""

import json
import argparse
import sys
import os
import re
from datetime import datetime
from pathlib import Path

def convert_rich_content_to_markdown(content):
    """Convert Granola's rich content format to markdown."""
    if not content or not isinstance(content, dict):
        return ""
    
    def process_node(node):
        if not isinstance(node, dict):
            return ""
        
        node_type = node.get('type', '')
        text = ""
        
        if node_type == 'text':
            return node.get('text', '')
        elif node_type == 'paragraph':
            content_items = node.get('content', [])
            paragraph_text = ''.join(process_node(item) for item in content_items)
            return paragraph_text + '\n\n' if paragraph_text else ''
        elif node_type == 'heading':
            level = node.get('attrs', {}).get('level', 1)
            heading_prefix = '#' * level
            content_items = node.get('content', [])
            heading_text = ''.join(process_node(item) for item in content_items)
            return f"{heading_prefix} {heading_text}\n\n" if heading_text else ''
        elif node_type == 'bulletList':
            content_items = node.get('content', [])
            list_text = ''.join(process_node(item) for item in content_items)
            return list_text
        elif node_type == 'orderedList':
            content_items = node.get('content', [])
            list_text = ''.join(process_node(item) for item in content_items)
            return list_text
        elif node_type == 'listItem':
            content_items = node.get('content', [])
            item_text = ''.join(process_node(item) for item in content_items).strip()
            return f"- {item_text}\n" if item_text else ''
        elif node_type == 'doc':
            content_items = node.get('content', [])
            return ''.join(process_node(item) for item in content_items)
        elif node_type == 'hardBreak':
            return '\n'
        elif node_type == 'codeBlock':
            content_items = node.get('content', [])
            code_text = ''.join(process_node(item) for item in content_items)
            return f"```\n{code_text}```\n\n"
        else:
            # For unknown types, try to process any content
            content_items = node.get('content', [])
            if content_items:
                return ''.join(process_node(item) for item in content_items)
            return ""
    
    return process_node(content).strip()

def get_meeting_panels(document_id, document_panels):
    """Get all panels for a specific meeting document."""
    panels = []
    if document_id in document_panels:
        panel_data = document_panels[document_id]
        if isinstance(panel_data, dict):
            for panel_id, panel_info in panel_data.items():
                if isinstance(panel_info, dict) and panel_info.get('content'):
                    panels.append({
                        'id': panel_id,
                        'title': panel_info.get('title', 'Untitled Section'),
                        'content': panel_info.get('content'),
                        'template_slug': panel_info.get('template_slug'),
                        'updated_at': panel_info.get('content_updated_at', panel_info.get('updated_at'))
                    })
    return panels

def sanitize_filename(filename):
    """Convert a string to a safe filename."""
    if not filename:
        return "untitled"
    
    # Convert to string if not already
    filename = str(filename)
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace('\n', ' ').replace('\r', ' ')
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename).strip()
    # Limit length
    if len(filename) > 100:
        filename = filename[:97] + "..."
    
    # Ensure we don't have an empty filename
    if not filename:
        filename = "untitled"
        
    return filename

def get_meeting_date(created_at):
    """Extract date string from meeting creation timestamp."""
    try:
        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return date_obj.strftime('%Y-%m-%d')
    except:
        return 'unknown-date'

def load_granola_cache(cache_path):
    """Load and parse the Granola cache file."""
    try:
        with open(cache_path, 'r') as f:
            data = json.load(f)
            cache_data = json.loads(data['cache'])
            state = cache_data['state']
            return state['documents'], state.get('documentPanels', {})
    except Exception as e:
        print(f"Error loading cache file: {e}")
        sys.exit(1)

def format_meeting_as_markdown(meeting):
    """Format a single meeting as markdown."""
    title = meeting.get('title', 'Untitled Meeting')
    created_at = meeting.get('created_at', '')
    updated_at = meeting.get('updated_at', '')
    
    # Parse dates
    try:
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    except:
        created_date = created_at
    
    try:
        updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
    except:
        updated_date = updated_at
    
    markdown = f"# {title}\n\n"
    markdown += f"**Created:** {created_date}\n"
    markdown += f"**Updated:** {updated_date}\n"
    markdown += f"**ID:** {meeting.get('id', 'N/A')}\n\n"
    
    # Add summary if available
    if meeting.get('summary'):
        markdown += f"## Summary\n\n{meeting['summary']}\n\n"
    
    # Add rich content from panels
    panels = meeting.get('panels', [])
    if panels:
        markdown += "## Meeting Content\n\n"
        for panel in panels:
            panel_title = panel.get('title', 'Untitled Section')
            markdown += f"### {panel_title}\n\n"
            content_markdown = convert_rich_content_to_markdown(panel.get('content'))
            if content_markdown:
                markdown += f"{content_markdown}\n\n"
    
    # Fallback to old notes format if no panels
    if not panels:
        notes_markdown = meeting.get('notes_markdown')
        notes_plain = meeting.get('notes_plain')
        notes = meeting.get('notes')
        
        if notes_markdown:
            markdown += f"## Notes\n\n{notes_markdown}\n\n"
        elif notes_plain:
            markdown += f"## Notes\n\n{notes_plain}\n\n"
        elif notes:
            markdown += f"## Notes\n\n{str(notes)}\n\n"
    
    # Add people if available
    if meeting.get('people'):
        people_data = meeting['people']
        markdown += "## Participants\n\n"
        
        # Add creator
        if people_data.get('creator'):
            creator = people_data['creator']
            creator_name = creator.get('name', 'Unknown')
            markdown += f"- {creator_name} (creator)\n"
        
        # Add attendees
        if people_data.get('attendees'):
            for attendee in people_data['attendees']:
                if isinstance(attendee, dict):
                    attendee_name = attendee.get('name', attendee.get('displayName', 'Unknown'))
                    markdown += f"- {attendee_name}\n"
                elif isinstance(attendee, str):
                    markdown += f"- {attendee}\n"
        
        markdown += "\n"
    
    return markdown

def extract_meeting_notes_to_files(cache_path, base_output_dir='daily_outputs'):
    """Extract meeting notes from Granola cache as individual files organized by date."""
    documents, document_panels = load_granola_cache(cache_path)
    
    # Create base output directory (make it absolute)
    base_path = Path(base_output_dir).expanduser().resolve()
    base_path.mkdir(exist_ok=True)
    
    meetings_processed = 0
    meetings_by_date = {}
    
    for doc_id, meeting in documents.items():
        if meeting.get('deleted_at') is None:  # Only include non-deleted meetings
            # Get panels for this meeting
            panels = get_meeting_panels(doc_id, document_panels)
            
            meeting_data = {
                'id': meeting.get('id'),
                'title': meeting.get('title'),
                'created_at': meeting.get('created_at'),
                'updated_at': meeting.get('updated_at'),
                'summary': meeting.get('summary'),
                'notes': meeting.get('notes'),
                'notes_plain': meeting.get('notes_plain'),
                'notes_markdown': meeting.get('notes_markdown'),
                'people': meeting.get('people', []),
                'type': meeting.get('type'),
                'valid_meeting': meeting.get('valid_meeting', False),
                'panels': panels
            }
            
            # Get date for directory organization
            meeting_date = get_meeting_date(meeting.get('created_at', ''))
            
            # Create date directory
            date_dir = base_path / meeting_date
            date_dir.mkdir(exist_ok=True)
            
            # Create safe filename
            title = meeting.get('title', 'Untitled Meeting')
            safe_title = sanitize_filename(title)
            filename = f"{safe_title}.md"
            
            # Handle duplicate filenames by adding timestamp
            file_path = date_dir / filename
            if file_path.exists():
                timestamp = meeting.get('created_at', '').replace(':', '-').replace('Z', '')
                filename = f"{safe_title}_{timestamp}.md"
                file_path = date_dir / filename
            
            # Generate markdown content
            markdown_content = format_meeting_as_markdown(meeting_data)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            meetings_processed += 1
            
            # Track meetings by date for summary
            if meeting_date not in meetings_by_date:
                meetings_by_date[meeting_date] = []
            meetings_by_date[meeting_date].append({
                'title': title,
                'filename': filename
            })
    
    # Print summary
    print(f"Exported {meetings_processed} meetings to {base_output_dir}/")
    print(f"Organized into {len(meetings_by_date)} date directories:")
    for date, meetings in sorted(meetings_by_date.items()):
        print(f"  {date}: {len(meetings)} meetings")

def extract_meeting_notes(cache_path, output_format='json', output_file=None):
    """Extract meeting notes from Granola cache (legacy format)."""
    documents, document_panels = load_granola_cache(cache_path)
    
    meetings = []
    for doc_id, meeting in documents.items():
        if meeting.get('deleted_at') is None:  # Only include non-deleted meetings
            # Get panels for this meeting
            panels = get_meeting_panels(doc_id, document_panels)
            
            meeting_data = {
                'id': meeting.get('id'),
                'title': meeting.get('title'),
                'created_at': meeting.get('created_at'),
                'updated_at': meeting.get('updated_at'),
                'summary': meeting.get('summary'),
                'notes': meeting.get('notes'),
                'notes_plain': meeting.get('notes_plain'),
                'notes_markdown': meeting.get('notes_markdown'),
                'people': meeting.get('people', []),
                'type': meeting.get('type'),
                'valid_meeting': meeting.get('valid_meeting', False),
                'panels': panels
            }
            meetings.append(meeting_data)
    
    # Sort meetings by creation date (newest first)
    meetings.sort(key=lambda x: x['created_at'] or '', reverse=True)
    
    if output_format == 'json':
        output_content = json.dumps(meetings, indent=2, ensure_ascii=False)
    elif output_format == 'markdown':
        output_content = f"# Meeting Notes Export\n\nExported {len(meetings)} meetings on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
        for meeting in meetings:
            output_content += format_meeting_as_markdown(meeting)
            output_content += "---\n\n"
    else:
        print(f"Unsupported format: {output_format}")
        sys.exit(1)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output_content)
        print(f"Exported {len(meetings)} meetings to {output_file}")
    else:
        print(output_content)

def main():
    parser = argparse.ArgumentParser(description='Extract meeting notes from Granola cache')
    parser.add_argument('--cache-path', 
                       default='~/Library/Application Support/Granola/cache-v3.json',
                       help='Path to Granola cache file')
    parser.add_argument('--output-dir',
                       default='daily_outputs',
                       help='Base directory for organized meeting files (default: daily_outputs)')
    parser.add_argument('--legacy-mode',
                       action='store_true',
                       help='Use legacy output format (single file or stdout)')
    parser.add_argument('--format', 
                       choices=['json', 'markdown'], 
                       default='markdown',
                       help='Output format for legacy mode (default: markdown)')
    parser.add_argument('--output', 
                       help='Output file for legacy mode (prints to stdout if not specified)')
    
    args = parser.parse_args()
    
    # Expand user path
    cache_path = Path(args.cache_path).expanduser()
    
    if not cache_path.exists():
        print(f"Cache file not found: {cache_path}")
        sys.exit(1)
    
    if args.legacy_mode:
        extract_meeting_notes(cache_path, args.format, args.output)
    else:
        extract_meeting_notes_to_files(cache_path, args.output_dir)

if __name__ == '__main__':
    main()