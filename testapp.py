import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from redis.asyncio import Redis


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
redis_client = Redis(
    host='localhost',
    port=6379, 
    db=0, 
    decode_responses=True 
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

popular_cities = {'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Нижний Новгород', 'Красноярск', 'Челябинск', 'Самара', 'Уфа', 'Ростов-на-Дону', 'Краснодар', 'Омск', 'Воронеж', 'Пермь', 'Волгоград', 'Саратов', 'Тюмень', 'Тольятти', 'Барнаул', 'Махачкала', 'Ижевск', 'Хабаровск', 'Ульяновск', 'Иркутск', 'Владивосток', 'Ярославль', 'Севастополь', 'Томск', 'Ставрополь', 'Кемерово', 'Набережные Челны', 'Оренбург', 'Новокузнецк', 'Балашиха', 'Рязань', 'Чебоксары', 'Пенза', 'Липецк', 'Калининград', 'Киров', 'Астрахань', 'Тула', 'Сочи', 'Улан-Удэ', 'Курск', 'Тверь', 'Магнитогорск', 'Сургут', 'Брянск', 'Якутск', 'Иваново', 'Владимир', 'Симферополь', 'Нижний Тагил', 'Калуга', 'Белгород', 'Чита', 'Грозный', 'Волжский', 'Смоленск', 'Подольск', 'Саранск', 'Вологда', 'Курган', 'Череповец', 'Архангельск', 'Орёл', 'Владикавказ', 'Нижневартовск', 'Йошкар-Ола', 'Стерлитамак', 'Мурманск', 'Мытищи', 'Кострома', 'Новороссийск', 'Тамбов', 'Химки', 'Нальчик', 'Таганрог', 'Нижнекамск', 'Благовещенск', 'Комсомольск-на-Амуре', 'Петрозаводск', 'Люберцы', 'Королёв', 'Энгельс', 'Великий Новгород', 'Шахты', 'Братск', 'Сыктывкар', 'Ангарск', 'Старый Оскол', 'Дзержинск', 'Псков', 'Красногорск', 'Орск', 'Одинцово', 'Абакан', 'Армавир', 'Балаково', 'Бийск', 'Южно-Сахалинск', 'Уссурийск', 'Прокопьевск', 'Норильск', 'Рыбинск', 'Волгодонск', 'Альметьевск', 'Сызрань', 'Петропавловск-Камчатский', 'Каменск-Уральский', 'Новочеркасск', 'Златоуст', 'Хасавюрт', 'Северодвинск', 'Домодедово', 'Керчь', 'Миасс', 'Салават', 'Копейск', 'Пятигорск', 'Электросталь', 'Майкоп', 'Находка', 'Березники', 'Щёлково', 'Серпухов', 'Нефтекамск', 'Коломна', 'Ковров', 'Обнинск', 'Кызыл', 'Кисловодск', 'Дербент', 'Каспийск', 'Батайск', 'Нефтеюганск', 'Рубцовск', 'Назрань', 'Ессентуки', 'Новочебоксарск', 'Долгопрудный', 'Новомосковск', 'Октябрьский', 'Невинномысск', 'Раменское', 'Реутов', 'Первоуральск', 'Михайловск', 'Черкесск', 'Пушкино', 'Жуковский', 'Ханты-Мансийск', 'Димитровград', 'Артём', 'Новый Уренгой', 'Евпатория', 'Муром', 'Северск', 'Орехово-Зуево', 'Камышин', 'Мурино', 'Арзамас', 'Видное', 'Бердск', 'Элиста', 'Ногинск', 'Новошахтинск', 'Ноябрьск'}

@app.get("/search_cities", response_class=JSONResponse)
async def search_cities(query: str):

    cities_data = await redis_client.lrange('cities', 0, -1)

    def split_and_check(city_data):
        split_data = city_data.split(',')
        if split_data[0].strip() in popular_cities:
            return city_data
        return None

    starts_with_query = [city_data for city_data in cities_data if city_data.lower().startswith(query.lower())]

    popular_matches = [split_and_check(city_data) for city_data in starts_with_query if split_and_check(city_data) is not None]

    other_matches = [city_data for city_data in starts_with_query if city_data.lower().startswith(query.lower()) and split_and_check(city_data) is None]

    filtered_cities = popular_matches[::-1] + other_matches

    return JSONResponse(content={"data": filtered_cities[:5]})

@app.post("/webhook/contract")
async def process_contract_data(redis: Redis, userId: str, data: dict):
    try:
        await redis.lpush(f'invoice_step1_{userId}', data)
        return 200
    except Exception as e:
        raise 500
