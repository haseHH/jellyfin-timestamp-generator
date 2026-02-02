import os
import requests
import math
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.templating import Jinja2Templates

jellyfin_address = os.getenv('JF_ADDRESS', 'NONE')
url = f'{jellyfin_address}/Sessions?ActiveWithinSeconds=600'

jellyfin_api_key = os.getenv('JF_API_KEY', 'NONE')
auth = {'Authorization': f'MediaBrowser Token="{jellyfin_api_key}"'}

app = FastAPI(
    title='Jellyfin Timestamp Generator',
)
templates = Jinja2Templates(directory='templates', autoescape=False)

ticks_per_sec = 10000000
ticks_per_min = ticks_per_sec * 60
ticks_per_hour = ticks_per_min * 60

#region functions
def get_sessions():
    r = requests.get(url, headers=auth)
    return r.json()

def get_user_session(user: str):
    for session in get_sessions():
        if (session['UserName'] == user):
            return session

def get_timestamp_from_ticks(ticks: int, force_hour: bool):
    if (ticks > ticks_per_hour):
        force_hour = True

    total_seconds = math.floor(ticks / ticks_per_sec)
    total_minutes = math.floor(total_seconds / 60)
    if (force_hour):
        total_hours = math.floor(total_minutes / 60)

    display_seconds = str(total_seconds - (total_minutes * 60))
    if (force_hour):
        display_minutes = str(total_minutes - (total_hours * 60))
        display_hours = str(total_hours)
        timestamp = f'{display_hours}:{display_minutes.rjust(2, '0')}:{display_seconds.rjust(2, '0')}'
    else:
        display_minutes = str(total_minutes)
        timestamp = f'{display_minutes.rjust(2, '0')}:{display_seconds.rjust(2, '0')}'

    return timestamp
#endregion functions

#region misc_pages
@app.get('/favicon.ico', status_code=status.HTTP_404_NOT_FOUND)
def favicon():
    return '404'

@app.get('/')
@app.get('/info')
def info(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='info.html',
        context={'title': app.title},
    )
#endregion misc_pages

#region main_pages
@app.get('/api/session/{user}')
def parse_session(user: str, force_hour: bool = False):
    user_session = get_user_session(user)
    if (user_session is None):
        return JSONResponse(
            content={'error': f'No session found for user \'{user}\'.'},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if user_session.get('PlayState', {}).get('IsPaused', True):
        play_pause_symbol = '⏸'
    else:
        play_pause_symbol = '▶'

    current_ticks = user_session.get('PlayState', {}).get('PositionTicks', 0)
    total_ticks = user_session.get('NowPlayingItem', {}).get('RunTimeTicks', 0)
    remaining_ticks = total_ticks - current_ticks

    include_hour = force_hour or (total_ticks >= ticks_per_hour)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'play_state': play_pause_symbol,
            'current': get_timestamp_from_ticks(current_ticks, include_hour),
            'total': get_timestamp_from_ticks(total_ticks, include_hour),
            'remaining': get_timestamp_from_ticks(remaining_ticks, include_hour),
        },
    )

@app.get('/session/{user}')
def render_formatted_timer(
        request: Request,
        user: str,
        force_hour: bool = False,
        format: str = f'%p%s%s%c%s/%s%t%s%s-%r',
        font: str = 'Arial',
        font_size: str = '40px',
        text_color: str = 'black',
        outline_color: str = 'white',
        outline_width: str = '0px',
    ):
    session_response = parse_session(user, force_hour)

    if (session_response.status_code != status.HTTP_200_OK):
        return templates.TemplateResponse(
            request=request,
            name='formatted.html',
            context={
                'title': app.title,
                'content': f'<code>{json.loads(session_response.body)}</code>',
                'refresh_time': 5,
                'font': font,
                'font_size': font_size,
                'text_color': text_color,
                'outline_color': outline_color,
                'outline_width': outline_width,
            },
            status_code=session_response.status_code
        )

    session = json.loads(session_response.body)
    format = format.replace(f'%p', session['play_state'])
    format = format.replace(f'%c', session['current'])
    format = format.replace(f'%t', session['total'])
    format = format.replace(f'%r', session['remaining'])
    format = format.replace(f'%s', '&nbsp;')

    return templates.TemplateResponse(
        request=request,
        name='formatted.html',
        context={
            'title': app.title,
            'content': format,
            'font': font,
            'font_size': font_size,
            'text_color': text_color,
            'outline_color': outline_color,
            'outline_width': outline_width,
        },
    )
#endregion main_pages
