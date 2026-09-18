import torch
import torch.nn as nn

class Vortex369Compressor(nn.Module):
    """
    SDKP Framework Unified Compression Engine integrating:
    1. SDKP Scale Law (S factor = 8046602.01)
    2. Density-Weighted Quantum Causal Compression (QCC via state density D)
    3. Modulo-9 Vortex Cyclic Invariants (Z9) with GPU/device awareness
    4. Dual-channel (3 <-> 6) energy balancing anchored at 9
    """
    def __init__(self, modulus=9, default_scale=8046602.01):
        super().__init__()
        self.modulus = modulus
        self.default_scale = default_scale

    def apply_sdkp_scale_law(self, tensor: torch.Tensor, scale_horizon: torch.Tensor = None) -> torch.Tensor:
        s_val = scale_horizon if scale_horizon is not None else torch.tensor(self.default_scale, device=tensor.device)
        scale_factor = torch.log1p(torch.abs(s_val))
        return tensor / (scale_factor + 1e-8)

    def apply_density_qcc_gate(self, tensor: torch.Tensor, density: torch.Tensor = None) -> torch.Tensor:
        if density is None:
            return tensor
        density_weight = torch.sigmoid(density)
        return tensor * density_weight

    def digital_root_compression(self, tensor: torch.Tensor) -> torch.Tensor:
        scaled_int = torch.abs(tensor * 1000.0).to(torch.int64)
        digital_root = torch.fmod(scaled_int, self.modulus)
        
        # Explicit device and dtype inheritance to prevent CUDA/CPU device errors
        nine_tensor = torch.tensor(9, dtype=torch.int64, device=tensor.device)
        digital_root = torch.where(digital_root == 0, nine_tensor, digital_root)
        
        return digital_root.to(dtype=tensor.dtype, device=tensor.device) / self.modulus

    def balance_channels(self, state_tensor: torch.Tensor) -> torch.Tensor:
        ch3 = state_tensor * (3.0 / 9.0)
        ch6 = state_tensor * (6.0 / 9.0)
        return (ch3 + ch6) / 2.0

    def forward(self, tensor: torch.Tensor, density: torch.Tensor = None, scale: torch.Tensor = None) -> torch.Tensor:
        scaled = self.apply_sdkp_scale_law(tensor, scale)
        qcc_gated = self.apply_density_qcc_gate(scaled, density)
        mod_compressed = self.digital_root_compression(qcc_gated)
        return self.balance_channels(mod_compressed)
