from __future__ import annotations

import random
import re
from datetime import datetime, timedelta, timezone

from faker import Faker

CATEGORIES = [
    "Plumbing", "Electrical", "HVAC", "Roofing", "Landscaping",
    "Accounting", "Legal Services", "IT Services", "Marketing",
    "Construction", "Cleaning Services", "Auto Repair",
    "Real Estate", "Insurance", "Financial Services",
    "Consulting", "Architecture", "Engineering", "Printing", "Catering",
]

SOURCE_TEMPLATES = [
    "yellowpages", "yelp", "bbb", "clutch", "google_maps",
]

PHONE_FORMATS = [
    "({area}) {prefix}-{line}",
    "{area}-{prefix}-{line}",
    "+1{area}{prefix}{line}",
    "{area}{prefix}{line}",
]


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def seed_demo(count: int = 200, sources: int = 3, seed: int | None = None) -> list[dict]:
    fake = Faker("en_US")
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)

    source_names = SOURCE_TEMPLATES[:sources]
    now = datetime.now(timezone.utc)
    records = []

    for i in range(count):
        company = fake.company()
        slug = _slugify(company)
        area = str(random.randint(201, 999))
        prefix = str(random.randint(200, 999))
        line = str(random.randint(1000, 9999))
        fmt = random.choice(PHONE_FORMATS)
        phone = fmt.format(area=area, prefix=prefix, line=line)

        domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", f"{slug[:20]}.com"])
        email = f"contact@{domain}" if random.random() > 0.3 else f"{slug[:10]}@{domain}"

        source = source_names[i % len(source_names)]
        scraped_at = (now - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))).isoformat()

        records.append({
            "company_name": company,
            "phone": phone,
            "email": email,
            "website": f"https://www.{slug[:20]}.com",
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "category": random.choice(CATEGORIES),
            "rating": str(round(random.uniform(1.0, 5.0), 1)),
            "review_count": random.randint(1, 500),
            "source": source,
            "source_url": f"https://{source}.com/biz/{slug[:30]}",
            "scraped_at": scraped_at,
        })

    return records
