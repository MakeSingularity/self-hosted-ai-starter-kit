GPU Setup (Conda)

1) Determine your local CUDA toolkit/runtime version (e.g., `nvidia-smi` on systems with NVIDIA GPUs).
2) Edit `environment.yml` if you need to pin a different `pytorch-cuda` version to match your drivers.
3) Create the environment (fresh):

   conda env create -f environment.yml

4) Or update an existing `oliver` environment to match the spec:

   conda env update -n oliver -f environment.yml --prune

5) Activate and verify:

   conda activate oliver
   python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"

Notes:

- If you need a different PyTorch build (e.g., MPS for macOS), change channels and package spec accordingly.
- The `environment.yml` uses `pip: -r requirements.txt` to ensure project pip packages are installed after conda packages.
- For reproducibility, commit `environment.yml` so others can recreate the same GPU-capable env.
