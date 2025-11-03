# MarketsStatus Telegram Bot

A small Telegram bot helper that reports the open/close status of major international stock markets and the time remaining until they open or close.

## Requirements
- Python 3.9+ recommended
- pip

On Windows, time zone data comes from the `tzdata` package.

## Installation
1. Create/activate your virtual environment (optional but recommended).
2. Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   If your Python is 3.9+ on Windows and you see time zone issues, ensure `tzdata` is installed:
   ```bash
   pip install tzdata
   ```

## Configuration
Create a `.env` file in the project root with your Telegram Bot token:
```
BOT_TOKEN=123456789:ABCDEF_your_real_token_here
```

## Run
Start your bot process as you normally would. For a simple run from this folder:
```bash
python MarketsStatis.py
```

> Note: The bot uses `telebot.AsyncTeleBot`. Ensure your runtime integrates the bot into an async loop/polling mechanism if needed by your setup.

## Main Function: `markets_status`
- Input: optional language code (`"en"` or `"es"`, defaults to English).
- Logic:
  - Defines a set of markets (US, Switzerland, Hong Kong, Japan, UK, Germany, UAE, Russia, India, Australia) with their IANA time zones and trading sessions.
  - Uses `zoneinfo` (and `tzdata` on Windows) to compute local times per market.
  - Skips weekends and common national holidays (via the `holidays` package) when computing business days.
  - For each market, determines whether it is currently open or closed and calculates the remaining time until close (if open) or until the next open (if closed).
- Output: a formatted, multi-line string headed by “International market status” (or Spanish equivalent) suitable for sending as a Telegram message.

## Telegram Command
- `/markets` — replies with the formatted status text returned by `markets_status` in the user’s language (English or Spanish).
