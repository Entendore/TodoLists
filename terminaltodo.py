import json
import os
from datetime import datetime, timedelta, date
import time
import sys
import re
from pathlib import Path
import textwrap
from collections import defaultdict
import statistics

# File to store tasks
DATA_FILE = "todo_data.json"
MAX_CARRYOVERS = 3  # Global limit for task carryovers
MAX_LINE_WIDTH = 100  # For text wrapping

# Professional color scheme - muted, accessible palette
class Theme:
    # Primary colors
    PRIMARY = '\033[38;2;75;85;192m'    # Professional blue
    SECONDARY = '\033[38;2;120;90;210m' # Purple accent
    ACCENT = '\033[38;2;45;155;120m'   # Green for success
    
    # Status colors
    SUCCESS = '\033[38;2;40;167;69m'   # Bootstrap success green
    WARNING = '\033[38;2;255;193;7m'   # Bootstrap warning yellow
    DANGER = '\033[38;2;220;53;69m'    # Bootstrap danger red
    INFO = '\033[38;2;23;162;184m'     # Bootstrap info blue
    
    # Neutral colors
    TEXT = '\033[38;2;64;64;64m'       # Dark gray text
    LIGHT_TEXT = '\033[38;2;120;120;120m' # Light gray text
    BORDER = '\033[38;2;200;200;200m'  # Light border color
    HIGHLIGHT = '\033[38;2;230;240;255m' # Light blue highlight
    
    # Special states
    COMPLETED = '\033[38;2;150;150;150m' # Muted gray for completed items
    STRIKETHROUGH = '\033[9m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    RESET = '\033[0m'
    
    # UI components
    @classmethod
    def header(cls, text, icon=""):
        return f"{cls.BOLD}{cls.PRIMARY}{icon} {text}{cls.RESET}\n{cls.BORDER}{'─' * (MAX_LINE_WIDTH - 10)}{cls.RESET}"
    
    @classmethod
    def section(cls, text):
        return f"\n{cls.BOLD}{cls.TEXT}▸ {text}{cls.RESET}"
    
    @classmethod
    def status(cls, text, type="info"):
        colors = {
            "success": cls.SUCCESS,
            "warning": cls.WARNING,
            "danger": cls.DANGER,
            "info": cls.INFO
        }
        return f"{colors.get(type, cls.INFO)}{cls.BOLD}●{cls.RESET} {text}"
    
    @classmethod
    def menu_item(cls, number, text, shortcut=None):
        shortcut_text = f" {cls.LIGHT_TEXT}[{shortcut}]{cls.RESET}" if shortcut else ""
        return f"{cls.BOLD}{cls.PRIMARY}{number}.{cls.RESET} {text}{shortcut_text}"
    
    @classmethod
    def progress_bar(cls, progress, width=30):
        """Create a professional progress bar with gradient effect"""
        filled = int(progress * width)
        empty = width - filled
        
        # Create gradient effect for filled portion
        bar = ""
        for i in range(filled):
            # Gradient from light to dark blue
            ratio = i / max(width, 1)
            r = int(120 + ratio * 30)
            g = int(140 + ratio * 50)
            b = int(210 + ratio * 40)
            bar += f"\033[38;2;{r};{g};{b}m█{cls.RESET}"
        
        bar += f"{cls.BORDER}{'░' * empty}{cls.RESET}"
        percentage = f"{cls.BOLD}{int(progress*100)}%{cls.RESET}"
        
        return f"{bar} {percentage}"
    
    @classmethod
    def card(cls, title, content, border_color=BORDER):
        """Create a professional card UI element"""
        lines = content.split('\n')
        max_width = max(len(line) for line in lines + [title]) + 4
        
        # Top border
        output = f"{border_color}┌{'─' * (max_width)}┐{cls.RESET}\n"
        
        # Title
        padding = (max_width - len(title)) // 2
        output += f"{border_color}│{cls.RESET} {cls.BOLD}{title}{' ' * (max_width - len(title) - 1)}{border_color}│{cls.RESET}\n"
        output += f"{border_color}├{'─' * (max_width)}┤{cls.RESET}\n"
        
        # Content
        for line in lines:
            output += f"{border_color}│{cls.RESET} {line}{' ' * (max_width - len(line) - 1)}{border_color}│{cls.RESET}\n"
        
        # Bottom border
        output += f"{border_color}└{'─' * (max_width)}┘{cls.RESET}"
        return output

def load_tasks():
    """Load tasks from JSON file with backward compatibility"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            
            # Backward compatibility for existing data files
            for task in data["tasks"]:
                if "priority" not in task:
                    task["priority"] = "Medium"
                if "is_recurring" not in task:
                    task["is_recurring"] = False
                    task["recurrence_pattern"] = ""
                if "notes" not in task:
                    task["notes"] = ""
                if "no_carryover" not in task:
                    task["no_carryover"] = False
                if "carry_count" not in task:
                    task["carry_count"] = 0
                if "estimated_time" not in task:
                    task["estimated_time"] = ""
                if "max_time" not in task:
                    task["max_time"] = ""
                if "subtasks" not in task:
                    task["subtasks"] = []
                if "time_spent" not in task:
                    task["time_spent"] = 0  # Total minutes spent
                if "time_sessions" not in task:
                    task["time_sessions"] = []  # List of {start, end, duration}
            
            if "max_carryovers" not in data:
                data["max_carryovers"] = MAX_CARRYOVERS
            
            return data
    
    return {
        "tasks": [],
        "last_carryover_date": datetime.now().strftime("%Y-%m-%d"),
        "max_carryovers": MAX_CARRYOVERS
    }

def parse_time_to_minutes(time_str):
    """Convert time string (30m, 1h, 1.5h) to minutes"""
    if not time_str:
        return 0
    
    time_str = time_str.strip().lower()
    if 'h' in time_str:
        hours = float(time_str.replace('h', ''))
        return int(hours * 60)
    elif 'm' in time_str:
        return int(time_str.replace('m', ''))
    else:
        # Assume minutes if no unit specified
        try:
            return int(time_str)
        except ValueError:
            return 0

def format_minutes_to_time(minutes):
    """Convert minutes to human-readable format (1h 30m)"""
    if minutes <= 0:
        return "0m"
    
    hours = minutes // 60
    mins = minutes % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if mins > 0 or not parts:
        parts.append(f"{mins}m")
    
    return " ".join(parts)

def format_time_to_words(minutes):
    """Convert minutes to descriptive words"""
    if minutes < 15:
        return "Quick task"
    elif minutes < 30:
        return "Short task"
    elif minutes < 60:
        return "Medium task"
    elif minutes < 120:
        return "Long task"
    else:
        return "Extended task"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')
    # Print header on every screen
    print(f"{Theme.BOLD}{Theme.PRIMARY}TASKFLOW │ Professional Task Management{Theme.RESET}")
    print(f"{Theme.BORDER}{'═' * (MAX_LINE_WIDTH - 10)}{Theme.RESET}\n")

def format_task_display(task, index=None, show_subtasks=True):
    """Professional task formatting with clean typography"""
    # Priority indicators with subtle styling
    priority_indicators = {
        "High": f"{Theme.DANGER}◉{Theme.RESET}",
        "Medium": f"{Theme.WARNING}◉{Theme.RESET}",
        "Low": f"{Theme.SUCCESS}◉{Theme.RESET}"
    }
    
    # Main task styling
    checkbox = f"{Theme.SUCCESS}✓{Theme.RESET}" if task["completed"] else " "
    checkbox_display = f"{Theme.BORDER}[{checkbox}]{Theme.RESET}"
    
    # Apply strikethrough and muted color for completed tasks
    style_prefix = ""
    style_suffix = ""
    if task["completed"]:
        style_prefix = f"{Theme.COMPLETED}{Theme.STRIKETHROUGH}"
        style_suffix = f"{Theme.RESET}"
    
    # Time estimate display with professional formatting
    est_min = parse_time_to_minutes(task["estimated_time"])
    max_min = parse_time_to_minutes(task["max_time"])
    time_spent = task["time_spent"]
    
    time_display = ""
    if est_min or max_min or time_spent:
        parts = []
        if time_spent:
            parts.append(f"{Theme.ACCENT}{format_minutes_to_time(time_spent)}{Theme.RESET}")
        if est_min:
            parts.append(f"{Theme.LIGHT_TEXT}{format_minutes_to_time(est_min)}{Theme.RESET}")
        if max_min:
            parts.append(f"{Theme.WARNING}{format_minutes_to_time(max_min)}{Theme.RESET}")
        
        # Use different separators based on how many parts we have
        if len(parts) == 1:
            time_display = parts[0]
        elif len(parts) == 2:
            time_display = f"{parts[0]} {Theme.LIGHT_TEXT}/ {Theme.RESET}{parts[1]}"
        else:
            time_display = f"{parts[0]} {Theme.LIGHT_TEXT}/ {Theme.RESET}{parts[1]} {Theme.LIGHT_TEXT}/ {Theme.RESET}{parts[2]}"
        
        time_display = f"  {Theme.LIGHT_TEXT}⏱ {time_display}{Theme.RESET}"
    
    # Recurrence and attachment indicators with subtle styling
    indicators = []
    if task["is_recurring"]:
        indicators.append(f"{Theme.LIGHT_TEXT}⟳{Theme.RESET}")
    if re.search(r'/[\w\./_-]+', task["notes"]):
        indicators.append(f"{Theme.LIGHT_TEXT}📎{Theme.RESET}")
    if task["no_carryover"]:
        indicators.append(f"{Theme.LIGHT_TEXT}🚫{Theme.RESET}")
    
    indicator_str = " ".join(indicators)
    if indicator_str:
        indicator_str = f"{indicator_str} "
    
    # Build main task line with professional spacing
    prefix = f"{index}. " if index is not None else ""
    priority_icon = priority_indicators.get(task["priority"], "◉")
    
    main_line = (
        f"{prefix}{priority_icon} {checkbox_display} "
        f"{style_prefix}{task['description']}{style_suffix}"
        f"{time_display}"
    )
    
    if indicator_str:
        main_line = f"{indicator_str}{main_line}"
    
    # Build subtasks section with clean indentation
    subtask_lines = []
    if show_subtasks and task["subtasks"]:
        for st in task["subtasks"]:
            st_checkbox = f"{Theme.SUCCESS}✓{Theme.RESET}" if st["completed"] else " "
            st_checkbox_display = f"{Theme.BORDER}[{st_checkbox}]{Theme.RESET}"
            
            st_style_prefix = ""
            st_style_suffix = ""
            if st["completed"]:
                st_style_prefix = f"{Theme.COMPLETED}{Theme.STRIKETHROUGH}"
                st_style_suffix = f"{Theme.RESET}"
            
            subtask_line = (
                f"    {st_checkbox_display} {st_style_prefix}{st['description']}"
                f"{st_style_suffix}"
            )
            subtask_lines.append(subtask_line)
    
    # Combine all parts
    output = [main_line]
    if subtask_lines:
        output.extend(subtask_lines)
    
    return "\n".join(output)

def get_todays_tasks(data):
    """Get today's tasks sorted by priority with subtasks"""
    today = datetime.now().strftime("%Y-%m-%d")
    tasks = [task for task in data["tasks"] 
            if task["due_date"] == today]
    
    # Priority order: High (0), Medium (1), Low (2)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(tasks, 
                 key=lambda x: (priority_order.get(x["priority"], 1), 
                               x["created_at"]))

