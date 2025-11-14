# TaskFlow Professional ✨

A professional task management and time tracking application built with Streamlit. Combines intuitive task organization with powerful analytics to optimize your productivity.

## 🚀 Key Features

- **Smart Task Carryover**: Incomplete tasks automatically carry over to the next day with configurable limits
- **Priority System**: Visual indicators for High (🔴), Medium (🟡), and Low (🟢) priority tasks
- **Time Tracking**: Real-time timer with session history and efficiency metrics
- **Analytics Dashboard**: Daily reports, weekly trends, and category analysis
- **Nested Subtasks**: Hierarchical task structures with independent completion tracking
- **Recurring Tasks**: Daily, weekly, monthly, or custom patterns (e.g., "mon,wed,fri")
- **Time Estimates**: Set estimated and max time per task — track actual vs planned
- **Export/Import**: Save or restore your task data as JSON

## ⚙️ Installation

```bash
# Install dependencies
pip install streamlit plotly pandas numpy

# Run the app
streamlit run taskflow_app.py