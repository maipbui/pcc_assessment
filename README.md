# PCC Assessment: Point Cloud Compression Assessment
## Tested Environment
Ubuntu 20.04.3 LTS
## Requirements
### Installation
0. Install basic prerequisites:
```shell
sudo apt install git gcc g++ cmake subversion xvfb libblas-dev libatlas-base-dev nvidia-cuda-toolkit -y
```
1. Install Anaconda: https://www.anaconda.com/products/individual#linux
2. Install traditional PCC Algorithms: Draco, GPCC, VPCC
```shell
cd [root]
mkdir build
cd build
cmake ..
make
```
3. Install separate Conda environment for neural network-based PCC algorithms where ```{PCC_name}``` is the name of PCC algorithm. The env config files can be found under ```[root]/env``` folder: 
```shell
cd [root]
conda env create -f env/{PCC_name}.yml
```
4. To activate installed Conda environment for neural network-based PCC algorithms: 
```shell
conda activate {PCC_name}
```

## Acknowledgement
Thank you and credits to [xtorker](https://github.com/xtorker/PCCArena) for part of the easy-to-use Anaconda environment configs `env`
