# -*- coding: utf-8 -*-

""" Module to handle account information """
#
# Author: Wil Alvarez (aka Satanas)
# Mar 13, 2011

from turpial.api.common import DefProtocols
from turpial.api.models.profile import Profile
from turpial.api.protocols.twitter import twitter

class Account:    
    def __init__(self, id_, protocol_id):
        self.id_ = id_
        if protocol_id == DefProtocols.TWITTER:
            self.protocol = twitter.Main(self.id_)
        #elif protocol_id == DefProtocols.IDENTICA:
        #    self.protocol = identica.Main(self._id)
        self.profile = Profile()
    
    def auth(self, username, password):
        self.profile = self.protocol.auth(username, password)
        
    def __getattr__(self, name):
        try:
            return getattr(self.protocol, name)
        except:
            try:
                return getattr(self.profile, name)
            except:
                raise AttributeError
