import requests

# API调用，开发初期先模拟紫岛的appid
host = "https://adnmb2.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36"}


def get_showf(fid: str, page: int):
    url = host+"Api/showf"
    data = {"appid": "nimingban", "page": str(page), "id": fid}
    if fid == "-1":
        url = host+"Api/timeline"
        del(data["id"])
    r = requests.get(url=url, headers=headers, params=data)
    return r


def get_thread(tid: str, page: int):
    url = "https://adnmb2.com/api/thread"
    data = {"appid": "nimingban", "id": tid, "page": str(page)}
    r = requests.get(url=url, headers=headers, params=data)
    return r


def get_forum_list(dao: str) -> dict:
    url = "http://cover.acfunwiki.org/luwei.json"
    r = requests.get(url).json()
    x = {}
    if dao == 'adnmb':
        for i in range(len(r['forum'])):
            x[r['forum'][i]['id']] = r['forum'][i]['name']
        return x
    elif dao == 'tnmb':
        # TODO: 备胎岛未适配
        return r.json()['beitaiForum']
    else:
        return {}



