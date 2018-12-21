from typing import Tuple, Callable

import torchvision
from torch import nn, Tensor
from torch.nn import functional as F

import backbone.base


class ResNet101(backbone.base.Base):

    def __init__(self, pretrained: bool):
        super().__init__(pretrained)

    def features(self) -> Tuple[nn.Module, Callable[[Tensor], Tensor], nn.Module, Callable[[Tensor], Tensor], int, int]:
        resnet101 = torchvision.models.resnet101(pretrained=self._pretrained)

        # list(resnet101.children()) consists of following modules
        #   [0] = Conv2d, [1] = BatchNorm2d, [2] = ReLU, [3] = MaxPool2d,
        #   [4] = Sequential(Bottleneck...), [5] = Sequential(Bottleneck...),
        #   [6] = Sequential(Bottleneck...), [7] = Sequential(Bottleneck...),
        #   [8] = AvgPool2d, [9] = Linear
        children = list(resnet101.children())
        features = children[:-3]
        num_features_out = 1024

        hidden = children[-3]
        num_hidden_out = 2048

        for parameters in [feature.parameters() for i, feature in enumerate(features) if i <= 4]:
            for parameter in parameters:
                parameter.requires_grad = False

        features = nn.Sequential(*features)

        return features, self.pool_handler, hidden, self.hidden_handler, num_features_out, num_hidden_out

    def pool_handler(self, pool: Tensor) -> Tensor:
        return pool

    def hidden_handler(self, hidden: Tensor) -> Tensor:
        hidden = F.adaptive_max_pool2d(input=hidden, output_size=1)
        hidden = hidden.view(hidden.shape[0], -1)
        return hidden
