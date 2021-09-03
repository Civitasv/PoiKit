# -- coding: utf-8 --
from enum import Enum


class CrawlType(Enum):
    RECT = 0
    ADCODE = 1
    USER_CUSTOM = 2
