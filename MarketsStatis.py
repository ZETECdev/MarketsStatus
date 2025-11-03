from os import getenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telebot import AsyncTeleBot
from zoneinfo import ZoneInfo
import holidays as hol

bot = AsyncTeleBot(getenv('BOT_TOKEN', parse_mode='HTML'))


async def markets_status(lang: str = 'en'):
    markets_data_txt = ''
    lang_in = (lang or 'es').strip().lower()
    if 'en' in lang_in:
        lang_norm = 'en'
    elif 'es' in lang_in:
        lang_norm = 'es'
    else:
        lang_norm = 'es'
    markets_data = {
        'us': {
            'loc': {'en': 'USA', 'es': 'USA'},
            'sessions': [ {'open': '09:30', 'close': '16:00'} ],
            'flag': '🇺🇸', 'tz': 'America/New_York', 'cc': 'US'
        },
        'ch': {
            'loc': {'en': 'Switzerland', 'es': 'Suiza'},
            'sessions': [ {'open': '09:00', 'close': '17:30'} ],
            'flag': '🇨🇭', 'tz': 'Europe/Zurich', 'cc': 'CH'
        }, 
        'hk': {
            'loc': {'en': 'Hong Kong', 'es': 'Hong Kong'},
            'sessions': [ {'open': '09:30', 'close': '12:00'}, {'open': '13:00', 'close': '16:00'} ],
            'flag': '🇨🇳', 'tz': 'Asia/Hong_Kong', 'cc': 'HK'
        },
        'jp': {
            'loc': {'en': 'Japan', 'es': 'Japón'},
            'sessions': [ {'open': '09:00', 'close': '11:30'}, {'open': '12:30', 'close': '15:00'} ],
            'flag': '🇯🇵', 'tz': 'Asia/Tokyo', 'cc': 'JP'
        },
        'uk': {
            'loc': {'en': 'England', 'es': 'Inglaterra'},
            'sessions': [ {'open': '08:00', 'close': '16:30'} ],
            'flag': '🇬🇧', 'tz': 'Europe/London', 'cc': 'GB'
        },
        'de': {
            'loc': {'en': 'Germany', 'es': 'Alemania'},
            'sessions': [ {'open': '09:00', 'close': '17:30'} ],
            'flag': '🇩🇪', 'tz': 'Europe/Berlin', 'cc': 'DE'
        },
        'ae': {
            'loc': {'en': 'Dubai', 'es': 'Dubai'},
            'sessions': [ {'open': '10:00', 'close': '15:00'} ],
            'flag': '🇦🇪', 'tz': 'Asia/Dubai', 'cc': 'AE'
        },
        'ru': {
            'loc': {'en': 'Russia', 'es': 'Rusia'},
            'sessions': [ {'open': '09:50', 'close': '18:39'} ],
            'flag': '🇷🇺', 'tz': 'Europe/Moscow', 'cc': 'RU'
        },
        'in': {
            'loc': {'en': 'India', 'es': 'India'},
            'sessions': [ {'open': '09:15', 'close': '15:30'} ],
            'flag': '🇮🇳', 'tz': 'Asia/Kolkata', 'cc': 'IN'
        },
        'au': {
            'loc': {'en': 'Australia', 'es': 'Australia'},
            'sessions': [ {'open': '10:00', 'close': '16:00'} ],
            'flag': '🇦🇺', 'tz': 'Australia/Sydney', 'cc': 'AU'
        }
    }

    def is_holiday(date_local, country_code):
        if hol is None:
            return False
        try:
            hd = hol.country_holidays(country_code, years=[date_local.year, date_local.year + 1])
            return date_local in hd
        except Exception:
            return False

    def is_business_day(date_local, country_code):
        if date_local.weekday() >= 5:
            return False
        if is_holiday(date_local, country_code):
            return False
        return True

    def next_business_date(date_local, country_code):
        d = 0
        candidate = date_local
        while True:
            d += 1
            candidate = date_local + timedelta(days=d)
            if is_business_day(candidate, country_code):
                return candidate

    for market in markets_data.values():
        tz = ZoneInfo(market['tz'])
        now_local = datetime.now(tz)

        today_sessions = []
        for s in market['sessions']:
            o_t = datetime.strptime(s['open'], '%H:%M').time()
            c_t = datetime.strptime(s['close'], '%H:%M').time()
            o_dt = datetime.combine(now_local.date(), o_t, tz)
            c_dt = datetime.combine(now_local.date(), c_t, tz)
            today_sessions.append((o_dt, c_dt))

        def first_session_open_on(date_obj):
            o_t0 = datetime.strptime(market['sessions'][0]['open'], '%H:%M').time()
            return datetime.combine(date_obj, o_t0, tz)

        status = 'closed'
        time_left_str = ''

        if not is_business_day(now_local.date(), market['cc']):
            next_date = next_business_date(now_local.date(), market['cc'])
            next_open_dt = first_session_open_on(next_date)
            delta = next_open_dt - now_local
            time_left_str = f"{delta.days}D, {delta.seconds // 3600}H, {(delta.seconds // 60) % 60}Min"
        else:
            in_session = False
            for (o_dt, c_dt) in today_sessions:
                if o_dt <= now_local < c_dt:
                    in_session = True
                    status = 'open'
                    delta = c_dt - now_local
                    hours = delta.seconds // 3600
                    minutes = (delta.seconds // 60) % 60
                    time_left_str = f"{hours}H, {minutes}Min"
                    break

            if not in_session:
                upcoming = [(o_dt, c_dt) for (o_dt, c_dt) in today_sessions if now_local < o_dt]
                if len(upcoming) > 0:
                    next_open_dt = sorted(upcoming, key=lambda x: x[0])[0][0]
                    delta = next_open_dt - now_local
                    days = delta.days
                    hours = delta.seconds // 3600
                    minutes = (delta.seconds // 60) % 60
                    time_left_str = f"{days}D, {hours}H, {minutes}Min" if days > 0 else f"{hours}H, {minutes}Min"
                else:
                    next_date = next_business_date(now_local.date(), market['cc'])
                    next_open_dt = first_session_open_on(next_date)
                    delta = next_open_dt - now_local
                    days = delta.days
                    hours = delta.seconds // 3600
                    minutes = (delta.seconds // 60) % 60
                    time_left_str = f"{days}D, {hours}H, {minutes}Min" if days > 0 else f"{hours}H, {minutes}Min"
        name_loc = market['loc'].get(lang_norm, market['loc']['en'])
        if status == 'closed':
            label = '❌ <i>Abre en</i>' if lang_norm == 'es' else '❌ <i>Opens in</i>'
        else:
            label = '✅ <i>Cierra en</i>' if lang_norm == 'es' else '✅ <i>Closes in</i>'
        markets_data_txt += f"\n{market['flag']} <b>{name_loc}</b>: {label} {time_left_str}"
    header = '🌏 <i>Estado mercados internacionales</i>' if lang_norm == 'es' else '🌏 <i>International market status</i>'
    return header + '\n' + markets_data_txt



@bot.message_handler(commands=['markets'])
async def markets(ctx):
    lang = 'es' if ctx.from_user.language_code == 'es' else 'en'
    try:
        markets_msg = await markets_status(lang)
        await bot.send_message(ctx.chat.id, markets_msg)
    except Exception as e:
        await bot.send_message(ctx.chat.id, '⚠️ ERROR: ' + str(e))


bot.infinity_polling()
        