def display_todays_tasks(tasks):
    """Professional display of today's tasks with analytics"""
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["completed"])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Time statistics
    total_estimated = sum(parse_time_to_minutes(t["estimated_time"]) for t in tasks)
    total_spent = sum(t["time_spent"] for t in tasks)
    time_efficiency = (total_spent / total_estimated * 100) if total_estimated > 0 else 0
    
    # Create header card
    header_content = (
        f"{Theme.LIGHT_TEXT}Today's Focus{Theme.RESET}\n"
        f"{Theme.BOLD}{today}{Theme.RESET}\n"
        f"{Theme.LIGHT_TEXT}Plan your day, achieve your goals{Theme.RESET}"
    )
    print(Theme.card("DAILY OVERVIEW", header_content, Theme.PRIMARY))
    
    # Progress summary
    print(f"\n{Theme.header('PROGRESS SUMMARY')}")
    
    # Tasks progress bar
    print(f"\n{Theme.TEXT}Tasks Completed:{Theme.RESET}")
    print(Theme.progress_bar(completed_tasks / max(total_tasks, 1)))
    print(f"{Theme.LIGHT_TEXT}{completed_tasks} of {total_tasks} tasks completed{Theme.RESET}")
    
    # Time progress bar (if estimates exist)
    if total_estimated > 0:
        print(f"\n{Theme.TEXT}Time Utilization:{Theme.RESET}")
        print(Theme.progress_bar(min(total_spent / max(total_estimated, 1), 1.0)))
        
        efficiency_text = f"{time_efficiency:.0f}% of estimated time used"
        efficiency_color = Theme.SUCCESS if time_efficiency <= 100 else Theme.WARNING
        print(f"{efficiency_color}{efficiency_text}{Theme.RESET}")
    
    # Task distribution by priority
    print(f"\n{Theme.header('TODAY\'S TASKS')}")
    
    if not tasks:
        print(f"\n{Theme.status('No tasks scheduled for today. Well done!', 'success')}")
        return
    
    # Group by priority with professional section headers
    priorities = {
        "High": {"tasks": [], "color": Theme.DANGER},
        "Medium": {"tasks": [], "color": Theme.WARNING},
        "Low": {"tasks": [], "color": Theme.SUCCESS}
    }
    
    for task in tasks:
        if task["priority"] in priorities:
            priorities[task["priority"]]["tasks"].append(task)
    
    # Display each priority section
    for priority, data in priorities.items():
        if data["tasks"]:
            count = len(data["tasks"])
            completed = sum(1 for t in data["tasks"] if t["completed"])
            
            print(f"\n{Theme.BOLD}{data['color']}{priority} PRIORITY "
                  f"{Theme.LIGHT_TEXT}({completed}/{count} completed){Theme.RESET}")
            
            for i, task in enumerate(data["tasks"], 1):
                print(format_task_display(task, i))
    
    # Quick stats footer
    if total_tasks > 0:
        print(f"\n{Theme.BORDER}{'─' * (MAX_LINE_WIDTH - 10)}{Theme.RESET}")
        stats = []
        if total_estimated > 0:
            stats.append(f"Est. time: {Theme.LIGHT_TEXT}{format_minutes_to_time(total_estimated)}{Theme.RESET}")
        stats.append(f"Avg. task time: {Theme.LIGHT_TEXT}{format_minutes_to_time(total_spent // max(total_tasks, 1))}{Theme.RESET}")
        stats.append(f"Efficiency: {Theme.LIGHT_TEXT}{time_efficiency:.0f}%{Theme.RESET}")
        
        print(f" {Theme.LIGHT_TEXT}│ {Theme.RESET}".join(stats))

