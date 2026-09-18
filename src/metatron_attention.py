import torch
import torch.nn as nn
from src.vortex_369 import Vortex369Compressor
from src.metatron_router import MetatronCubeRouter

class MetatronAttention(nn.Module):
    """
    Replaces standard O(N^2) multi-head self-attention with a deterministic 13-node
    Metatron graph topology modulated by 3-6-9 vortex invariants.
    """
    def __init__(self, embed_dim=64, num_nodes=13):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_nodes = num_nodes
        
        # Vertex projections into the 13 Metatron nodes
        self.node_proj = nn.Linear(embed_dim, embed_dim * num_nodes)
        self.out_proj = nn.Linear(embed_dim * num_nodes, embed_dim)
        
        self.router = MetatronCubeRouter(num_nodes=num_nodes)
        self.vortex = Vortex369Compressor()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x shape: [batch_size, seq_len, embed_dim]
        batch_size, seq_len, _ = x.shape
        
        # 1. Project sequence embeddings into 13-node vertex space
        vertex_feats = self.node_proj(x)
        vertex_feats = vertex_feats.view(batch_size, seq_len, self.num_nodes, self.embed_dim)
        
        # 2. Compress and balance features via 3-6-9 vortex invariants
        compressed = self.vortex.digital_root_compression(vertex_feats)
        balanced = self.vortex.balance_channels(compressed)
        
        # 3. Route features across the 78 interconnected edges of the K13 graph
        flat_feats = balanced.view(-1, self.embed_dim)
        routed = self.router.route_state(flat_feats)
        
        # 4. Collapse routing output back to standard embedding dimension
        routed_tensor = routed.view(batch_size, seq_len, self.num_nodes * self.embed_dim)
        return self.out_proj(routed_tensor)
