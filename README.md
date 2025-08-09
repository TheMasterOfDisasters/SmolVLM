# SmolVLM
I need eyes


## testing notes

    conda remove -n SmolVLM --all -y  
    conda create -n SmolVLM python=3.10 -y  
    conda activate SmolVLM  

    pip install torch==2.8.0+cu128 torchvision==0.23.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128
    pip install transformers
    pip install num2words
    pip install accelerate




    -------------------------

    pip install flash_attn-2.7.0.post2-cp310-cp310-win_amd64.whl

    pip install torchvision==0.23.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128
    pip install flash-attn --no-build-isolation

    
    pip install accelerate
    pip install bitsandbytes
    

  
    winget install --id=Task.Task -e  
    winget install --id=Curl.Curl  

    pip install torch==2.8.0+cu128 torchvision==0.23.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128
    pip install https://huggingface.co/lldacing/flash-attention-windows-wheel/resolve/main/flash_attn-2.7.4.post1%2Bcu128torch2.8.0cxx11abiTRUE-cp310-cp310-win_amd64.whl
    pip install https://huggingface.co/lldacing/flash-attention-windows-wheel/resolve/main/flash_attn-2.7.4.post1%2Bcu128torch2.7.0cxx11abiFALSE-cp310-cp310-win_amd64.whl
    pip install flash-attn --no-build-isolation

    pip install https://huggingface.co/lldacing/flash-attention-windows-wheel/resolve/main/flash_attn-2.7.4.post1+cu128torch2.8.0cxx11abiTRUE-cp310-cp310-win_amd64.whl


    python -c "import torch; print('Torch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version (built):', torch.version.cuda); print('Device name:', torch.cuda.get_device_name()); import flash_attn; print('Flash Attention version:', flash_attn.__version__)"



    python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"



    pip install transformers pillow nicegui fastapi uvicorn
    



    Check versions
    python -c "import sys; import torch; import platform; print(f'Python version: {sys.version}'); print(f'Python executable: {sys.executable}'); print(f'Platform: {platform.platform()}'); print(f'Torch version: {torch.__version__}'); print(f'Torch built CUDA: {torch.version.cuda}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')" && python -c "import importlib.util; print(f'FlashAttn installed: {importlib.util.find_spec(\"flash_attn\") is not None}')" && python -c "import importlib; importlib.import_module('flash_attn'); print('flash_attn import: OK')" && python -c "import importlib; importlib.import_module('flash_attn_2_cuda'); print('flash_attn_2_cuda import: OK')"
