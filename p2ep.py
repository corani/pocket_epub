#!/usr/bin/python
#
# Copyright (c) 2014, Daniel Bos
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of the <organization> nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import time, configparser, threading, cherrypy
import urllib, urllib2, json, webbrowser, re, os
from jinja2 import Environment, FileSystemLoader
from subprocess import call

class P2eP(threading.Thread):
    auth_done = False

    def __init__(self):
        threading.Thread.__init__(self)
        self.config = configparser.ConfigParser()
        self.config.read('settings.dat')
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.env.filters['create_file_name'] = lambda article: re.sub("[^a-zA-Z0-9]+", "_", article['resolved_title']) or article['resolved_id']

    def saveConfig(self):
        with open('settings.dat', 'w') as f:
            self.config.write(f)

    def postJSON(self, url, data):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-Accept', 'application/json')
        res = urllib2.urlopen(req, json.dumps(data))
        return json.loads(res.read())

    def getJSON(self, url):
        res = urllib2.urlopen(url)
        return json.loads(res.read())
    
    def auth(self):
        if len(self.config.get('DEFAULT', 'pocket_token', fallback='')) == 0:
            cherrypy.log("Start OAuth authorization")
            data = self.postJSON('https://getpocket.com/v3/oauth/request', {
                "consumer_key": self.config['DEFAULT']['pocket_key'],
                "redirect_uri": 'http://127.0.0.1:1337/oauthRequest'
            })
            code = data['code']
            webbrowser.open("https://getpocket.com/auth/authorize?request_token=%s&redirect_uri=%s" % (code, urllib.quote("http://127.0.0.1:1337/oauthAuthorize")))
            while not self.auth_done:
                time.sleep(1)
            data = self.postJSON('https://getpocket.com/v3/oauth/authorize', {
                "consumer_key": self.config['DEFAULT']['pocket_key'],
                "code": code
            })
            self.config['DEFAULT']['pocket_token'] = data['access_token']
            self.saveConfig()
        else:
            cherrypy.log("Authorization already done")

    def run(self):
        cherrypy.log("Start server")
        cherrypy.config.update({
            'tools.encode.on': True,
            'tools.decode.on': True,
            'tools.encode.encoding': 'utf-8',
            'tools.gzip.on': True,
            'server.socket_port': 1337
        })
        cherrypy.quickstart(self, '/')

    @cherrypy.expose
    def oauthRequest(self):
        return "You may close this window"

    @cherrypy.expose
    def oauthAuthorize(self):
        self.auth_done = True
        return "You may close this window"

    @cherrypy.expose
    def script(self):
        cherrypy.log("Generating script")
        tpl = self.env.get_template('script.tpl')
        return tpl.render(articles = self.articles)

    @cherrypy.expose
    def load(self, id):
        id = id.split(".")[0]
        cherrypy.log("Loading %s" % id)
        if os.path.isfile("cache/%s.html" % id):
            cherrypy.log("Cache hit!")
            with open("cache/%s.html" % id, "r") as f:
                return f.read()
        else:
            url = self.articles[int(id)]['resolved_url']
            cherrypy.log("Get %s" % url)
            data = self.getJSON('http://www.readability.com/api/content/v1/parser?url=%s&token=%s' % (urllib.quote(url), self.config['DEFAULT']['readability_token']))
            with open("cache/%s.html", "w") as f:
                f.write(data['content'])
            return data['content']

    @cherrypy.expose
    def done(self):
        cherrypy.log("Terminating server")
        cherrypy.server.exit()

    def retrievePocketList(self):
        cherrypy.log("Retrieve Pocket list")
        data = self.postJSON("https://getpocket.com/v3/get", {
            "consumer_key": self.config['DEFAULT']['pocket_key'],
            "access_token": self.config['DEFAULT']['pocket_token'],
            "detailType": "simple",
            "sort": "oldest",
            "contentType": "article",
            "state": "unread",
            "since": int(self.config.get('DEFAULT', 'since', fallback=0))
        })
        if data['status'] == 1:
            self.articles = {}
            for key, value in data['list'].iteritems():
                self.articles[key] = {
                    'resolved_id': value['resolved_id'],
                    'resolved_url': value['resolved_url'],
                    'resolved_title': value['resolved_title']
                }
            self.config['DEFAULT']['since'] = str(int(time.time()))
            self.saveConfig()
        return data['status'] == 1

    def convert(self):
        cherrypy.log("Start converting")
        call(['wget', '-q', 'http://127.0.0.1:1337/script'])
        call(['bash', './script'])

    def foreground(self):
        time.sleep(2)
        self.auth()
        if self.retrievePocketList():
            self.convert()
        else:
            cherrypy.engine.exit()

p = P2eP()
p.start()
p.foreground()
