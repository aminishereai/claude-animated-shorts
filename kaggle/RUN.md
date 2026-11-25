# Kaggle GPU render test (needs KAGGLE_USERNAME / KAGGLE_KEY in env; hosts www.kaggle.com + storage.googleapis.com allowed)
pip install kaggle
tar xzf /mnt/project-files/animated-shorts-eval/render-farm-staging.tgz -C ~/farm   # mkdir ~/farm first
# 1. upload render/ (without node_modules) as private dataset 3dio-render-src
cd ~/farm/render && printf '{"title":"3dio-render-src","id":"%s/3dio-render-src","licenses":[{"name":"CC0-1.0"}]}' $KAGGLE_USERNAME > dataset-metadata.json
kaggle datasets create -p . --dir-mode zip -r zip     # later: kaggle datasets version -p . -m update --dir-mode zip
# 2. push the GPU script (replace KAGGLE_USERNAME in kernel-metadata.json first)
cd ~/farm/kaggle && sed -i "s/KAGGLE_USERNAME/$KAGGLE_USERNAME/g" kernel-metadata.json && kaggle kernels push -p .
# 3. poll + fetch
kaggle kernels status $KAGGLE_USERNAME/3dio-gpu-render ; kaggle kernels output $KAGGLE_USERNAME/3dio-gpu-render -p out
# Note: --dir-mode zip uploads folders zipped; if Kaggle doesn't unzip public/bridge/kenney, tar the folder instead and untar in render_gpu.py.
