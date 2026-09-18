import torch

class SDKPStateTensor:
    """
    Tracks continuous state dynamics for Position (P), Density (D), Kinematics (K),
    and Scale (S) across continuous inference execution passes.
    """
    def __init__(self, p_dim=3, d_dim=1, k_dim=3, s_dim=1, device="cpu"):
        self.device = device
        self.P = torch.zeros(1, p_dim, device=device, requires_grad=True)  # Trajectory history
        self.D = torch.ones(1, d_dim, device=device, requires_grad=True)   # Density / internal memory
        self.K = torch.zeros(1, k_dim, device=device, requires_grad=True)  # Kinematic response
        self.S = torch.tensor([[1.0]], device=device, requires_grad=True)  # Dynamic scale horizon

    def update_state(self, delta_p, residual_loss):
        """
        Executes online parameter updates: prediction errors increase state density (D),
        directly parameterizing the kinematic response (K).
        """
        with torch.no_grad():
            self.P += delta_p
            self.D += torch.abs(residual_loss) * 0.1
            self.K = delta_p / (self.D + 1e-8)
            
    def get_state_vector(self):
        return torch.cat([self.P, self.D, self.K, self.S], dim=-1)
