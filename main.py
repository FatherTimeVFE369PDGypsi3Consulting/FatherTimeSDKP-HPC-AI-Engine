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

    print("=== Initializing FatherTimeHPC AI Engine ===")
    
    # 1. SDKP State Tensor
    state_engine = SDKPStateTensor()
    current_state = state_engine.get_state_vector()
    print(f"SDKP State Vector: {current_state.detach().numpy()}")

    # 2. Metatron Geometric Attention Pass
    seq_tokens = torch.randn(1, 8, 64) # Batch size 1, Sequence length 8, Embed dim 64
    attn_layer = MetatronAttention(embed_dim=64, num_nodes=params['metatron']['num_nodes'])
    attn_output = attn_layer(seq_tokens)
    print(f"Metatron Attention Output Shape: {attn_output.shape}")

    # 3. DCP Provenance Logging
    dcp = DigitalCrystalProtocol(
        author=params['dcp']['author'], 
        orcid=params['dcp']['orcid']
    )
    ledger_hash = dcp.generate_crystal_hash({"sdkp_state": current_state.detach().tolist()})
    print(f"DCP Ledger Hash: {ledger_hash}")

if __name__ == "__main__":
    run_father_time_hpc()
