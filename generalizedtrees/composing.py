# Utility for composing tree learners out of building blocks
#
# Copyright 2020 Yuriy Sverchkov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Type, Any
from dataclasses import make_dataclass
from generalizedtrees.base import TreeBuilder, TreeClassifierMixin


def greedy_classification_tree_learner(
    name: str,
    parameters, # As in dataclass
    fitter, # Fit function
    create_root, # Function
    construct_split, # Function
    generate_children, # Function
    queue: Type[Any], # Queue class
    global_stop, # function of model
    local_stop # function of model, node
    ):

    C = make_dataclass('C', fields=parameters, bases=(TreeBuilder, TreeClassifierMixin))

    members = dict(
        fit=fitter,
        new_queue=queue,
        create_root=create_root,
        construct_split=construct_split,
        generate_children=generate_children,
        global_stop=global_stop,
        local_stop=local_stop
    )

    return type(name, (C,), members)