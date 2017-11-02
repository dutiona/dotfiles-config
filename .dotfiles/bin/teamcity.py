
import urllib
import requests
import json

from pprint import pprint

import warnings
import logging
from logging import debug, info, warning, error
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logging.getLogger('requests').setLevel(logging.WARNING)

class teamcity(object):
    def __init__(self, host, user, password):
        self._host = host
        self._url = "https://{}/httpAuth/app/rest".format(host)
        self._auth = (user, password)

    def _request(self, method, url, headers=None, data=None):
        options = {
                "method": method,
                "url": url,
                "headers": headers,
                "auth": self._auth,
                "verify": False
                }
        # print("{} {}".format(options["method"], options["url"]))
        if data:
            options["data"] = data
        r = requests.request(**options)
        if r.status_code >= 400:
            print(r)
            raise urllib.error.HTTPError(options["url"], r.status_code, r.reason, r.headers, None)
        return r

    def get(self, href):
        url = "https://{}{}".format(self._host, href)
        return self._request("GET", url, {"Accept": "application/json"}).json()

    def build_queue(self):
        return self._request("GET", self._url + "/buildQueue", {"Accept": "application/json"}).json()

    def get_agent_properties(self, href):
        agent = self.get(href)
        properties = {}
        if agent["properties"]["count"] > 0:
            for p in agent["properties"]["property"]:
                properties[p["name"]] = p["value"]
        return properties

    def get_agents(self):
        r = self._request( "GET", self._url + "/agents?locator=authorized:any,connected:any", {"Accept": "application/json"}).json()
        if r["count"] == 0:
            return []
        else:
            return r["agent"]

    def get_agent(self, name):
        for agent in self.get_agents():
            if agent["name"] == name:
                url = "https://{}{}".format(self._host, agent["href"])
                return self._request("GET", url, {"Accept": "application/json"}).json()
        return None

    def authorized(self, agent, status=None):
        url = "https://{}{}/authorized".format(self._host, agent["href"])
        if status != None:
            return self._request("PUT", url, {"Content-Type": "text/plain"}, str(status).lower()).json()
        else:
            return self._request("GET", url, {"Content-Type": "text/plain"}).json()

    def enabled(self, agent, status=None):
        url = "https://{}{}/enabled".format(self._host, agent["href"])
        if status != None:
            return self._request("PUT", url, {"Content-Type": "text/plain"}, str(status).lower()).json()
        else:
            return self._request("GET", url, {"Content-Type": "text/plain"}).json()

    def connected(self, agent):
        url = "https://{}{}/connected".format(self._host, agent["href"])
        return self._request("GET", url, {"Content-Type": "text/plain"}).json()

    def remove(self, agent):
        if self.connected(agent):
            error("Still connected, cannot remove the agent: {}".format(agent["name"]))
        url = "https://{}{}".format(self._host, agent["href"])
        self._request("DELETE", url)

    def running_build(self, agent):
        url = "{}/builds?locator=agentName:{},running:true,personal:any,branch:branched:any".format(self._url, agent["name"])
        return self._request("GET", url, {"Accept": "application/json"}).json()

    def move_to_pool(self, agent, pool_id):
        url = "{}/agentPools/id:{}/agents".format(self._url, pool_id)
        xml = "<agent id='{}'/>".format(agent["id"])
        return self._request("POST", url, {"Content-Type": "application/xml", "Accept": "application/json"}, xml).json()


def main():
    warnings.simplefilter("ignore")
    tc = teamcity("teamcity.lrde.epita.fr", "bot", "VRqrvm7kayRU4")
    r = tc.get_agent("node8_1")
    # r = tc.get_agent("jessie-agent-node14-275763")
    # pprint(r)
    pprint(tc.running_build(r))

if __name__ == '__main__':
    main()
