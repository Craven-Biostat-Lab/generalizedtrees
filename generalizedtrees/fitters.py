# Fitting functions (for use in tree composition)
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

from typing import Tuple
from generalizedtrees.base import AbstractTreeBuilder
from generalizedtrees.core import FeatureSpec
import pandas as pd
import numpy as np

def supervised_data_fit(
    tree_builder: AbstractTreeBuilder,
    data: np.ndarray,
    targets: np.ndarray,
    feature_spec: Tuple[FeatureSpec],
    **kwargs):

    # TODO: Handle kwargs

    # Data checking can be inserted here

    tree_builder.target_classes = np.unique(targets)

    tree_builder.data = data
    tree_builder.targets = targets
    tree_builder.feature_spec = feature_spec

    tree_builder._build()
    tree_builder.prune()

    return tree_builder

def fit_with_data_and_oracle(
    tree_builder,
    data,
    oracle,
    #feature_spec: Tuple[FeatureSpec, ...], #TODO: Infer feature_spec
    #oracle_gives_probabilities: bool = False, #TODO: Figure out need and scope
    #max_tree_size: Optional[int] = None, #TODO: Set in parameters/kwargs
    **kwargs):
    
    tree_builder.data = data
    _, tree_builder._d = np.shape(tree_builder.data)

    tree_builder.oracle = oracle

    tree_builder.oracle_gives_probabilities = False #oracle_gives_probabilities

    # Targets of training data
    if tree_builder.oracle_gives_probabilities:
        tree_builder.targets = pd.DataFrame(tree_builder.oracle(tree_builder.data))
    else:
        tree_builder.targets = pd.Series(tree_builder.oracle(tree_builder.data))

    # Build the tree
    tree_builder._build()
    tree_builder.prune()

    return tree_builder