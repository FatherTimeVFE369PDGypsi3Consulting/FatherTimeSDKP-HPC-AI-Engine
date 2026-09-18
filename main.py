import yaml
import torch
from src.sdkp_tensor import SDKPStateTensor
from src.vortex_369 import Vortex369Compressor
from src.metatron_router import MetatronCubeRouter
from src.metatron_attention import MetatronAttention
from src.dcp_provenance import DigitalCrystalProtocol

def run_father_time_hpc():
    with open("config/params.yaml", "r") as f:
        params = yaml.safe_load(f)

    print("=== Initializing FatherTimeHPC Native AI Engine ===")
    
    # 1. SDKP Continuous State Tensor (P, D, K, S)
    state_engine = SDKPStateTensor()
    current_state = state_engine.get_state_vector()
    print(f"SDKP State Vector: {current_state.detach().numpy()}")

    # 2. Framework-Native Unified Vortex Engine
    vortex = Vortex369Compressor(
        modulus=params['vortex_369']['modulus'],
        default_scale=params['sdkp']['scale_factor']
    )
    
    # Apply SDKP scale laws, QCC density gating (D), and modulo-9 balance
    compressed_state = vortex(
        current_state, 
        density=state_engine.D, 
        scale=state_engine.S
    )
    print(f"SDKP Multi-Scale Vortex State: {compressed_state.detach().numpy()}")

    # 3. Metatron 13-Node Geometric Attention Pass
    seq_tokens = torch.randn(1, 8, 64)  # [batch_size=1, seq_len=8, embed_dim=64]
    attn_layer = MetatronAttention(embed_dim=64, num_nodes=params['metatron']['num_nodes'])
    attn_output = attn_layer(seq_tokens)
    print(f"Metatron Attention Output Shape: {attn_output.shape}")

    # 4. Digital Crystal Protocol (DCP) Provenance Stamp
    dcp = DigitalCrystalProtocol(
        author=params['dcp']['author'], 
        orcid=params['dcp']['orcid']
    )
    ledger_hash = dcp.generate_crystal_hash({
        "sdkp_state": current_state.detach().tolist(),
        "scale_factor": params['sdkp']['scale_factor']
    })
    print(f"DCP Cryptographic Ledger Hash: {ledger_hash}")

if __name__ == "__main__":
    run_father_time_hpc()
