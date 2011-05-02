# About

Spastic is a very simple threaded client for Twitter's streaming API that
provides methods for listening for new tweets and acting upon them as soon as
they are received.

# Usage

Spastic is designed to be very minimal with its core methods relegated to
handling HTTP authentication and dispatching events when data arrives.

## Track keywords or users

You can track keywords or users by calling the filter API method and passing
it a track and/or follow argument string. In this example we will track the
keyword "foo".

For more information see http://dev.twitter.com/doc/post/statuses/filter

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
        # we have to block since the listener is threaded
        time.sleep(30)
        tsc.disconnect()

## Ingest a random sample

You can also ingest a random sampling of tweets from all public statuses.

For more information see http://dev.twitter.com/doc/post/statuses/sample

    import json
    import time
    from twitter_stream import TwitterStreamClient
    
    tsc = TwitterStreamClient('user', 'pass',
        'http://stream.twitter.com/1/statuses/sample.json')
    
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
        # we have to block since the listener is threaded
        time.sleep(30)
        tsc.disconnect()

# License

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