export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install jq -y

# docker-plgin
apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Install Node.js and npm using NodeSource (same as rsot-for-k8s)
apt-get install -y curl
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Clean install to ensure all packages are properly installed
rm -rf node_modules package-lock.json
npm install

bash create_dist.sh

