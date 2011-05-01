"""
HTTP Auth Code Copyright (c) 2009-10 Michael Foord
http://www.voidspace.org.uk/python/articles/urllib2.shtml#id5

Anything else Copyright (c) 2011 Lee Trout

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Example:

import json
import time
from twitter_stream import TwitterStreamClient

tsc = TwitterStreamClient('user', 'pass',
    'http://stream.twitter.com/1/statuses/filter.json',
    data='track=foo')

def chirp(content):
    # This will output the incoming data (string) to the log
    logger.debug(content)
    # load the JSON
    tweet = json.loads(content)
    # now do something with the tweet...
    

tsc.register_handler(chirp)

if __name__ == '__main__':
    # listen for tweets for 30 seconds
    tsc.listen()
    time.sleep(30)
    tsc.disconnect()


"""
import logging
import socket
import sys
import threading
import time
import urllib2

# set buffer to 0 so we get small bits of data
socket._fileobject.default_bufsize = 0

logger = logging.getLogger('twitter_stream.TwitterStreamClient')

class TwitterStreamClient(object):
    """
    Simple client for Twitter's streaming API.
    """
    can_listen = True
    conn = None
    conn_args = {}
    connected = False
    error = None
    handlers = []
    reconnect_count = 0
    reconnect_delay = 5
    reconnect_max = 5
    
    def __init__(self, username, password, api_url, **conn_args):
        """
        Send over any connection arguments in conn_args. If you are using the filter
        api then you should provide a keyword argument.
        i.e. data="track=foo&follow=user"
        """
        logger.debug("constructing client %s %s %s" % (username, api_url, str(conn_args)))
        self.api_url = api_url
        self.credentials = {"user":username,"pass":password}
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, api_url, username, password)
        auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        self.opener = urllib2.build_opener(auth_handler)
        self.conn_args = conn_args
    
    def _handle(self, content):
        """
        Handle an incoming stream event by passing the data to the handler.
        """
        for h in self.handlers:
            h(content)
        if not self.handlers:
            logger.warn("No handlers specified")
            raise Exception("No handlers specified")
    
    def _listen(self, connect=True):
        """
        Wait on incoming events (new lines) and call the handler.
        """
        logger.debug('listen called')
        if connect and not self.connected:
            logger.debug('not connected... connecting')
            self.connect()
        listen = self.can_listen
        while listen:
            try:
                if self.conn:
                    self._handle(self.conn.readline())
                time.sleep(0.1)
                listen = self.can_listen
            except:
                logger.warn("an exception listening has occured (%s)" % str(sys.exc_info()[1]))
                listen = False
                self.reconnect()
    
    def connect(self):
        """
        Connects to self.api_url.
        """
        logger.debug("connecting %s %s" % (self.api_url, str(self.conn_args)))
        try:
            self.conn = self.opener.open(self.api_url, **self.conn_args)
            self.connected = True
        except:
            self.error = sys.exc_info()[1]
            logger.critical(self.error)
    
    def disconnect(self):
        """
        Closes the active connection.
        """
        if self.connected and self.conn:
            self.can_listen = False
        self.connected = False
    
    def listen(self):
        """
        Wrapper to spin off a listening thread.
        """
        self.can_listen = True
        threading.Thread(target=self._listen).start()
    
    def reconnect(self, failure=None):
        """
        Handles reconnecting and delaying to avoid hammering the host.
        """
        self.disconnect()
        if not self.error:
            if self.reconnect_count < self.reconnect_max:
                self.reconnect_count += 1
                delay = self.reconnect_delay * self.reconnect_count
                logger.info("reconnecting in %d seconds" % delay)
                time.sleep(delay)
                self.listen()
                return True
            self.error = 'Maximum reconnect attempts reached'
        logger.fatal(self.error)
    
    def register_handler(self, handler, idx=None):
        """
        Helper method to add a handler
        """
        if not idx:
            idx = len(self.handlers)
        if callable(handler):
            logger.debug("Adding handler (%s) in position %d" % (str(handler), idx))
            self.handlers.insert(idx, handler)
        else:
            logger.error("Handler \"%s\" is not callable" % str(handler))
            raise Exception("Handler \"%s\" is not callable" % str(handler))
    
    def unregister_handler(self, handler):
        """
        Helper method to remove a handler.
        """
        logger.debug("Removing handler (%s)" % str(handler))
        self.handlers.remove(handler)
        