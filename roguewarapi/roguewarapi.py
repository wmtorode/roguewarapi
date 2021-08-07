import requests
import logging
import traceback
import json
import time

from .data import StarMap, StarSystem, CacheManager, StarSystemConst, StarMapConstants

class RogueWarApi:
    """
    The Primary Interface for accessing the Roguewar API




    """
    _Version = "0.0.X"
    DefaultUri = 'http://roguewar.org'  #: the default URI of the RogueWar service
    _UserAgent = f'RogueWarApi/{_Version}'

    _kStarMapCacheKey = "kStarMap"


    def __init__(self, appName, appSecret, url=None, loggerhandler=None):
        """
        :param appName: the name of the client, use the name provided to you as part of your Name/Secret combo for authentication
        :type appName: str
        :param appSecret: the client secret you were given for API access
        :type appSecret: str
        :param url: optional, the url to the service, if not supplied a default is used
        :type url: str
        :param loggerhandler: optional, a standard python logging handler object
        :type loggerhandler: logging.Handler

        """
        self.appName = appName
        self.appSecret = appSecret
        self.BaseUri = self.DefaultUri + '/api/'
        if url is not None:
            self.BaseUri = url + '/api/'
        self.appToken = ''
        self.Logger = logging.getLogger("RogueWarApi")
        self.Logger.setLevel(logging.INFO)
        if loggerhandler is None:
            nullhandler = logging.NullHandler()
            self.Logger.addHandler(nullhandler)
        else:
            self.Logger.addHandler(loggerhandler)
        self.lastResult = None  # type: dict
        self.cache = CacheManager()
        self.starMapConstants = None # type: StarMapConstants


    def _getHeaders(self, cHeaders):
        headers = {'User-Agent': self._UserAgent, 'content-type': 'application/json', f'Authorization': f'Bearer {self.appToken}'}
        if self.appToken == '':
            del headers['Authorization']
        if cHeaders is not None:
            for header in cHeaders:
                headers[header] = cHeaders[header]
                if headers[header] == '':
                    del headers[header]
        return headers

    def _sendGetRequest(self, uri, callback=None, headers=None, reauth=True, **kwargs):
        try:
            url = self.BaseUri + uri
            firstarg = False
            for kwarg in kwargs:
                if not firstarg:
                    url += f'?{kwarg}={kwargs[kwarg]}'
                    firstarg = True
                else:
                    url += f'&{kwarg}={kwargs[kwarg]}'
            self.Logger.info(f'Sending Get request to: {url}')
            result = requests.get(url, headers=self._getHeaders(headers), verify=False)
            if result.ok:
                if callback is not None:
                    callback(result.json())
                else:
                    self.lastResult = result.json()
                return True
            else:
                if result.status_code == 401 and reauth:
                    if self._getAuthToken():
                        return self._sendGetRequest(uri, callback=callback, headers=headers, reauth=False, **kwargs)
                self.Logger.info(f'Request Failed: {result.status_code}')
        except:
            self.Logger.critical('Request Failed!')
            for line in traceback.format_exc().split("\n"):
                self.Logger.critical(line)
        return False

    def _sendPostRequest(self, uri, callback=None, jData=None, headers=None, reauth=True, **kwargs):
        try:
            url = self.BaseUri + uri
            firstarg = False
            for kwarg in kwargs:
                if not firstarg:
                    url += f'?{kwarg}={kwargs[kwarg]}'
                    firstarg = True
                else:
                    url += f'&{kwarg}={kwargs[kwarg]}'
            self.Logger.info(f'Sending Get request to: {url}')
            if jData is not None:
                bData = jData.encode()
                result = requests.post(url, headers=self._getHeaders(headers), data=bData, verify=False)
            else:
                result = requests.post(url, headers=self._getHeaders(headers), verify=False)
            if result.ok:
                if callback is not None:
                    callback(result.json())
                else:
                    self.lastResult = result.json()
                return True
            else:
                if result.status_code == 401 and reauth:
                    if self._getAuthToken():
                        return self._sendPostRequest(uri, callback=callback, jData=jData, headers=headers, reauth=False, **kwargs)
                self.Logger.info(f'Request Failed: {result.status_code}')
        except:
            self.Logger.critical('Request Failed!')
            for line in traceback.format_exc().split("\n"):
                self.Logger.critical(line)
        return False

    def _authCallback(self, jData):
        self.appToken = jData['access_token']

    def _getAuthToken(self):
        jData = {
            "botName" : self.appName,
            "botSecret" : self.appSecret
        }
        return self._sendPostRequest('botauth', callback=self._authCallback, jData=json.dumps(jData), reauth=False)

    def getStarMap(self):
        """
        Get the current starmap

        :return: a starmap object
        :rtype: StarMap
        """

        cache = self.cache.getCacheItem(self._kStarMapCacheKey)
        if cache:
            return cache
        if self._sendGetRequest('getmap'):
            starmap = StarMap()
            starmap.fromJson(self.lastResult)
            self.cache.placeCacheItem(self._kStarMapCacheKey, starmap)
            return starmap
        return None

    def getSystemConstants(self, bForce=False):
        """
        retrieve constants about the starmap, this includes data like system positions, and original owner

        :param bForce: force the data to be refreshed from the server, this generally shouldnt be needed
        :type bForce: bool
        :return: a `StarMapConstants` object
        :rtype: StarMapConstants
        """
        if bForce or self.starMapConstants is None:
            if self._sendGetRequest('getsystemstatic'):
                constants = StarMapConstants()
                constants.fromJson(self.lastResult)
                stTime = time.time()
                constants.mapAdjacents(50)
                self.starMapConstants = constants
                self.Logger.info(f"Adjacency Mapping took: {time.time() - stTime:0.02f} seconds")
        return self.starMapConstants
