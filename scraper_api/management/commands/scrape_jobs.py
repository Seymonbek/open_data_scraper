import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from scraper_api.models import Job
from datetime import datetime


class Command(BaseCommand):
    help = "remoteok.com saytidan ish e'lonlarini JSON formatda olib, ularni bazaga saqlash jarayoni"

    def handle(self, *args, **kwargs):
        url = "https://remoteok.com/remote-jobs.json"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Ma'lumot olib bo'lmadi: {e}"))
            return

        try:
            jobs = response.json()
        except ValueError:
            self.stdout.write(self.style.ERROR("JSON formatdagi javobni o'qishda xatolik yuz berdi"))
            return

        if isinstance(jobs, list) and jobs  :
            first = jobs[0]
            if "id" not in first:
                jobs = jobs[1:]

        count = 0
        for job in jobs:
            try:
                title = job.get("position") or job.get("title")
                if not title:
                    self.stdout.write(self.style.WARNING(f"Sarlavhasi yo‘q bo‘lgan ish e’loni o‘tkazib yuborildi: {job.get('id')}"))
                    continue

                company = job.get("company")
                job_id = job.get("id")
                link = f"https://remoteok.com/{job_id}"

                posted_at_str = job.get("date")
                posted_at = None
                if posted_at_str:
                    posted_at = datetime.fromisoformat(
                        posted_at_str.replace("Z", "+00:00")
                    )

                description_html = job.get("description") or ""
                soup = BeautifulSoup(description_html, "html.parser")
                description_text = soup.get_text(" ", strip=True)

                obj, created = Job.objects.update_or_create(
                    url=link,
                    defaults={
                        "title": title,
                        "company": company,
                        "posted_at": posted_at,
                        "description": description_text,
                        "scraped_at": datetime.now(),
                    },
                )

                if created:
                    count += 1

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Ish e’lonini tahlil qilishda xatolik yuz berdi: {e}"))
                continue

        self.stdout.write(
            self.style.SUCCESS(f"Ma'lumot yig‘ish yakunlandi. {count} ta yangi ish e’loni qo‘shildi.")
        )
