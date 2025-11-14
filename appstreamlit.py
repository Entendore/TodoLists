import streamlit as st
import json
import os
from datetime import datetime, timedelta, date
import time
import re
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from collections import defaultdict
import statistics

# Set page configuration
st.set_page_config(
    page_title="TaskFlow Professional",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling with CSS
st.markdown("""
<style>
    /* Professional color scheme */
    :root {
        --primary-color: #4B55B2;
        --secondary-color: #785BD2;
        --accent-color: #2D9B76;
        --success-color: #28A745;
        --warning-color: #FFC107;
        --danger-color: #DC3545;
        --info-color: #17A2B8;
        --light-color: #F8F9FA;
        --dark-color: #343A40;
        --border-color: #DEE2E6;
        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --transition: all 0.3s ease;
    }
    
    /* Card styling */
    .stCard {
        background-color: white;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: var(--card-shadow);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: var(--transition);
    }
    
    .stCard:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(75, 85, 178, 0.3);
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active {
        background-color: var(--success-color);
    }
    
    .status-idle {
        background-color: var(--warning-color);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: var(--transition);
        box-shadow: 0 2px 4px rgba(75, 85, 178, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(75, 85, 178, 0.4);
    }
    
    .stButton > button:focus {
        box-shadow: 0 0 0 3px rgba(75, 85, 178, 0.3);
    }
    
    /* Task item styling */
    .task-item {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
        border-left: 4px solid var(--primary-color);
        transition: var(--transition);
    }
    
    .task-item:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .task-high {
        border-left-color: var(--danger-color);
    }
    
    .task-medium {
        border-left-color: var(--warning-color);
    }
    
    .task-low {
        border-left-color: var(--success-color);
    }
    
    .task-completed {
        opacity: 0.7;
        text-decoration: line-through;
        border-left-color: #CED4DA;
    }
    
    /* Progress bar styling */
    .progress-container {
        width: 100%;
        background-color: #E9ECEF;
        border-radius: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 8px;
        border-radius: 8px;
        background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
    }
    
    /* Metric styling */
    div[data-testid="metric-container"] {
        background-color: white !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: var(--card-shadow) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px 8px 0 0;
        background-color: #E9ECEF;
        color: var(--dark-color);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Subtask styling */
    .subtask-item {
        padding-left: 2rem;
        margin-top: 0.25rem;
        border-left: 2px dashed #DEE2E6;
    }
    
    /* Report chart styling */
    .plotly-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--card-shadow);
    }
    
    /* Settings section */
    .settings-section {
        background-color: #F8F9FA;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Notification styling */
    .notification {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
    }
    
    .notification-success {
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
    }
    
    .notification-warning {
        background-color: #FFF3CD;
        border: 1px solid #FFEAA7;
        color: #856404;
    }
    
    .notification-error {
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        color: #721C24;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-title {
            font-size: 1.8rem;
        }
        
        .metric-row > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Data file configuration
DATA_FILE = "taskflow_data.json"

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'active_timer' not in st.session_state:
    st.session_state.active_timer = None
if 'last_carryover_date' not in st.session_state:
    st.session_state.last_carryover_date = datetime.now().strftime("%Y-%m-%d")
if 'max_carryovers' not in st.session_state:
    st.session_state.max_carryovers = 3
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

def load_data():
    """Load tasks from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            st.session_state.tasks = data.get("tasks", [])
            st.session_state.last_carryover_date = data.get("last_carryover_date", datetime.now().strftime("%Y-%m-%d"))
            st.session_state.max_carryovers = data.get("max_carryovers", 3)
    else:
        st.session_state.tasks = []
        st.session_state.last_carryover_date = datetime.now().strftime("%Y-%m-%d")
        st.session_state.max_carryovers = 3

def save_data():
    """Save tasks to JSON file"""
    data = {
        "tasks": st.session_state.tasks,
        "last_carryover_date": st.session_state.last_carryover_date,
        "max_carryovers": st.session_state.max_carryovers
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    add_notification("Data saved successfully", "success")

def add_notification(message, type="info"):
    """Add a notification to the session state"""
    st.session_state.notifications.append({
        "message": message,
        "type": type,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    # Keep only the last 5 notifications
    if len(st.session_state.notifications) > 5:
        st.session_state.notifications.pop(0)

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

def perform_carryover():
    """Carry over incomplete tasks with smart rules"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today == st.session_state.last_carryover_date:
        return False
    
    carried_count = 0
    
    for task in st.session_state.tasks:
        if (task.get("completed", False) or 
            task["due_date"] >= today or 
            task.get("no_carryover", False)):
            continue
        
        if task.get("carry_count", 0) >= st.session_state.max_carryovers:
            continue
        
        task["due_date"] = today
        task["carry_count"] = task.get("carry_count", 0) + 1
        carried_count += 1
    
    # Handle recurring tasks
    for task in st.session_state.tasks[:]:
        if task.get("is_recurring") and task.get("completed", False):
            if "completed_at" in task and task["completed_at"]:
                completion_date = datetime.fromisoformat(task["completed_at"]).date()
                yesterday = date.today() - timedelta(days=1)
                
                if completion_date == yesterday:
                    new_task = task.copy()
                    new_task["id"] = max([t["id"] for t in st.session_state.tasks] + [0]) + 1
                    new_task["completed"] = False
                    new_task["completed_at"] = None
                    new_task["due_date"] = calculate_next_due_date(task)
                    new_task["carry_count"] = 0
                    new_task["subtasks"] = []
                    new_task["time_spent"] = 0
                    new_task["time_sessions"] = []
                    st.session_state.tasks.append(new_task)
    
    st.session_state.last_carryover_date = today
    return carried_count > 0

def calculate_next_due_date(task):
    """Calculate next due date for recurring tasks"""
    today = date.today()
    pattern = task["recurrence_pattern"].lower()
    
    if pattern == "daily":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    
    elif pattern == "weekly":
        return (today + timedelta(days=7)).strftime("%Y-%m-%d")
    
    elif pattern == "monthly":
        next_month = today.replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        last_day = (next_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        day = min(today.day, last_day.day)
        return next_month.replace(day=day).strftime("%Y-%m-%d")
    
    elif "," in pattern:  # Specific weekdays
        weekdays = {
            "mon": 0, "tue": 1, "wed": 2, "thu": 3,
            "fri": 4, "sat": 5, "sun": 6
        }
        valid_days = [weekdays[day.strip()] for day in pattern.split(",") if day.strip() in weekdays]
        
        if valid_days:
            next_dates = [next_weekday(today, wd) for wd in valid_days]
            return min(next_dates).strftime("%Y-%m-%d")
    
    return (today + timedelta(days=1)).strftime("%Y-%m-%d")

def next_weekday(d, weekday):
    """Find next occurrence of specific weekday"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)

def start_timer(task_id):
    """Start timing a task"""
    # Stop any active timers first
    stop_active_timer()
    
    for task in st.session_state.tasks:
        if task["id"] == task_id and not task.get("completed", False):
            # Start new session
            if "time_sessions" not in task:
                task["time_sessions"] = []
            
            task["time_sessions"].append({
                "start_time": datetime.now().isoformat(),
                "session_id": max([s.get("session_id", 0) for s in task["time_sessions"]] + [0]) + 1
            })
            
            st.session_state.active_timer = {
                "task_id": task_id,
                "start_time": datetime.now(),
                "task_name": task["description"]
            }
            
            add_notification(f"Timer started for '{task['description']}'", "success")
            return True
    
    add_notification("Could not start timer for this task", "error")
    return False

def stop_active_timer():
    """Stop the active timer and record duration"""
    if st.session_state.active_timer:
        task_id = st.session_state.active_timer["task_id"]
        start_time = st.session_state.active_timer["start_time"]
        duration_minutes = (datetime.now() - start_time).total_seconds() / 60
        
        for task in st.session_state.tasks:
            if task["id"] == task_id:
                if "time_sessions" not in task:
                    task["time_sessions"] = []
                
                # Find the active session and update it
                for session in task["time_sessions"]:
                    if "end_time" not in session:
                        session["end_time"] = datetime.now().isoformat()
                        session["duration"] = round(duration_minutes, 1)
                
                # Update total time spent
                if "time_spent" not in task:
                    task["time_spent"] = 0
                task["time_spent"] += duration_minutes
                
                add_notification(f"Timer stopped. Spent {format_minutes_to_time(int(duration_minutes))} on '{task['description']}'", "success")
        
        st.session_state.active_timer = None
        return True
    
    return False

def get_todays_tasks():
    """Get today's tasks sorted by priority"""
    today = datetime.now().strftime("%Y-%m-%d")
    tasks = [task for task in st.session_state.tasks 
            if task["due_date"] == today]
    
    # Priority order: High (0), Medium (1), Low (2)
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(tasks, key=lambda x: (priority_order.get(x["priority"], 1), x.get("created_at", "")))

def get_task_by_id(task_id):
    """Get task by ID"""
    for task in st.session_state.tasks:
        if task["id"] == task_id:
            return task
    return None

def add_task(description, category="General", priority="Medium", 
             is_recurring=False, recurrence_pattern="", notes="",
             estimated_time="", max_time="", no_carryover=False,
             subtasks=None):
    """Add a new task with enhanced properties"""
    today = datetime.now().strftime("%Y-%m-%d")
    new_id = max([task["id"] for task in st.session_state.tasks] + [0]) + 1
    
    task = {
        "id": new_id,
        "description": description,
        "category": category,
        "priority": priority,
        "is_recurring": is_recurring,
        "recurrence_pattern": recurrence_pattern,
        "notes": notes,
        "due_date": today,
        "completed": False,
        "no_carryover": no_carryover,
        "carry_count": 0,
        "estimated_time": estimated_time,
        "max_time": max_time,
        "subtasks": subtasks or [],
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "time_spent": 0,
        "time_sessions": []
    }
    
    st.session_state.tasks.append(task)
    add_notification(f"Task '{description}' created successfully", "success")
    return new_id

def complete_task(task_id, complete_subtasks=False):
    """Mark task as completed with optional subtask completion"""
    for task in st.session_state.tasks:
        if task["id"] == task_id and not task.get("completed", False):
            task["completed"] = True
            task["completed_at"] = datetime.now().isoformat()
            
            if complete_subtasks and "subtasks" in task:
                for subtask in task["subtasks"]:
                    subtask["completed"] = True
            
            # Stop timer if this task was being timed
            if st.session_state.active_timer and st.session_state.active_timer["task_id"] == task_id:
                stop_active_timer()
            
            add_notification(f"Task '{task['description']}' completed", "success")
            return True
    return False

def complete_subtask(task_id, subtask_id):
    """Mark a subtask as completed"""
    task = get_task_by_id(task_id)
    if task and "subtasks" in task:
        for subtask in task["subtasks"]:
            if subtask["id"] == subtask_id and not subtask.get("completed", False):
                subtask["completed"] = True
                add_notification(f"Subtask '{subtask['description']}' completed", "success")
                return True
    return False

def generate_daily_report():
    """Generate daily time report"""
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")
    daily_tasks = [t for t in st.session_state.tasks if t["due_date"] == today_str]
    
    if not daily_tasks:
        return None
    
    # Calculate totals
    total_estimated = sum(parse_time_to_minutes(t["estimated_time"]) for t in daily_tasks)
    total_actual = sum(t.get("time_spent", 0) for t in daily_tasks)
    total_max = sum(parse_time_to_minutes(t["max_time"]) for t in daily_tasks)
    total_tasks = len(daily_tasks)
    completed_tasks = sum(1 for t in daily_tasks if t.get("completed", False))
    
    return {
        "date": today_str,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "total_estimated": total_estimated,
        "total_actual": total_actual,
        "total_max": total_max,
        "efficiency": (total_actual / total_estimated * 100) if total_estimated > 0 else 0,
        "tasks": daily_tasks
    }

def generate_weekly_report(days=7):
    """Generate weekly time report"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    daily_data = defaultdict(lambda: {
        "estimated": 0,
        "actual": 0,
        "tasks": 0,
        "completed": 0
    })
    
    for task in st.session_state.tasks:
        if "created_at" in task:
            task_date = datetime.fromisoformat(task["created_at"]).date()
            if start_date <= task_date <= end_date:
                date_str = task_date.strftime("%Y-%m-%d")
                daily_data[date_str]["estimated"] += parse_time_to_minutes(task["estimated_time"])
                daily_data[date_str]["actual"] += task.get("time_spent", 0)
                daily_data[date_str]["tasks"] += 1
                if task.get("completed", False):
                    daily_data[date_str]["completed"] += 1
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "daily_data": dict(sorted(daily_data.items())),
        "total_estimated": sum(data["estimated"] for data in daily_data.values()),
        "total_actual": sum(data["actual"] for data in daily_data.values()),
        "total_tasks": sum(data["tasks"] for data in daily_data.values()),
        "total_completed": sum(data["completed"] for data in daily_data.values())
    }

def generate_category_report(days=30):
    """Generate report by category"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    category_data = defaultdict(lambda: {
        "estimated": 0,
        "actual": 0,
        "tasks": 0,
        "completed": 0
    })
    
    for task in st.session_state.tasks:
        if "created_at" in task:
            task_date = datetime.fromisoformat(task["created_at"]).date()
            if start_date <= task_date <= end_date and (task.get("time_spent", 0) > 0 or task["estimated_time"]):
                category = task["category"]
                category_data[category]["estimated"] += parse_time_to_minutes(task["estimated_time"])
                category_data[category]["actual"] += task.get("time_spent", 0)
                category_data[category]["tasks"] += 1
                if task.get("completed", False):
                    category_data[category]["completed"] += 1
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "category_data": dict(category_data)
    }

def display_notifications():
    """Display notifications in the sidebar"""
    if st.session_state.notifications:
        with st.sidebar:
            st.markdown("### 📋 Recent Activity")
            for notification in reversed(st.session_state.notifications):
                icon = "✅" if notification["type"] == "success" else "⚠️" if notification["type"] == "warning" else "❌"
                st.markdown(f"""
                <div class="notification notification-{notification['type']}">
                    <span style="font-size: 1.2rem; margin-right: 10px;">{icon}</span>
                    <div>
                        <div style="font-weight: 500;">{notification['message']}</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">{notification['timestamp']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def display_active_timer():
    """Display active timer in the sidebar"""
    if st.session_state.active_timer:
        elapsed = (datetime.now() - st.session_state.active_timer["start_time"]).total_seconds() / 60
        elapsed_str = format_minutes_to_time(int(elapsed))
        
        with st.sidebar:
            st.markdown("### ⏱️ Active Timer")
            st.markdown(f"""
            <div class="stCard">
                <div style="font-weight: 600; color: var(--primary-color);">{st.session_state.active_timer['task_name']}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--accent-color); margin: 0.5rem 0;">{elapsed_str}</div>
                <div style="color: var(--light-color); font-size: 0.9rem;">
                    Started at: {st.session_state.active_timer['start_time'].strftime('%I:%M %p')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("⏹️ Stop Timer", use_container_width=True, type="primary"):
                    stop_active_timer()
                    st.rerun()
            with col2:
                if st.button("📋 Task Details", use_container_width=True):
                    st.session_state.selected_task_id = st.session_state.active_timer["task_id"]
                    st.session_state.show_task_details = True
                    st.rerun()

def render_task_item(task, index=None):
    """Render a single task item with professional styling"""
    priority_colors = {
        "High": "task-high",
        "Medium": "task-medium",
        "Low": "task-low"
    }
    
    task_class = priority_colors.get(task["priority"], "task-medium")
    if task.get("completed", False):
        task_class += " task-completed"
    
    # Format time display
    est_time = parse_time_to_minutes(task["estimated_time"])
    max_time = parse_time_to_minutes(task["max_time"])
    time_spent = task.get("time_spent", 0)
    
    time_display = ""
    if time_spent or est_time or max_time:
        parts = []
        if time_spent:
            parts.append(f"<span style='color: #2D9B76; font-weight: 500;'>{format_minutes_to_time(time_spent)}</span>")
        if est_time:
            parts.append(f"<span style='color: #6C757D;'>{format_minutes_to_time(est_time)}</span>")
        if max_time:
            parts.append(f"<span style='color: #FFC107;'>{format_minutes_to_time(max_time)}</span>")
        
        time_display = " / ".join(parts)
        time_display = f"<div style='font-size: 0.85rem; margin-top: 4px; color: #6C757D;'>⏱ {time_display}</div>"
    
    # Format indicators
    indicators = []
    if task.get("is_recurring", False):
        indicators.append("⟳")
    if task.get("notes") and re.search(r'/[\w\./_-]+', task["notes"]):
        indicators.append("📎")
    if task.get("no_carryover", False):
        indicators.append("🚫")
    
    indicator_str = " ".join(indicators)
    if indicator_str:
        indicator_str = f"<span style='color: #6C757D; margin-right: 8px;'>{indicator_str}</span>"
    
    # Format checkbox
    checkbox = "✓" if task.get("completed", False) else " "
    checkbox_style = "color: #28A745; font-weight: bold;" if task.get("completed", False) else ""
    
    # Subtasks
    subtasks_html = ""
    if task.get("subtasks"):
        subtasks_html = "<div style='margin-top: 8px;'>"
        for subtask in task["subtasks"]:
            st_checkbox = "✓" if subtask.get("completed", False) else " "
            st_style = "color: #28A745; text-decoration: line-through;" if subtask.get("completed", False) else ""
            subtasks_html += f"""
            <div class="subtask-item">
                <span style="display: inline-block; width: 20px; height: 20px; border: 1px solid #6C757D; border-radius: 4px; 
                            text-align: center; line-height: 18px; {st_style}">{st_checkbox}</span>
                <span style="{st_style}">{subtask['description']}</span>
            </div>
            """
        subtasks_html += "</div>"
    
    # Create the task item HTML
    task_html = f"""
    <div class="task-item {task_class}" style="cursor: pointer;" onclick="window.parent.document.querySelector('button[data-testid=\\"task-{task['id']}-details\\"]').click()">
        <div style="display: flex; align-items: center; margin-bottom: 4px;">
            <div style="display: flex; align-items: center; width: 20px; margin-right: 12px;">
                <span style="display: inline-block; width: 20px; height: 20px; border: 1.5px solid #6C757D; 
                            border-radius: 4px; text-align: center; line-height: 18px; {checkbox_style}">{checkbox}</span>
            </div>
            <div style="flex: 1; font-weight: 500;">
                {indicator_str}{task['description']}
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 0.8rem; padding: 2px 8px; border-radius: 4px; background-color: #E9ECEF; color: #495057;">
                    {task['category']}
                </span>
                <span style="font-size: 0.8rem; color: #6C757D;">
                    Due: {task['due_date']}
                </span>
            </div>
            <div style="font-size: 0.8rem; color: #6C757D;">
                {len([st for st in task.get('subtasks', []) if st.get('completed', False)])}/{len(task.get('subtasks', []))} subtasks
            </div>
        </div>
        {time_display}
        {subtasks_html}
    </div>
    """
    
    return task_html

def render_dashboard():
    """Render the dashboard view"""
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<div class="header-title">TaskFlow Professional</div>', unsafe_allow_html=True)
    
    # Time-based greeting
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good morning, Productivity Professional"
    elif 12 <= current_hour < 17:
        greeting = "Good afternoon, Productivity Professional"
    elif 17 <= current_hour < 21:
        greeting = "Good evening, Productivity Professional"
    else:
        greeting = "Good night, Productivity Professional"
    
    st.markdown(f'<div class="header-subtitle">{greeting}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load data and perform carryover
    load_data()
    carryover_performed = perform_carryover()
    if carryover_performed:
        add_notification("Carryover completed for today's tasks", "info")
    
    # Get today's tasks
    today = datetime.now().strftime("%A, %B %d, %Y")
    todays_tasks = get_todays_tasks()
    
    # Calculate statistics
    total_tasks = len(todays_tasks)
    completed_tasks = sum(1 for t in todays_tasks if t.get("completed", False))
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Time statistics
    total_estimated = sum(parse_time_to_minutes(t["estimated_time"]) for t in todays_tasks)
    total_spent = sum(t.get("time_spent", 0) for t in todays_tasks)
    time_efficiency = (total_spent / total_estimated * 100) if total_estimated > 0 else 0
    
    # Display metrics
    st.markdown("### 📊 Today's Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tasks Completed", f"{completed_tasks}/{total_tasks}", 
                 delta=f"{completion_rate:.0f}%", 
                 delta_color="normal")
    
    with col2:
        if total_estimated > 0:
            st.metric("Time Efficiency", f"{time_efficiency:.0f}%", 
                     delta=f"{format_minutes_to_time(total_spent)} spent", 
                     delta_color="off")
        else:
            st.metric("Time Spent", format_minutes_to_time(total_spent))
    
    with col3:
        priority_counts = {
            "High": len([t for t in todays_tasks if t["priority"] == "High"]),
            "Medium": len([t for t in todays_tasks if t["priority"] == "Medium"]),
            "Low": len([t for t in todays_tasks if t["priority"] == "Low"])
        }
        st.metric("Priority Tasks", f"{priority_counts['High']} High", 
                 delta=f"{priority_counts['Medium']} Medium", 
                 delta_color="off")
    
    with col4:
        recurring_count = len([t for t in todays_tasks if t.get("is_recurring", False)])
        st.metric("Recurring Tasks", recurring_count)
    
    # Display tasks by priority
    st.markdown("### 📋 Today's Tasks")
    
    if not todays_tasks:
        st.markdown("""
        <div class="stCard" style="text-align: center; padding: 2rem;">
            <h3 style="color: #28A745; margin-bottom: 1rem;">🎉 No Tasks for Today!</h3>
            <p style="color: #6C757D; font-size: 1.1rem;">Excellent work! You've completed everything planned for today.</p>
            <p style="color: #6C757D; margin-top: 1rem;">Consider adding tasks for tomorrow or reviewing your analytics.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Create tabs for different priority levels
        tab1, tab2, tab3 = st.tabs(["🔴 High Priority", "🟡 Medium Priority", "🟢 Low Priority"])
        
        with tab1:
            high_pri_tasks = [t for t in todays_tasks if t["priority"] == "High"]
            if high_pri_tasks:
                for i, task in enumerate(high_pri_tasks, 1):
                    st.markdown(render_task_item(task, i), unsafe_allow_html=True)
                    
                    # Hidden button for task details (triggered by JavaScript)
                    st.button("Task Details", key=f"task-{task['id']}-details", 
                             on_click=lambda tid=task['id']: setattr(st.session_state, 'selected_task_id', tid) or setattr(st.session_state, 'show_task_details', True),
                             type="secondary", use_container_width=True)
            else:
                st.info("No high priority tasks for today")
        
        with tab2:
            med_pri_tasks = [t for t in todays_tasks if t["priority"] == "Medium"]
            if med_pri_tasks:
                for i, task in enumerate(med_pri_tasks, 1):
                    st.markdown(render_task_item(task, i), unsafe_allow_html=True)
                    
                    st.button("Task Details", key=f"task-{task['id']}-details", 
                             on_click=lambda tid=task['id']: setattr(st.session_state, 'selected_task_id', tid) or setattr(st.session_state, 'show_task_details', True),
                             type="secondary", use_container_width=True)
            else:
                st.info("No medium priority tasks for today")
        
        with tab3:
            low_pri_tasks = [t for t in todays_tasks if t["priority"] == "Low"]
            if low_pri_tasks:
                for i, task in enumerate(low_pri_tasks, 1):
                    st.markdown(render_task_item(task, i), unsafe_allow_html=True)
                    
                    st.button("Task Details", key=f"task-{task['id']}-details", 
                             on_click=lambda tid=task['id']: setattr(st.session_state, 'selected_task_id', tid) or setattr(st.session_state, 'show_task_details', True),
                             type="secondary", use_container_width=True)
            else:
                st.info("No low priority tasks for today")
    
    # Quick action buttons
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ Add New Task", use_container_width=True, type="primary"):
            st.session_state.show_add_task = True
            st.rerun()
    
    with col2:
        if st.button("⏱️ Start Timer", use_container_width=True, 
                    disabled=len([t for t in todays_tasks if not t.get("completed", False)]) == 0):
            st.session_state.show_timer_selector = True
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_tab = "Analytics"
            st.rerun()
    
    with col4:
        if st.button("📁 Task Archive", use_container_width=True):
            st.session_state.current_tab = "Archive"
            st.rerun()

def render_add_task_form():
    """Render the add task form"""
    st.markdown("### ➕ Add New Task")
    
    with st.form("add_task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_input("Task Description*", placeholder="Enter task description")
            
            category = st.selectbox("Category", 
                                  ["Work", "Personal", "Shopping", "Health", "Other"],
                                  index=1)
            
            priority = st.selectbox("Priority", 
                                  ["High", "Medium", "Low"],
                                  index=1,
                                  format_func=lambda x: {"High": "🔴 High Priority", 
                                                       "Medium": "🟡 Medium Priority", 
                                                       "Low": "🟢 Low Priority"}[x])
        
        with col2:
            col2_1, col2_2 = st.columns(2)
            
            with col2_1:
                estimated_time = st.text_input("Estimated Time", placeholder="e.g., 30m, 1h")
            
            with col2_2:
                max_time = st.text_input("Maximum Time", placeholder="e.g., 1h, 2h")
            
            is_recurring = st.checkbox("Recurring Task")
            
            if is_recurring:
                recurrence_pattern = st.selectbox("Recurrence Pattern", 
                                                 ["daily", "weekly", "monthly", "custom"],
                                                 format_func=lambda x: {"daily": "Daily", 
                                                                      "weekly": "Weekly", 
                                                                      "monthly": "Monthly", 
                                                                      "custom": "Custom Days"}[x])
                if recurrence_pattern == "custom":
                    custom_pattern = st.text_input("Custom Pattern", placeholder="e.g., mon,wed,fri")
            else:
                recurrence_pattern = ""
                custom_pattern = ""
            
            no_carryover = st.checkbox("Exclude from Carryover", 
                                     help="Task won't carry over to next day if incomplete")
        
        notes = st.text_area("Notes & Attachments", placeholder="Add notes or file paths (e.g., /projects/report.pdf)")
        
        # Subtasks section
        st.markdown("### ➕ Subtasks (Optional)")
        subtask_count = st.number_input("Number of subtasks", min_value=0, max_value=10, value=0)
        
        subtasks = []
        for i in range(subtask_count):
            subtask_desc = st.text_input(f"Subtask {i+1}", key=f"subtask_{i}")
            if subtask_desc:
                subtasks.append({
                    "id": i+1,
                    "description": subtask_desc,
                    "completed": False
                })
        
        submitted = st.form_submit_button("✅ Create Task", use_container_width=True)
        
        if submitted:
            if not description:
                st.error("Task description is required")
            else:
                full_pattern = custom_pattern if is_recurring and recurrence_pattern == "custom" else recurrence_pattern
                
                add_task(
                    description=description,
                    category=category,
                    priority=priority,
                    is_recurring=is_recurring,
                    recurrence_pattern=full_pattern,
                    notes=notes,
                    estimated_time=estimated_time,
                    max_time=max_time,
                    no_carryover=no_carryover,
                    subtasks=subtasks
                )
                save_data()
                st.session_state.show_add_task = False
                st.rerun()

def render_task_details(task_id):
    """Render task details view"""
    task = get_task_by_id(task_id)
    if not task:
        st.error("Task not found")
        return
    
    st.markdown(f"### 📝 Task Details: {task['description']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Category:** {task['category']}")
        st.markdown(f"**Priority:** {task['priority']}")
        st.markdown(f"**Due Date:** {task['due_date']}")
        st.markdown(f"**Status:** {'✅ Completed' if task.get('completed', False) else '⏳ Pending'}")
        
        if task.get("created_at"):
            created_date = datetime.fromisoformat(task["created_at"]).strftime("%B %d, %Y at %I:%M %p")
            st.markdown(f"**Created:** {created_date}")
        
        if task.get("completed_at"):
            completed_date = datetime.fromisoformat(task["completed_at"]).strftime("%B %d, %Y at %I:%M %p")
            st.markdown(f"**Completed:** {completed_date}")
        
        # Time tracking
        st.markdown("### ⏱️ Time Tracking")
        est_time = parse_time_to_minutes(task["estimated_time"])
        max_time = parse_time_to_minutes(task["max_time"])
        time_spent = task.get("time_spent", 0)
        
        col_time1, col_time2, col_time3 = st.columns(3)
        
        with col_time1:
            st.metric("Estimated Time", format_minutes_to_time(est_time))
        
        with col_time2:
            st.metric("Time Spent", format_minutes_to_time(time_spent))
        
        with col_time3:
            if est_time > 0:
                efficiency = (time_spent / est_time) * 100
                st.metric("Efficiency", f"{efficiency:.0f}%")
        
        # Progress bar
        if est_time > 0:
            progress = min(time_spent / est_time, 1.0)
            st.progress(progress)
            st.caption(f"{progress*100:.0f}% of estimated time used")
        
        # Time sessions
        if task.get("time_sessions"):
            st.markdown("**Time Sessions:**")
            sessions_df = pd.DataFrame(task["time_sessions"])
            if not sessions_df.empty:
                sessions_df['duration'] = sessions_df.get('duration', 0).apply(lambda x: format_minutes_to_time(int(x)))
                sessions_df['start_time'] = pd.to_datetime(sessions_df['start_time']).dt.strftime('%I:%M %p')
                if 'end_time' in sessions_df.columns:
                    sessions_df['end_time'] = pd.to_datetime(sessions_df['end_time']).dt.strftime('%I:%M %p')
                    sessions_df = sessions_df[['session_id', 'start_time', 'end_time', 'duration']]
                else:
                    sessions_df = sessions_df[['session_id', 'start_time', 'duration']]
                st.dataframe(sessions_df, use_container_width=True)
        
        # Notes
        st.markdown("### 📓 Notes")
        if task.get("notes"):
            st.markdown(task["notes"])
        else:
            st.info("No notes added")
    
    with col2:
        st.markdown("### 🔧 Actions")
        
        if not task.get("completed", False):
            if st.button("✅ Mark as Complete", use_container_width=True, type="primary"):
                complete_task(task_id)
                save_data()
                st.rerun()
            
            if st.button("⏱️ Start Timer", use_container_width=True, 
                        disabled=st.session_state.active_timer is not None):
                start_timer(task_id)
                save_data()
                st.rerun()
        
        if st.button("✏️ Edit Task", use_container_width=True):
            st.session_state.editing_task_id = task_id
            st.session_state.show_edit_task = True
            st.rerun()
        
        if st.button("🗑️ Delete Task", use_container_width=True, type="secondary"):
            st.session_state.confirm_delete_task_id = task_id
            st.rerun()
    
    # Subtasks section
    if task.get("subtasks"):
        st.markdown("### ✅ Subtasks")
        
        for subtask in task["subtasks"]:
            col_sub1, col_sub2 = st.columns([4, 1])
            
            with col_sub1:
                st.markdown(f"{'~~' if subtask.get('completed', False) else ''}{subtask['description']}{'~~' if subtask.get('completed', False) else ''}")
            
            with col_sub2:
                if not subtask.get("completed", False) and not task.get("completed", False):
                    if st.button("✓", key=f"complete_subtask_{subtask['id']}", use_container_width=True):
                        complete_subtask(task_id, subtask["id"])
                        save_data()
                        st.rerun()
        
        # Completion stats
        completed_subtasks = sum(1 for st in task["subtasks"] if st.get("completed", False))
        total_subtasks = len(task["subtasks"])
        st.progress(completed_subtasks / total_subtasks)
        st.caption(f"{completed_subtasks}/{total_subtasks} subtasks completed")

def render_analytics():
    """Render analytics and reports view"""
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<div class="header-title">📊 Analytics & Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Data-driven insights to optimize your productivity</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Daily Report", "📅 Weekly Trends", "🏷️ Category Analysis", "🎯 Estimation Accuracy"])
    
    with tab1:
        daily_report = generate_daily_report()
        if daily_report:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Tasks Completed", f"{daily_report['completed_tasks']}/{daily_report['total_tasks']}", 
                         delta=f"{daily_report['completion_rate']:.0f}%")
            
            with col2:
                st.metric("Estimated Time", format_minutes_to_time(daily_report['total_estimated']))
            
            with col3:
                st.metric("Actual Time", format_minutes_to_time(daily_report['total_actual']))
            
            with col4:
                st.metric("Efficiency", f"{daily_report['efficiency']:.0f}%", 
                         delta="on target" if 80 < daily_report['efficiency'] < 120 else "review estimates",
                         delta_color="normal")
            
            # Time comparison chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["Estimated", "Actual"],
                y=[daily_report['total_estimated'], daily_report['total_actual']],
                marker_color=['#4B55B2', '#2D9B76'],
                text=[format_minutes_to_time(daily_report['total_estimated']), 
                      format_minutes_to_time(daily_report['total_actual'])],
                textposition='auto',
            ))
            fig.update_layout(
                title="Time Comparison",
                xaxis_title="Time Type",
                yaxis_title="Minutes",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Task details
            st.markdown("### Task Details")
            for task in sorted(daily_report['tasks'], key=lambda x: x.get('time_spent', 0), reverse=True):
                with st.expander(f"{task['description']} - {format_minutes_to_time(task.get('time_spent', 0))} spent"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown(f"**Priority:** {task['priority']}")
                        st.markdown(f"**Category:** {task['category']}")
                        st.markdown(f"**Status:** {'✅ Completed' if task.get('completed', False) else '⏳ Pending'}")
                    
                    with col_b:
                        est_time = parse_time_to_minutes(task['estimated_time'])
                        act_time = task.get('time_spent', 0)
                        if est_time > 0:
                            efficiency = (act_time / est_time) * 100
                            st.markdown(f"**Efficiency:** {efficiency:.0f}%")
                            st.progress(min(efficiency/100, 1.0))
        else:
            st.info("No data available for today's report. Complete some tasks to generate insights.")
    
    with tab2:
        weekly_report = generate_weekly_report(7)
        if weekly_report['daily_data']:
            dates = list(weekly_report['daily_data'].keys())
            estimated = [data['estimated'] for data in weekly_report['daily_data'].values()]
            actual = [data['actual'] for data in weekly_report['daily_data'].values()]
            completion_rates = [data['completed']/data['tasks']*100 if data['tasks'] > 0 else 0 
                               for data in weekly_report['daily_data'].values()]
            
            # Create subplot with two y-axes
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add traces
            fig.add_trace(
                go.Bar(x=dates, y=estimated, name="Estimated Time", marker_color='#4B55B2'),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Bar(x=dates, y=actual, name="Actual Time", marker_color='#2D9B76'),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=dates, y=completion_rates, name="Completion Rate", 
                          mode='lines+markers', line=dict(color='#FFC107', width=3)),
                secondary_y=True,
            )
            
            # Set titles and layout
            fig.update_layout(
                title="Weekly Time Tracking & Completion Rates",
                xaxis_title="Date",
                height=400,
                barmode='group'
            )
            fig.update_yaxes(title_text="Minutes", secondary_y=False)
            fig.update_yaxes(title_text="Completion Rate (%)", secondary_y=True, range=[0, 100])
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_daily_tasks = weekly_report['total_tasks'] / 7
                st.metric("Avg Daily Tasks", f"{avg_daily_tasks:.1f}")
            
            with col2:
                total_est = weekly_report['total_estimated']
                total_act = weekly_report['total_actual']
                efficiency = (total_act / total_est * 100) if total_est > 0 else 0
                st.metric("Weekly Efficiency", f"{efficiency:.0f}%")
            
            with col3:
                completion_rate = (weekly_report['total_completed'] / weekly_report['total_tasks'] * 100) if weekly_report['total_tasks'] > 0 else 0
                st.metric("Task Completion", f"{completion_rate:.0f}%")
        else:
            st.info("No data available for weekly report. Track tasks for a week to generate insights.")
    
    with tab3:
        category_report = generate_category_report(30)
        if category_report['category_data']:
            categories = list(category_report['category_data'].keys())
            actual_times = [data['actual'] for data in category_report['category_data'].values()]
            estimated_times = [data['estimated'] for data in category_report['category_data'].values()]
            completion_rates = [data['completed']/data['tasks']*100 if data['tasks'] > 0 else 0 
                               for data in category_report['category_data'].values()]
            
            # Pie chart for time distribution
            fig = px.pie(
                values=actual_times,
                names=categories,
                title="Time Distribution by Category",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            # Bar chart for completion rates
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=categories,
                y=completion_rates,
                marker_color='#4B55B2',
                text=[f"{rate:.0f}%" for rate in completion_rates],
                textposition='auto',
            ))
            fig2.update_layout(
                title="Completion Rate by Category",
                xaxis_title="Category",
                yaxis_title="Completion Rate (%)",
                height=300,
                yaxis_range=[0, 100]
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Category table
            st.markdown("### Category Details")
            category_df = pd.DataFrame({
                "Category": categories,
                "Tasks": [data['tasks'] for data in category_report['category_data'].values()],
                "Completed": [data['completed'] for data in category_report['category_data'].values()],
                "Estimated Time": [format_minutes_to_time(data['estimated']) for data in category_report['category_data'].values()],
                "Actual Time": [format_minutes_to_time(data['actual']) for data in category_report['category_data'].values()],
                "Efficiency": [f"{(data['actual']/data['estimated']*100):.0f}%" if data['estimated'] > 0 else "N/A" 
                              for data in category_report['category_data'].values()]
            })
            st.dataframe(category_df, use_container_width=True)
        else:
            st.info("No category data available. Categorize your tasks to generate insights.")
    
    with tab4:
        st.markdown("### Coming Soon")
        st.info("Estimation accuracy analysis will be available in the next release. This report will help you improve your time estimates by analyzing patterns in your task completion times.")

def render_settings():
    """Render settings view"""
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<div class="header-title">⚙️ System Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Configure your TaskFlow experience</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Data management section
    st.markdown("### 💾 Data Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Data", use_container_width=True):
            save_data()
    
    with col2:
        if st.button("🔄 Load Data", use_container_width=True):
            load_data()
            st.success("Data loaded successfully")
    
    with col3:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.confirm_clear_data = True
    
    # Carryover settings
    st.markdown("### 🔄 Carryover Settings")
    
    max_carryovers = st.slider("Maximum carryovers per task", 
                              min_value=0, max_value=10, 
                              value=st.session_state.max_carryovers,
                              help="Number of times a task can be carried over before it's archived")
    
    if max_carryovers != st.session_state.max_carryovers:
        st.session_state.max_carryovers = max_carryovers
        save_data()
        st.success("Carryover settings updated")
    
    # Display current settings
    st.markdown("### 📋 Current Configuration")
    
    settings_df = pd.DataFrame({
        "Setting": ["Maximum Carryovers", "Last Carryover Date", "Total Tasks", "Active Timer"],
        "Value": [
            st.session_state.max_carryovers,
            st.session_state.last_carryover_date,
            len(st.session_state.tasks),
            "Yes" if st.session_state.active_timer else "No"
        ]
    })
    st.dataframe(settings_df, use_container_width=True)
    
    # Export/Import section
    st.markdown("### 📤 Export & Import")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Export Data", use_container_width=True):
            with open(DATA_FILE, 'r') as f:
                data = f.read()
            st.download_button(
                label="⬇️ Download JSON",
                data=data,
                file_name=f"taskflow_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("📤 Import Data", type=['json'])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                st.session_state.tasks = data.get("tasks", [])
                st.session_state.last_carryover_date = data.get("last_carryover_date", datetime.now().strftime("%Y-%m-%d"))
                st.session_state.max_carryovers = data.get("max_carryovers", 3)
                save_data()
                st.success("Data imported successfully")
            except Exception as e:
                st.error(f"Error importing data: {str(e)}")

def render_archive():
    """Render task archive view"""
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<div class="header-title">🗃️ Task Archive</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Review completed and historical tasks</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_filter = st.selectbox("Time Period", 
                                 ["Today", "This Week", "This Month", "All Time"],
                                 index=1)
    
    with col2:
        status_filter = st.selectbox("Task Status", 
                                   ["Completed", "Incomplete", "All"],
                                   index=0)
    
    with col3:
        category_filter = st.selectbox("Category", 
                                     ["All"] + list(set(t["category"] for t in st.session_state.tasks)),
                                     index=0)
    
    # Filter tasks
    cutoff_date = datetime.now().date()
    if days_filter == "Today":
        cutoff_date = datetime.now().date()
    elif days_filter == "This Week":
        cutoff_date = datetime.now().date() - timedelta(days=7)
    elif days_filter == "This Month":
        cutoff_date = datetime.now().date() - timedelta(days=30)
    
    filtered_tasks = []
    for task in st.session_state.tasks:
        task_date = datetime.fromisoformat(task["created_at"]).date() if "created_at" in task else datetime.now().date()
        
        if task_date < cutoff_date:
            continue
        
        if status_filter == "Completed" and not task.get("completed", False):
            continue
        
        if status_filter == "Incomplete" and task.get("completed", False):
            continue
        
        if category_filter != "All" and task["category"] != category_filter:
            continue
        
        filtered_tasks.append(task)
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tasks", len(filtered_tasks))
    
    with col2:
        completed = sum(1 for t in filtered_tasks if t.get("completed", False))
        st.metric("Completed", completed)
    
    with col3:
        completion_rate = (completed / len(filtered_tasks) * 100) if filtered_tasks else 0
        st.metric("Completion Rate", f"{completion_rate:.0f}%")
    
    # Display tasks
    if filtered_tasks:
        # Sort by completion date or creation date
        sort_by = st.radio("Sort by", ["Completion Date", "Creation Date", "Priority"], 
                          horizontal=True, index=0)
        
        if sort_by == "Completion Date":
            filtered_tasks.sort(key=lambda x: x.get("completed_at", x.get("created_at", "")), reverse=True)
        elif sort_by == "Creation Date":
            filtered_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_by == "Priority":
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            filtered_tasks.sort(key=lambda x: (priority_order.get(x["priority"], 1), x.get("created_at", "")), reverse=True)
        
        # Pagination
        tasks_per_page = 10
        total_pages = max(1, (len(filtered_tasks) + tasks_per_page - 1) // tasks_per_page)
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page - 1) * tasks_per_page
        end_idx = min(start_idx + tasks_per_page, len(filtered_tasks))
        
        for i, task in enumerate(filtered_tasks[start_idx:end_idx], start_idx + 1):
            st.markdown(render_task_item(task, i), unsafe_allow_html=True)
            
            if st.button("📋 Details", key=f"archive_task_{task['id']}", use_container_width=True):
                st.session_state.selected_task_id = task['id']
                st.session_state.show_task_details = True
                st.rerun()
    else:
        st.info("No tasks match the current filters. Try adjusting your filters to see more tasks.")

def main():
    """Main application logic"""
    # Initialize session state variables
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "Dashboard"
    if 'show_add_task' not in st.session_state:
        st.session_state.show_add_task = False
    if 'show_task_details' not in st.session_state:
        st.session_state.show_task_details = False
    if 'selected_task_id' not in st.session_state:
        st.session_state.selected_task_id = None
    if 'show_edit_task' not in st.session_state:
        st.session_state.show_edit_task = False
    if 'editing_task_id' not in st.session_state:
        st.session_state.editing_task_id = None
    if 'confirm_delete_task_id' not in st.session_state:
        st.session_state.confirm_delete_task_id = None
    if 'confirm_clear_data' not in st.session_state:
        st.session_state.confirm_clear_data = False
    if 'show_timer_selector' not in st.session_state:
        st.session_state.show_timer_selector = False
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        if st.button("🏠 Dashboard", use_container_width=True, 
                    type="primary" if st.session_state.current_tab == "Dashboard" else "secondary"):
            st.session_state.current_tab = "Dashboard"
            st.session_state.show_add_task = False
            st.session_state.show_task_details = False
            st.session_state.show_edit_task = False
            st.session_state.show_timer_selector = False
            st.rerun()
        
        if st.button("📊 Analytics", use_container_width=True, 
                    type="primary" if st.session_state.current_tab == "Analytics" else "secondary"):
            st.session_state.current_tab = "Analytics"
            st.session_state.show_add_task = False
            st.session_state.show_task_details = False
            st.session_state.show_edit_task = False
            st.session_state.show_timer_selector = False
            st.rerun()
        
        if st.button("🗃️ Archive", use_container_width=True, 
                    type="primary" if st.session_state.current_tab == "Archive" else "secondary"):
            st.session_state.current_tab = "Archive"
            st.session_state.show_add_task = False
            st.session_state.show_task_details = False
            st.session_state.show_edit_task = False
            st.session_state.show_timer_selector = False
            st.rerun()
        
        if st.button("⚙️ Settings", use_container_width=True, 
                    type="primary" if st.session_state.current_tab == "Settings" else "secondary"):
            st.session_state.current_tab = "Settings"
            st.session_state.show_add_task = False
            st.session_state.show_task_details = False
            st.session_state.show_edit_task = False
            st.session_state.show_timer_selector = False
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("➕ Add New Task", use_container_width=True):
            st.session_state.show_add_task = True
            st.session_state.current_tab = "Dashboard"
            st.rerun()
        
        if st.button("⏱️ Time Tracking", use_container_width=True):
            st.session_state.show_timer_selector = True
            st.session_state.current_tab = "Dashboard"
            st.rerun()
    
    # Display notifications and active timer
    display_notifications()
    display_active_timer()
    
    # Main content area
    if st.session_state.show_add_task:
        render_add_task_form()
    elif st.session_state.show_task_details and st.session_state.selected_task_id:
        render_task_details(st.session_state.selected_task_id)
    elif st.session_state.show_edit_task and st.session_state.editing_task_id:
        st.warning("Task editing is not fully implemented in this demo version")
        if st.button("← Back to Dashboard"):
            st.session_state.show_edit_task = False
            st.session_state.current_tab = "Dashboard"
            st.rerun()
    elif st.session_state.confirm_delete_task_id:
        task = get_task_by_id(st.session_state.confirm_delete_task_id)
        st.warning(f"Are you sure you want to delete the task '{task['description']}'?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", use_container_width=True):
                st.session_state.tasks = [t for t in st.session_state.tasks if t["id"] != st.session_state.confirm_delete_task_id]
                save_data()
                add_notification(f"Task '{task['description']}' deleted", "success")
                st.session_state.confirm_delete_task_id = None
                st.rerun()
        with col2:
            if st.button("❌ No, Cancel", use_container_width=True):
                st.session_state.confirm_delete_task_id = None
                st.rerun()
    elif st.session_state.confirm_clear_data:
        st.warning("⚠️ This will delete ALL your tasks and data. This action cannot be undone!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Clear All Data", use_container_width=True):
                st.session_state.tasks = []
                st.session_state.last_carryover_date = datetime.now().strftime("%Y-%m-%d")
                st.session_state.max_carryovers = 3
                save_data()
                add_notification("All data cleared successfully", "success")
                st.session_state.confirm_clear_data = False
                st.rerun()
        with col2:
            if st.button("❌ No, Cancel", use_container_width=True):
                st.session_state.confirm_clear_data = False
                st.rerun()
    elif st.session_state.show_timer_selector:
        st.markdown("### ⏱️ Select Task to Time")
        todays_tasks = get_todays_tasks()
        incomplete_tasks = [t for t in todays_tasks if not t.get("completed", False)]
        
        if incomplete_tasks:
            for task in incomplete_tasks:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{task['description']}**")
                    st.caption(f"{task['category']} • {task['priority']} priority")
                with col2:
                    if st.button("▶️ Start", key=f"timer_{task['id']}", use_container_width=True):
                        start_timer(task["id"])
                        save_data()
                        st.session_state.show_timer_selector = False
                        st.rerun()
        else:
            st.info("No incomplete tasks available for timing today.")
        
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.show_timer_selector = False
            st.rerun()
    else:
        # Render the current tab
        if st.session_state.current_tab == "Dashboard":
            render_dashboard()
        elif st.session_state.current_tab == "Analytics":
            render_analytics()
        elif st.session_state.current_tab == "Archive":
            render_archive()
        elif st.session_state.current_tab == "Settings":
            render_settings()

if __name__ == "__main__":
    main()