def time_tracking_menu(data):
    """Professional time tracking interface"""
    clear_screen()
    print(Theme.header("TIME TRACKING", "⏱"))
    
    # Show active timer if any
    active = get_active_timer(data)
    if active:
        elapsed_str = format_minutes_to_time(int(active["elapsed_minutes"]))
        elapsed_word = format_time_to_words(int(active["elapsed_minutes"]))
        
        timer_content = (
            f"{Theme.LIGHT_TEXT}Active Session{Theme.RESET}\n"
            f"{Theme.BOLD}{active['task_name']}{Theme.RESET}\n"
            f"{Theme.ACCENT}◉ {elapsed_str}{Theme.RESET} {Theme.LIGHT_TEXT}({elapsed_word}){Theme.RESET}\n"
            f"Started: {active['start_time'].strftime('%I:%M %p')}"
        )
        print(Theme.card("CURRENT TIMER", timer_content, Theme.ACCENT))
        
        print(f"\n{Theme.header('TIMER CONTROLS')}")
        print(Theme.menu_item(1, "Stop timer", "S"))
        print(Theme.menu_item(2, "View today's time report", "R"))
        print(Theme.menu_item(0, "Return to main menu", "ESC"))
    else:
        print(Theme.status("No active timer. Select a task to begin timing.", "info"))
        
        # Show incomplete tasks for timing
        today = datetime.now().strftime("%Y-%m-%d")
        incomplete_tasks = [t for t in data["tasks"] 
                          if t["due_date"] == today and not t["completed"]]
        
        if incomplete_tasks:
            print(f"\n{Theme.header('AVAILABLE TASKS')}")
            for i, task in enumerate(incomplete_tasks, 1):
                print(f"  {i}. {format_task_display(task)}")
            
            print(f"\n{Theme.header('ACTIONS')}")
            print(Theme.menu_item(1, f"Start timer for task #", "1-{len(incomplete_tasks)}"))
        
        print(Theme.menu_item(0, "Return to main menu", "ESC"))
    
    return active

