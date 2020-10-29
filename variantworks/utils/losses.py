#!/usr/bin/env python
#
# Copyright 2020 NVIDIA CORPORATION.
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
#
"""Custom loss function implementations."""


import torch
from torch.nn.functional import one_hot
import torch.nn.functional as F
from nemo.backends.pytorch.nm import LossNM
from typing import Optional
from nemo.core.neural_types import LabelsType, LogitsType, LossType, NeuralType
from nemo.utils.decorators import add_port_docs


class CategoricalFocalLoss(LossNM):
    """Criterion that computes Categorical Focal Loss."""

    def __init__(self, alpha: float, gamma: Optional[float] = 2.0,
                 reduction: Optional[str] = 'none', logits_dim=2) -> None:
        super(FocalLoss, self).__init__()
        self.alpha: float = alpha
        self.gamma: Optional[float] = gamma
        self.reduction: Optional[str] = reduction
        self.eps: float = 1e-10
        self._logits_dim = logits_dim

    @property
    @add_port_docs()
    def input_ports(self):
        """Returns definitions of module input ports.
        """
        return {
            "logits": NeuralType(['B'] + ['ANY'] * (self._logits_dim - 1), LogitsType()),
            "labels": NeuralType(['B'] + ['ANY'] * (self._logits_dim - 2), LabelsType()),
        }

    @property
    @add_port_docs()
    def output_ports(self):
        """Returns definitions of module output ports.
        loss:
            NeuralType(None)
        """
        return {"loss": NeuralType(elements_type=LossType())}

    def _loss_function(
            self,
            logits: torch.Tensor,
            labels: torch.Tensor) -> torch.Tensor:
        # compute log softmax of logits
        log_probs = F.log_softmax(logits, dim=-1)
        probs = torch.exp(log_probs)
        return F.nll_loss(
            ((1 - probs) ** self.gamma) * log_probs, 
            labels, 
            weight=self.alpha,
            reduction = self.reduction
        )
