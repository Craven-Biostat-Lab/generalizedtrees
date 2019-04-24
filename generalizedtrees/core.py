# Generalized Tree Models
#
# Copyright 2019 Yuriy Sverchkov
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

from __future__ import annotations
from sklearn.base import BaseEstimator, ClassifierMixin
from typing import List, Tuple
from abc import ABC, abstractmethod
from collections import deque
import logging

logger = logging.getLogger(__name__)


class Constraint(ABC):

    @abstractmethod
    def test(self, sample):
        pass


class LEQConstraint(Constraint):

    def __init__(self, feature_index, value):
        self.feature_index = feature_index
        self.value = value

    def test(self, sample):
        return sample[self.feature_index] <= self.value

    def __invert__(self):
        return GTConstraint(self.feature_index, self.value)

    def __repr__(self):
        return f"[{self.feature_index}]<={self.value}"


class GTConstraint(Constraint):

    def __init__(self, feature_index, value):
        self.feature_index = feature_index
        self.value = value

    def test(self, sample):
        return sample[self.feature_index] > self.value

    def __invert__(self):
        return LEQConstraint(self.feature_index, self.value)

    def __repr__(self):
        return f"[{self.feature_index}]>{self.value}"


class SimplePredictor:

    def __init__(self, prediction):
        self.prediction = prediction

    def predict(self, sample):
        return self.prediction

    def __repr__(self):
        return f'Predict: {self.prediction}'


class Node:

    def __init__(self, constraint: Constraint = None, parent: Node = None):
        self.parent = parent
        self.constraint = constraint
        self.model = None

    @property
    def all_constraints(self) -> () or Tuple[Constraint]:
        if self.parent:
            if self.constraint is None:
                logger.error(f'Node {self} with parent {self.parent}. This is a bad constraint configuration.')
            return self.parent.all_constraints + (self.constraint,)
        elif self.constraint is not None:
            return self.constraint,  # Trailing comma because this is a tuple
        else:
            return ()

    def __repr__(self):
        return f'({self.constraint}: {self.model})'


class ChildSelector:

    def __init__(self, children: List[Node]):
        self.children = children

    def predict(self, sample):
        for c in self.children:  # Child constraints should be mutex so we return the first satisfying one
            if c.constraint.test(sample):
                return c.model.predict(sample)
        return None  # Maybe throw exception here?

    def __repr__(self):
        return self.children.__repr__()


class NodeQueue:

    def __init__(self):
        self.q = deque()

    def append(self, x):
        self.q.append(x)

    def extend(self, xs):
        self.q.extend(xs)

    def pop(self):
        return self.q.popleft()

    def __len__(self):
        return len(self.q)


class GeneralTreeEstimator(BaseEstimator, ABC):

    def __init__(
            self,
            sequential_access_data_structure_factory=NodeQueue):
        """
        The general tree classifier is defined by
        :param sequential_access_data_structure_factory: A  factory that produces a data structure such as a stack,
        queue, or priority queue that determines the order in which the tree is built. For a priority queue the rule for
        comparing nodes is also communicated through this function. The data structure must implement append (for one
        element), extend (for a list of elements) and pop.
        """
        assert callable(sequential_access_data_structure_factory),\
            "Sequential access data structure factory must be callable"
        self.root = None
        self.sequential_access_data_structure_factory = sequential_access_data_structure_factory

    @abstractmethod
    def best_split(self, constraints):
        pass

    @abstractmethod
    def leaf_predictor(self, constraints):
        pass

    def best_split_of_node(self, node: Node):
        return self.best_split(node.all_constraints)

    def leaf_predictor_of_node(self, node: Node):
        return self.leaf_predictor(node.all_constraints)

    def build(self):
        self.root = Node()
        nodes = self.sequential_access_data_structure_factory()
        nodes.append(self.root)

        while nodes:
            parent = nodes.pop()
            split = self.best_split_of_node(parent)

            logger.log(5, f'building: {self}')
            logger.log(5, f'best split: {split}')

            if len(split) > 1:  # Splitting
                children = [Node(s, parent) for s in split]
                logger.log(5, f'setting children: {children}')
                parent.model = ChildSelector(children)
                nodes.extend(children)

            else:  # It's a leaf
                parent.model = self.leaf_predictor_of_node(parent)

    def predict(self, data):
        return [self.predict_instance(x) for x in data]

    def predict_instance(self, sample):
        return self.root.model.predict(sample)

    def __repr__(self):
        return f"Tree: {self.root}"


def test_all_x(constraints):
    return lambda x: all([c.test(x) for c in constraints])


def test_all_tuples(constraints):
    return lambda pair: test_all_x(constraints)(pair[0])


class AbstractTreeClassifier(GeneralTreeEstimator, ClassifierMixin):
    pass