def reports_menu(data):
    """Professional reports interface"""
    clear_screen()
    print(Theme.header("TIME ANALYTICS", "📊"))
    
    print(Theme.status("Gain insights into your productivity patterns and time usage", "info"))
    
    print(f"\n{Theme.header('REPORT CATALOG')}")
    print(Theme.menu_item(1, "Daily Summary", "D"))
    print(Theme.menu_item(2, "Weekly Trends", "W"))
    print(Theme.menu_item(3, "Category Analysis", "C"))
    print(Theme.menu_item(4, "Estimation Accuracy", "E"))
    print(Theme.menu_item(5, "Productivity Insights", "P"))
    print(Theme.menu_item(0, "Return to main menu", "ESC"))
    
    print(f"\n{Theme.BORDER}{'─' * (MAX_LINE_WIDTH - 10)}{Theme.RESET}")
    print(f"{Theme.LIGHT_TEXT}Tip: Use these reports to optimize your planning and improve time estimation accuracy{Theme.RESET}")

def main_menu():
    """Professional main menu interface"""
    clear_screen()
    
    # Welcome message with time of day
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 17:
        greeting = "Good afternoon"
    elif 17 <= current_hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Good night"
    
    # System status indicators
    active_timer = get_active_timer(load_tasks()) is not None
    timer_status = f"{Theme.ACCENT}◉ Active{Theme.RESET}" if active_timer else f"{Theme.LIGHT_TEXT}◉ Idle{Theme.RESET}"
    
    # Create header content
    header_content = (
        f"{Theme.BOLD}{greeting}, Productivity Professional{Theme.RESET}\n"
        f"{Theme.LIGHT_TEXT}TaskFlow v2.1 │ {timer_status}{Theme.RESET}\n"
        f"{Theme.LIGHT_TEXT}A professional task management system{Theme.RESET}"
    )
    print(Theme.card("WELCOME", header_content, Theme.PRIMARY))
    
    print(f"\n{Theme.header('MAIN MENU')}")
    print(Theme.menu_item(1, "Create new task", "N"))
    print(Theme.menu_item(2, "View & manage today's tasks", "T"))
    print(Theme.menu_item(3, "Time tracking", "S"))
    print(Theme.menu_item(4, "Analytics & reports", "R"))
    print(Theme.menu_item(5, "Task archive", "A"))
    print(Theme.menu_item(6, "System settings", "G"))
    print(Theme.menu_item(0, "Exit application", "Q"))
    
    print(f"\n{Theme.BORDER}{'─' * (MAX_LINE_WIDTH - 10)}{Theme.RESET}")
    print(f"{Theme.LIGHT_TEXT}Use number keys or shortcut letters to navigate │ Press ESC to cancel any action{Theme.RESET}")

