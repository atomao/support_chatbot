import copy
import json
from datetime import datetime

from redis import Redis

from flaskshop.corelib.local_cache import lc 
from flaskshop.settings import Config



class PropsMixin:
    @property
    def _props_name(self):
        return f"__{self.get_uuid()}/props_cached"

    @property
    def _props_db_key(self):
        return f"{self.get_uuid()}/props"
    
    def get_props_item(self, key, default=None):
        return self.props.get(key, default)

    def set_props_item(self, key, value):
        props = self.props
        props[key] = value
        self.props = props

    def delete_props_item(self, key):
        props = self.props
        props.pop(key, None)
        self.props = props

    def update_props(self, data):
        props = self.props
        props.update(data)
        self.props = props

    def incr_props_item(self, key):
        n = self.get_props_item(key, 0)
        n += 1
        self.set_props_item(key, n)
        return n

    def decr_props_item(self, key, min_val=0):
        n = self.get_props_item(key, 0)
        n -= 1
        n = n if n > min_val else min_val
        self.set_props_item(key, n)
        return n


class PropsItem:
    def __init__(self, name, default=None, output_filter=None, pre_set=None):
        self.name = name
        self.default = default
        self.output_filter = output_filter
        self.pre_set = pre_set

    def __get__(self, obj, objtype):
        r = obj.get_props_item(self.name, None)
        if r is None:
            return copy.deepcopy(self.default)
        elif self.output_filter:
            return self.output_filter(r)
        else:
            return r

    def __set__(self, obj, value):
        if self.pre_set:
            value = self.pre_set(value)
        obj.set_props_item(self.name, value)

    def __delete__(self, obj):
        obj.delete_props_item(self.name)


def datetime_outputfilter(v):
    return datetime.strptime(v, "%Y-%m-%d %H:%M:%S") if v else None


def date_outputfilter(v):
    return datetime.strptime(v, "%Y-%m-%d").date() if v else None


class DatetimePropsItem(PropsItem):
    def __init__(self, name, default=None):
        super().__init__(name, default, datetime_outputfilter)


class DatePropsItem(PropsItem):
    def __init__(self, name, default=None):
        super().__init__(name, default, date_outputfilter)
