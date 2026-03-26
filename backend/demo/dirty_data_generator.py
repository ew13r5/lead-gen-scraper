from __future__ import annotations

import copy
import random


def make_dirty(records: list[dict], seed: int | None = None) -> list[dict]:
    if seed is not None:
        random.seed(seed)

    result = [copy.deepcopy(r) for r in records]
    duplicates = []

    for record in result:
        # 15% duplicates
        if random.random() < 0.15:
            dupe = copy.deepcopy(record)
            dupe["source"] = random.choice(["yelp", "bbb", "google_maps", "clutch"])
            if dupe.get("phone"):
                # Slightly vary phone format
                digits = "".join(c for c in dupe["phone"] if c.isdigit())
                if len(digits) >= 10:
                    dupe["phone"] = f"{digits[:3]}-{digits[3:6]}-{digits[6:10]}"
            duplicates.append(dupe)

        # 10% invalid emails
        if random.random() < 0.10 and record.get("email"):
            corruption = random.choice(["remove_at", "bad_tld", "typo"])
            if corruption == "remove_at":
                record["email"] = record["email"].replace("@", "")
            elif corruption == "bad_tld":
                record["email"] = record["email"].replace(".com", ".con")
            elif corruption == "typo":
                record["email"] = "x" + record["email"]

        # 10% phone format variations (already varied by seeder, but force some)
        if random.random() < 0.10 and record.get("phone"):
            digits = "".join(c for c in record["phone"] if c.isdigit())
            if len(digits) >= 10:
                fmt = random.choice([
                    f"({digits[:3]}) {digits[3:6]}-{digits[6:10]}",
                    f"+1{digits[:10]}",
                    f"{digits[:3]}.{digits[3:6]}.{digits[6:10]}",
                ])
                record["phone"] = fmt

        # 5% HTML entities
        if random.random() < 0.05 and record.get("company_name"):
            record["company_name"] = record["company_name"].replace("&", "&amp;")
            if "'" in record["company_name"]:
                record["company_name"] = record["company_name"].replace("'", "&#39;")
            elif "&amp;" not in record["company_name"]:
                record["company_name"] = record["company_name"] + " &amp; Co"

        # 5% Unicode issues
        if random.random() < 0.05:
            if record.get("address"):
                pos = random.randint(0, max(0, len(record["address"]) - 1))
                record["address"] = record["address"][:pos] + "\u200b" + record["address"][pos:]
            if record.get("company_name"):
                record["company_name"] = record["company_name"].replace(" ", "\u00a0", 1)

    result.extend(duplicates)
    random.shuffle(result)
    return result
