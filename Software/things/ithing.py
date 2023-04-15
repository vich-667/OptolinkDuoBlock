#!/usr/bin/python3
"""
Created on 18.10.2019

@author: vich
"""
import abc
import logging

log = logging.getLogger("Thing")


class InvalidThingSet(Exception):
    pass


class IThing(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_status(self):
        pass

    @abc.abstractmethod
    def set_value(self, channel, value):
        pass

    @abc.abstractmethod
    def shutdown(self):
        pass


class ThingMock(IThing):
    def get_status(self):
        return {
            "state": "do",
            "position1": 100,
            "position2": 0
        }

    def set_value(self, channel, value):
        log.debug(f"Set {channel} with value {value} to thing mock!")
        return True

    def shutdown(self):
        pass

    def start(self):
        """
        method provided from threading
        """
        pass
