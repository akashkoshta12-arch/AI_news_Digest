import requests

def get_github_news():
    url = "https://api.github.com/search/repositories?q=AI&sort=updated&order=desc"
    res = requests.get(url)

    if res.status_code != 200:
        return []

    data = []
    for repo in res.json().get("items", [])[:5]:
        data.append({
            "title": repo.get("name"),
            "content": repo.get("description") or "No description",
            "link": repo.get("html_url")
        })

    return data