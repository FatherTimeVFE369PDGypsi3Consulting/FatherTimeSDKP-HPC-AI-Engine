import torch
import torch.nn as nn

class SDKPLoss(nn.Module):
    """
    SDKP Framework Dynamic Trajectory & Residual Loss Function.
    Calculates physical trajectory error (P), density-weighted memory decay (D),
    and 3-6-9 modulo-9 equilibrium conservation penalties.
    """
    def __init__(self, gamma=0.1, lambda_vortex=0.05):
        super().__init__()
        self.gamma = gamma
        self.lambda_vortex = lambda_vortex
        self.mse = nn.MSELoss()

    def forward(
        self, 
        pred_trajectory: torch.Tensor, 
        target_trajectory: torch.Tensor, 
        density: torch.Tensor, 
        vortex_state: torch.Tensor
    ) -> tuple[torch.Tensor, dict]:
        # 1. Physical Trajectory Error (Delta P)
        traj_loss = self.mse(pred_trajectory, target_trajectory)
        
        # 2. Density Memory Regularization (Inversely penalizes density collapse)
        density_loss = self.gamma / (torch.mean(torch.abs(density)) + 1e-8)
        
        # 3. Vortex Equilibrium Penalty (Deviation from 3-6-9 conservation anchor at 0.5)
        vortex_loss = self.lambda_vortex * torch.abs(torch.mean(vortex_state) - 0.5)
        
        total_loss = traj_loss + density_loss + vortex_loss
        
        metrics = {
            "total_loss": total_loss.item(),
            "trajectory_mse": traj_loss.item(),
            "density_penalty": density_loss.item(),
            "vortex_penalty": vortex_loss.item()
        }
        
        return total_loss, metrics
