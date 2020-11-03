import asyncio
import aiohttp


class PrometheusMeta:
    def __init__(self, **kw):
        self.login = kw['login']
        self.passwd = kw['password']
        self.url = kw['url']
        self.api_path = kw['api_path']
        self.api_url = f'{self.url}{self.api_path}'
        self.headers = kw['headers']


prmt_meta = PrometheusMeta(
    login='login',
    password='password',
    url='https://prometheus.example.com/api/v1/query',
    api_path='/api/v1/query',
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

big_q = [
    { 'query': f'avg by (namespace) (avg_over_time(kube_deployment_created{{deployment="kube-controlplane",namespace=~"cp-[0-9]+"}}[{day+1}d]))'} 
    for day in range(3)
]

##########################################################################################################################################################
########################      KАК ВОТ ЭТО ПРЕВРАТИТЬ В КЛАСС назавем его Worker + СМ ВОПРОС В MAIN      ##################################################
##########################################################################################################################################################
async def fetch(client, data_post):
    async with client.post(url=prmt_meta.url, data=data_post) as resp:
        assert resp.status == 200
        return await resp.json()


async def queue(client, queries):
    tasks = []
    for q in queries:
        ob = asyncio.ensure_future(
            fetch(client, q)
        )
        tasks.append(ob)
    return await asyncio.gather(*tasks)


async def main():
    headers = prmt_meta.headers
    auth = aiohttp.BasicAuth(login=prmt_meta.login, password=prmt_meta.passwd)
    async with aiohttp.ClientSession(auth=auth, headers=headers) as session:
        return await queue(session, big_q)


if __name__ == '__main__':
    # Хочу что бы было как то так
    # worker = Worker(
    #    url=prtm.url,
    #    login=prtm.login,
    #    pass=prtm.pass
    # )
    # worker.big_q=[<BIG QUEUE HERE>]
    # result = worker.run()
    
    print(asyncio.run(main()))
