import yaml
import torch
from src.sdkp_tensor import SDKPStateTensor
from src.vortex_369 import Vortex369Compressor
from src.metatron_router import MetatronCubeRouter
from src.metatron_attention import MetatronAttention
from src.sdkp_loss import SDKPLoss
from src.dcp_provenance import DigitalCrystalProtocol

def run_father_time_hpc():
    with open("config/params.yaml", "r") as f:
        params = yaml.safe_load(f)

    print("=== Initializing FatherTimeHPC Native AI Engine ===")
    
    # 1. SDKP Continuous State Initialization
    state_engine = SDKPStateTensor()
    current_state = state_engine.get_state_vector()
    print(f"Initial SDKP State Vector: {current_state.detach().numpy()}")

    # 2. Vortex Compression & Attention Pass
    vortex = Vortex369Compressor(
        modulus=params['vortex_369']['modulus'],
        default_scale=params['sdkp']['scale_factor']
    )
    compressed_state = vortex(current_state, density=state_engine.D, scale=state_engine.S)
    
    seq_tokens = torch.randn(1, 8, 64)
    attn_layer = MetatronAttention(embed_dim=64, num_nodes=params['metatron']['num_nodes'])
    attn_output = attn_layer(seq_tokens)

    # 3. Dynamic Residual Loss Calculation & Real-Time Density Update
    loss_fn = SDKPLoss(gamma=params['sdkp']['gamma'])
    target_trajectory = torch.zeros_like(state_engine.P)
    
    total_loss, metrics = loss_fn(
        pred_trajectory=state_engine.P, 
        target_trajectory=target_trajectory, 
        density=state_engine.D, 
        vortex_state=compressed_state
    )
    
    # Plasticity Step: Residual error alters memory density (D) in real time
    state_engine.update_state(delta_p=torch.tensor([[0.05, -0.02, 0.01]]), residual_loss=total_loss)
    updated_state = state_engine.get_state_vector()
    print(f"Updated SDKP State Vector (Post-Inference Density D): {updated_state.detach().numpy()}")
    print(f"Execution Metrics: {metrics}")

    # 4. DCP Cryptographic Stamp
    dcp = DigitalCrystalProtocol(author=params['dcp']['author'], orcid=params['dcp']['orcid'])
    ledger_hash = dcp.generate_crystal_hash({
        "sdkp_state": updated_state.detach().tolist(),
        "metrics": metrics
    })
    print(f"DCP Cryptographic Ledger Hash: {ledger_hash}")

if __name__ == "__main__":
    run_father_time_hpc()
