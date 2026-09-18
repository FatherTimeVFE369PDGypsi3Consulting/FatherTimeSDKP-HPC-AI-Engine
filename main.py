import yaml
import torch
from src.sdkp_tensor import SDKPStateTensor
from src.vortex_369 import Vortex369Compressor
from src.metatron_router import MetatronCubeRouter
from src.dcp_provenance import DigitalCrystalProtocol

def run_father_time_hpc():
    with open("config/params.yaml", "r") as f:
        params = yaml.safe_load(f)

    print("=== Initializing FatherTimeHPC AI Engine ===")
    
    # 1. State Vector Initialization
    state_engine = SDKPStateTensor()
    current_state = state_engine.get_state_vector()
    print(f"SDKP State Vector (P, D, K, S): {current_state.detach().numpy()}")

    # 2. Vortex Compression & Dual-Channel Balance
    vortex = Vortex369Compressor(modulus=params['vortex_369']['modulus'])
    compressed = vortex.digital_root_compression(current_state)
    balanced = vortex.balance_channels(compressed)
    print(f"3-6-9 Vortex Compressed State: {balanced.numpy()}")

    # 3. Metatron Graph Routing (K13 Topology)
    router = MetatronCubeRouter(num_nodes=params['metatron']['num_nodes'])
    graph_output = router.route_state(balanced)
    print(f"Metatron 13-Node Graph Tensor Shape: {graph_output.shape}")

    # 4. DCP Cryptographic Provenance Stamp
    dcp = DigitalCrystalProtocol(
        author=params['dcp']['author'], 
        orcid=params['dcp']['orcid']
    )
    ledger_hash = dcp.generate_crystal_hash({"sdkp_state": current_state.detach().tolist()})
    print(f"DCP Ledger Hash: {ledger_hash}")

if __name__ == "__main__":
    run_father_time_hpc()
