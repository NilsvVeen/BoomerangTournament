import config
import requests
from requests.auth import (HTTPBasicAuth)
import re

def format_ranked_results(event_title, scores_dict):
    """
    Returns HTML <ul> with ranks.
    Do NOT return the <h2> heading — that's handled in update_tournament_page.
    """
    is_fast_catch = event_title.lower() in ["fast catch", "fc"]

    def parse_score(score):
        if isinstance(score, str):
            s = score.strip().lower()
            if s.endswith('c'):  # catches only
                try:
                    return 1000 - int(s[:-1])
                except:
                    return float('inf')
            elif '/' in s:
                try:
                    time, catches = s.replace("s", "").split("/")
                    time = float(time.strip())
                    catches = int(catches.strip().replace("c", ""))
                    return time if catches >= 5 else 1000 - catches
                except:
                    return float('inf')
            else:
                try:
                    return float(s)
                except:
                    return float('inf')
        return float(score)

    sortable = [(parse_score(score), name, score) for name, score in scores_dict.items()]
    reverse = not is_fast_catch
    sortable.sort(reverse=reverse)

    lines = ["<ul>"]
    for rank, (_, name, raw_score) in enumerate(sortable, start=1):
        lines.append(f"<li>{rank}. {name}: {raw_score}</li>")
    lines.append("</ul>")

    return "\n".join(lines)



def update_tournament_page(event_title, scores_html):
    if config.uploadingToWebsite:
        username = config.website_credentials.get("username", "")
        app_password = config.website_credentials.get("app_password", "")
        base_url = config.website_credentials.get("base_url", "")
        tournament_slug = config.website_credentials.get("tournament_slug", "")
        auth = HTTPBasicAuth(username, app_password)

        if not all([username, app_password, base_url, tournament_slug]):
            print("❌ Missing required website credentials.")
            return

        # 1. Get page by slug
        response = requests.get(f"{base_url}?slug={tournament_slug}", auth=auth)
        if response.status_code != 200:
            print(f"❌ Failed to fetch pages: {response.status_code} {response.text}")
            return

        if response.json():
            page = response.json()[0]
            page_id = page['id']

            # 2. Fetch raw content
            detail = requests.get(f"{base_url}/{page_id}?context=edit", auth=auth)
            if detail.status_code != 200:
                print("❌ Could not fetch raw page content.")
                return

            raw_content = detail.json().get("content", {}).get("raw", "")

            # 3. Build wrapped section
            new_section = f"<!-- EVENT: {event_title} -->\n<h2>{event_title}</h2>\n{scores_html}\n<!-- END EVENT: {event_title} -->"

            # 4. Replace or insert
            pattern = rf"(?s)<!-- EVENT: {re.escape(event_title)} -->.*?<!-- END EVENT: {re.escape(event_title)} -->"
            if re.search(pattern, raw_content):
                updated_content = re.sub(pattern, new_section, raw_content)
            else:
                updated_content = raw_content.strip() + "\n\n" + new_section

            # 5. Update page
            update = requests.post(
                f"{base_url}/{page_id}",
                auth=auth,
                json={"content": updated_content}
            )

            if update.status_code == 200:
                print(f"✅ Updated event '{event_title}' in page '{tournament_slug}'.")
            else:
                print(f"❌ Failed to update page: {update.status_code} {update.text}")
        else:
            print(f"⚠️ Creating new page for tournament '{tournament_slug}'...")

            new_content = f"<h1>{tournament_slug.replace('-', ' ').title()}</h1>\n\n<!-- EVENT: {event_title} -->\n<h2>{event_title}</h2>\n{scores_html}\n<!-- END EVENT: {event_title} -->"
            create = requests.post(
                base_url,
                auth=auth,
                json={
                    "title": tournament_slug.replace('-', ' ').title(),
                    "slug": tournament_slug,
                    "status": "publish",
                    "content": new_content
                }
            )

            if create.status_code == 201:
                print(f"✅ Created new page '{tournament_slug}'.")
            else:
                print(f"❌ Failed to create page: {create.status_code} {create.text}")
