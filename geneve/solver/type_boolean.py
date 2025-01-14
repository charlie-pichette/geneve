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

"""Constraints solver for boolean fields."""

from ..constraints import ConflictError
from . import solver


@solver("boolean", "==", "!=")
def solve_boolean_field(field, value, constraints, left_attempts, environment):
    for k, v, *_ in constraints:
        if k == "==":
            v = bool(v)
            if value is None or value == v:
                value = v
            else:
                raise ConflictError(f"is already {value}, cannot set to {v}", field, k)
        elif k == "!=":
            v = bool(v)
            if value is None or value != v:
                value = not v
            else:
                raise ConflictError(f"is already {value}, cannot set to {not v}", field, k)

    if left_attempts and value is None:
        value = random.choice((True, False))
        left_attempts -= 1
    return {"value": value, "left_attempts": left_attempts}