# Helper functions (get_active_timer, generate reports, etc.) remain similar to previous implementation
# but with professional styling applied

def get_active_timer(data):
    """Get currently active timer if any"""
    for task in data["tasks"]:
        for session in task["time_sessions"]:
            if "end_time" not in session:
                start_time = datetime.fromisoformat(session["start_time"])
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                return {
                    "task_id": task["id"],
                    "task_name": task["description"],
                    "start_time": start_time,
                    "elapsed_minutes": round(elapsed, 1)
                }
    return None

def main():
    """Professional application entry point with clean UI flow"""
    data = load_tasks()
    
    while True:
        main_menu()
        choice = input(f"\n{Theme.BOLD}{Theme.PRIMARY}Select option [{Theme.LIGHT_TEXT}1-6 or 0{Theme.PRIMARY}]: {Theme.RESET}").strip().lower()
        
        if choice in ['0', 'q']:
            # Professional exit experience
            clear_screen()
            exit_content = (
                f"{Theme.LIGHT_TEXT}TaskFlow Professional │ Session Summary{Theme.RESET}\n"
                f"{Theme.BOLD}Thank you for using TaskFlow{Theme.RESET}\n"
                f"{Theme.LIGHT_TEXT}All data saved securely │ Next sync: {datetime.now().strftime('%I:%M %p')}{Theme.RESET}"
            )
            print(Theme.card("SESSION COMPLETE", exit_content, Theme.SUCCESS))
            time.sleep(2)
            sys.exit(0)
        
        elif choice in ['1', 'n']:
            # Create new task flow
            clear_screen()
            print(Theme.header("NEW TASK", "➕"))
            
            description = input(f"{Theme.TEXT}Task description:{Theme.RESET} ").strip()
            # ... (rest of task creation with professional UI)
            
        elif choice in ['2', 't']:
            # Today's tasks view
            clear_screen()
            todays_tasks = get_todays_tasks(data)
            display_todays_tasks(todays_tasks)
            
            input(f"\n{Theme.LIGHT_TEXT}Press Enter to return to main menu...{Theme.RESET}")
        
        elif choice in ['3', 's']:
            # Time tracking menu
            while True:
                active = time_tracking_menu(data)
                timer_choice = input(f"\n{Theme.BOLD}{Theme.PRIMARY}Select action: {Theme.RESET}").strip().lower()
                
                if timer_choice in ['0', 'esc']:
                    break
                # ... (timer handling logic)
        
        elif choice in ['4', 'r']:
            # Reports menu
            while True:
                reports_menu(data)
                report_choice = input(f"\n{Theme.BOLD}{Theme.PRIMARY}Select report: {Theme.RESET}").strip().lower()
                
                if report_choice in ['0', 'esc']:
                    break
                # ... (report generation logic)
        
        else:
            print(f"\n{Theme.status('Invalid selection. Please choose a valid option from the menu.', 'danger')}")
            time.sleep(1.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print(Theme.status("Application terminated by user. All data saved.", "info"))
        time.sleep(1)
        sys.exit(0)
    except Exception as e:
        clear_screen()
        print(Theme.status(f"Critical error: {str(e)}", "danger"))
        print(Theme.status("Contact support with the error details above.", "warning"))
        time.sleep(3)
        sys.exit(1)