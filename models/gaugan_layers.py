import torch
import torch.nn as nn


class SPADE(nn.Module):
    def __init__(self, scale_factor, n_filters, mask_channels):
        super(SPADE, self).__init__()
        self.scale_factor = scale_factor
        self.bn = nn.BatchNorm2d(n_filters)
        self.shared_conv = nn.Sequential(nn.Conv2d(mask_channels, 128, kernel_size=3, padding=1),
                                         nn.ReLU(inplace=True))
        self.mu_conv = nn.Conv2d(128, n_filters, kernel_size=3, padding=1)
        self.sigma_conv = nn.Conv2d(128, n_filters, kernel_size=3, padding=1)

    def forward(self, x, mask):
        mask = nn.functional.interpolate(mask, scale_factor=self.scale_factor)
        conditional_features = self.shared_conv(mask)
        mu = self.mu_conv(conditional_features)
        sigma = self.sigma_conv(conditional_features)
        return (x * sigma) + mu


class SPADE_ResBlock(nn.Module):
    def __init__(self, scale_factor, in_filters, n_filters , mask_channels):
        super(SPADE_ResBlock, self).__init__()
        self.spade_1 = SPADE(scale_factor, in_filters, mask_channels)
        self.relu_1 = nn.ReLU(inplace=True)
        self.conv_1 = nn.Conv2d(in_filters, n_filters, kernel_size=3, padding=1)
        self.spade_2 = SPADE(scale_factor, n_filters, mask_channels)
        self.relu_2 = nn.ReLU(inplace=True)
        self.conv_2 = nn.Conv2d(n_filters, n_filters, kernel_size=3, padding=1)
        self.spade_skip = SPADE(scale_factor, in_filters, mask_channels)
        self.relu_skip = nn.ReLU(inplace=True)
        self.conv_skip = nn.Conv2d(in_filters, n_filters, kernel_size=3, padding=1)


    def forward(self, x, mask):
        out = self.conv_1(self.relu_1(self.spade_1(x, mask)))
        out = self.conv_2(self.relu_2(self.spade_2(out, mask)))
        x = self.conv_skip(self.relu_skip(self.spade_skip(x, mask)))
        return out + x


