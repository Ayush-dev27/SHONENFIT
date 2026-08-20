# SHONENFIT - Project State & Architecture

## Core Roster (9 Characters Complete)
- Demon Slayer: Tanjiro, Inosuke, Tengen
- Jujutsu Kaisen: Toji, Maki, Yuji
- My Hero Academia: Deku, Bakugo, All Might

## Live Features & Architecture
- **Backend:** Flask (`app.py`), SQLite (`shonenfit.db`), Python (`generator.py`)
- **Gamification:** Rank Tiers (Grade 4, Grade 3, etc.), EXP accumulation (+250 EXP per arc)
- **Analytics:** System Fatigue Analyzer, Training Timeline, Streak Tracking
- **Workout Engine:**
  - Dynamic Set Parsing (RegEx extracts target set counts for button generation)
  - Recovery Lock System (prevents double-logging on active training days)
  - Recovery UI (`.recovery-btn` full-width action pills for time/restoration protocols)

## Database Schema Highlights
- `workout_logs`: Stores completed sessions with timestamp, sets logged, character key, and EXP earned.
- `user_profile`: Tracks total accumulated EXP, active rank tier, and active training arc streak. 