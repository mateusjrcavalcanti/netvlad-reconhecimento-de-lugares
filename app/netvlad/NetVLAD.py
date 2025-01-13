import torch
import torch.nn as nn

class NetVLAD(nn.Module):
    def __init__(self, num_clusters=64, dim=512):
        super(NetVLAD, self).__init__()
        self.num_clusters = num_clusters
        self.dim = dim
        self.conv = nn.Conv2d(dim, num_clusters, kernel_size=(1, 1), bias=True)
        self.centroids = nn.Parameter(torch.rand(num_clusters, dim))

    def forward(self, x):
        N, C, H, W = x.shape  # Recupera as dimensões de entrada (batch, channels, height, width)
        x_flatten = x.view(N, C, -1)  # Achata as dimensões H e W para um vetor de características de C x (H*W)
        soft_assign = self.conv(x).view(N, self.num_clusters, -1)  # Aplica conv para obter soft-assignments
        soft_assign = torch.nn.functional.softmax(soft_assign, dim=1)

        vlad = torch.zeros([N, self.num_clusters, C], dtype=x.dtype, device=x.device)
        for C_idx in range(self.num_clusters):
            residual = x_flatten - self.centroids[C_idx:C_idx + 1, :].view(1, C, 1)
            residual *= soft_assign[:, C_idx:C_idx + 1, :].expand_as(residual)
            vlad[:, C_idx:C_idx + 1, :] = residual.sum(dim=-1)

        vlad = vlad.view(N, -1)  # Achata a saída
        vlad = torch.nn.functional.normalize(vlad, p=2, dim=1)  # Normalização L2
        return vlad
