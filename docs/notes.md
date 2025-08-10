# Development Notes

## Version Management
`git tag v0.0.2`  
`git push origin v0.0.2`

## Docker Usage

### GPU Version
`docker run --gpus all -p 8888:8888 sensejworld/smolvlm`



## Test locally

### Build image
You need docker to be working. (Example : Docker Desktop)  
`docker build -t smolvlm:test .`

### Docker Run
`docker run --gpus all -p 8888:8888 smolvlm:test`

### Connect to image without run
`docker run --rm -it --entrypoint /bin/bash smolvlm:test`


## Conda setup

    conda remove -n SmolVLM --all -y
    conda create -n SmolVLM python=3.10 -y

    conda activate SmolVLM

    pip install torch==2.8.0+cu128 torchvision==0.23.0+cu128 torchaudio==2.8.0+cu128 --index-url https://download.pytorch.org/whl/cu128
    pip install transformers
    pip install num2words
    pip install accelerate
    pip install gradio

    // Flash attention might be missing, its ok for local windows version. But docker should contain it.
    python -c "import torch; print('Torch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version (built):', torch.version.cuda); print('Device name:', torch.cuda.get_device_name()); import flash_attn; print('Flash Attention version:', flash_attn.__version__)"
    python -c "import sys; import torch; import platform; print(f'Python version: {sys.version}'); print(f'Python executable: {sys.executable}'); print(f'Platform: {platform.platform()}'); print(f'Torch version: {torch.__version__}'); print(f'Torch built CUDA: {torch.version.cuda}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')" && python -c "import importlib.util; print(f'FlashAttn installed: {importlib.util.find_spec(\"flash_attn\") is not None}')" && python -c "import importlib; importlib.import_module('flash_attn'); print('flash_attn import: OK')" && python -c "import importlib; importlib.import_module('flash_attn_2_cuda'); print('flash_attn_2_cuda import: OK')"

## Testing

### API
    :: Standard call
    curl -X POST "http://localhost:8888/ptt/convert" ^
    -H "Accept: application/json" ^
    -F "query=What is in this image?" ^
    -F "image=@"X:\sandbox\git\SmolVLM\app\images\cat.jpg";type=image/jpeg"

    :: Default image
    curl -X POST "http://localhost:8888/ptt/convert" ^
    -H "Accept: application/json" ^
    -F "query=Count cats in the image?"

    :: Health
    curl "http://localhost:8888/health"

### UI 
    http://localhost:8888/