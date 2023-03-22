import requests
from bs4 import BeautifulSoup
import telegram
import asyncio


async def get_indeed_jobs():
    url = 'https://www.indeed.com.br/empregos-em-Maca%C3%A9,-RJ'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    job_listings = soup.find_all('div', class_='jobsearch-SerpJobCard unifiedRow row result')

    jobs = []
    for job_listing in job_listings:
        title = job_listing.find('h2', class_='title').text.strip()
        company = job_listing.find('span', class_='company').text.strip()
        location = job_listing.find('span', class_='location').text.strip()
        link = 'https://www.indeed.com.br' + job_listing.find('a')['href']
        job = f"{title}\n{company}\n{location}\n{link}\n"
        jobs.append(job)

    return jobs


async def get_linkedin_jobs():
    url = 'https://www.linkedin.com/jobs/search/?keywords=&location=Maca%C3%A9%2C%20Rio%20de%20Janeiro%2C%20Brasil&geoId=104076686&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    job_listings = soup.find_all('li', class_='result-card job-result-card result-card--with-hover-state')

    jobs = []
    for job_listing in job_listings:
        title = job_listing.find('h3', class_='result-card__title').text.strip()
        company = job_listing.find('a', class_='result-card__subtitle-link job-result-card__subtitle-link').text.strip()
        location = job_listing.find('span', class_='job-result-card__location').text.strip()
        link = job_listing.find('a', class_='result-card__full-card-link')['href']
        job = f"{title}\n{company}\n{location}\n{link}\n"
        jobs.append(job)

    return jobs


async def send_telegram_message(token, chat_id, message):
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)


async def main():
    token = '5701982262:AAEEnZXQr1Z_fdMsGzqLyVhQ5okMNrmi5t4'
    chat_id = '-1001579445015_683'
    db_path = 'db.txt'

    try:
        with open(db_path, 'r') as f:
            db = f.read().splitlines()
    except FileNotFoundError:
        db = []

    indeed_jobs = await get_indeed_jobs()
    linkedin_jobs = await get_linkedin_jobs()

    new_jobs = [job for job in indeed_jobs + linkedin_jobs if job not in db]

    if new_jobs:
        message = '\n\n'.join(new_jobs)
        await send_telegram_message(token, chat_id, message)
        print(f'{len(new_jobs)} nova(s) vaga(s) encontrada(s)')
        db += new_jobs
        with open(db_path, 'w') as f:
            f.write('\n'.join(db))
    else:
        await send_telegram_message(token, chat_id, 'Sem vagas no momento')
        print('Sem novas vagas')


if __name__ == '__main__':
    asyncio.run(main())
