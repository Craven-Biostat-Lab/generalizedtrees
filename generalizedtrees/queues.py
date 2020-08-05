# Packaged queue and stack classes
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

from heapq import heappush, heappop
from collections import deque

class Heap(list):

    def push(self, item):
        heappush(self, item)
    
    def pop(self):
        return heappop(self)

class Stack(deque):

    def push(self, item):
        self.append(item)

class Queue(Stack):

    def pop(self):
        return super().popleft()
    
    def popright(self):
        return super().pop()
