import torch
import torch.nn as nn
import networkx as nx

class MetatronCubeRouter(nn.Module):
    """
    Routes tensor evaluations across a 13-node complete graph topology (K13)
    with 78 interconnected edges using dynamic device alignment and einsum routing.
    """
    def __init__(self, num_nodes=13):
        super().__init__()
        self.num_nodes = num_nodes
        
        # Construct K13 complete graph topology (13 nodes, 78 edges)
        graph = nx.complete_graph(num_nodes)
        adj_matrix = torch.tensor(nx.to_numpy_array(graph), dtype=torch.float32)
        
        # Register buffer so PyTorch auto-moves adjacency matrix to GPU/CPU with the model
        self.register_buffer("adjacency_matrix", adj_matrix)

    def route_state(self, state_vector: torch.Tensor) -> torch.Tensor:
        adj = self.adjacency_matrix.to(device=state_vector.device, dtype=state_vector.dtype)
        
        if state_vector.dim() == 2:
            node_states = state_vector.unsqueeze(1).repeat(1, self.num_nodes, 1)
            return torch.einsum('ij, bjf -> bif', adj, node_states) / self.num_nodes
        elif state_vector.dim() == 4:
            # Multi-dimensional routing for sequence tokens: [batch_size, seq_len, num_nodes, embed_dim]
            return torch.einsum('ij, bsjf -> bsif', adj, state_vector) / self.num_nodes
        else:
            return torch.einsum('ij, bjf -> bif', adj, state_vector) / self.num_nodes

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.route_state(x)
