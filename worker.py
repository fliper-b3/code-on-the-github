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

class Worker:

    _task_queue = []
    _result_data = []

    def __init__(self, url, login, password, headers):
        self.url = url
        self.login = login
        self.password = password
        self.headers = headers
        self.auth = aiohttp.BasicAuth(login=prmt_meta.login,
                                 password=prmt_meta.passwd)

    def set_queue(self, q):
        self._task_queue = q

    def get_queue(self):
        return self._task_queue

    async def fetch(self, client, data_post):
        async with client.post(url=self.url, data=data_post) as resp:
            assert resp.status == 200
            return await resp.json()

    async def queue(self, client):
        tasks = []
        for q in self._task_queue:
            ob = asyncio.ensure_future(
                self.fetch(client, q)
            )
            tasks.append(ob)
        return await asyncio.gather(*tasks)

    async def main(self):
        if not self._task_queue:
            raise ("Queue is empty")
        async with aiohttp.ClientSession(auth=self.auth, headers=self.headers) as session:
            return await self.queue(session)

    def get_data(self):
        return self._result_data

    def run(self):
        self._result_data = asyncio.run(self.main())

if __name__ == '__main__':
    w = Worker(
        url=prmt_meta.url,
        login=prmt_meta.login,
        password=prmt_meta.passwd,
        headers=prmt_meta.headers,
    )
    w.set_queue(
        [
            {
                'query': f'avg by (namespace) (avg_over_time(kube_deployment_created{{deployment="kube-controlplane",namespace=~"cp-[0-9]+"}}[{day + 1}d]))'}
            for day in range(3)
        ]
    )
    w.run()
    print(w.get_data())
