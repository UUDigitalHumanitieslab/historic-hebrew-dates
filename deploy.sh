curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
sudo apt-add-repository 'deb https://dl.yarnpkg.com/debian/ stable main'
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y yarn python3 python3-pip
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10
python -v
pip -V
cd /vagrant
yarn
