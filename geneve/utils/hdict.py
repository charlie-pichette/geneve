# Licensed to Elasticsearch B.V. under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Hierarchical dictionary."""


def depth_first_keys(d, path=None):
    path = path or ()
    for k, v in d.items():
        p = path + (k,)
        if isinstance(v, dict):
            for k in depth_first_keys(v, p):
                yield k
        else:
            yield ".".join(p)


def depth_first_items(d, path=None):
    path = path or ()
    for k, v in d.items():
        p = path + (k,)
        if isinstance(v, dict):
            for k, v in depth_first_items(v, p):
                yield k, v
        else:
            yield ".".join(p), v


class hdict:
    """Multi level dictionary with JSON path-like keys."""

    def __init__(self):
        self.__top_level = {}
        self.__groups = []

    def __eq__(self, other):
        return self.__top_level == other.__top_level and self.__groups == other.__groups

    def __getitem__(self, key):
        d = self.__top_level
        try:
            for part in key.split("."):
                d = d[part]
        except KeyError:
            raise KeyError(key)
        return d

    def __setitem__(self, key, value):
        d = self.__top_level
        parts = key.split(".")
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value
        self.__update_groups()

    def __delitem__(self, key):
        d = self.__top_level
        parts = key.split(".")
        try:
            for part in parts[:-1]:
                d = d[part]
        except KeyError:
            return
        del d[parts[-1]]
        self.__update_groups()

    def __iter__(self):
        return depth_first_keys(self.__top_level)

    def items(self):
        return depth_first_items(self.__top_level)

    def __update_groups(self):
        groups = set()
        tail = []
        for field in self:
            parts = field.split(".")[:-1]
            while parts:
                groups.add(".".join(parts))
                parts = parts[:-1]
            tail = tail or [""]
        self.__groups = sorted(sorted(groups), key=lambda x: x.count("."), reverse=True) + tail

    def groups(self):
        for group in self.__groups:
            if group:
                yield group, {f"{group}.{k}": v for k, v in self[group].items() if k and not isinstance(v, dict)}
            else:
                yield "", {k: v for k, v in self.__top_level.items() if k and not isinstance(v, dict)}