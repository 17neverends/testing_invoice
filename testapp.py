from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from redis.asyncio import Redis
import aiohttp
from bs4 import BeautifulSoup
import re


async def get_top_cities(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Ошибка {response.status}. Не удалось получить доступ к странице.")
                return []
            soup = BeautifulSoup(await response.text(), 'html.parser')
            table = soup.find('table')
            cities = []
            for row in table.find_all('tr'):
                cells = row.find_all(['td'])
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    if any(char.isalpha() for char in cell_text):
                        cell_text_cleaned = re.sub(r'\[.*?\]', '', cell_text).strip()
                        cities.append(cell_text_cleaned)
            return cities



app = FastAPI()
templates = Jinja2Templates(directory="templates")
redis_client = Redis(
    host='localhost',
    port=6379, 
    db=0, 
    decode_responses=True 
)

@app.get("/calculate_invoice", response_class=HTMLResponse)
async def calculate_invoice_step1(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/get_cities", response_class=JSONResponse)
async def get_cities():
    data = await redis_client.lrange('cities', 0, -1)
    return JSONResponse(content={"data": data})

@app.get("/get_wiki_cities", response_class=JSONResponse)
async def get_wiki_cities():
    cities_data = await get_top_cities('https://ru.wikipedia.org/wiki/Список_городов_России_с_населением_более_100_тысяч_жителей')
    return JSONResponse(content={"data": cities_data})