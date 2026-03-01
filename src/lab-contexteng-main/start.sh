#!/bin/bash

: ${DOMAIN?"Please provide domain in DOMAIN env variable.  This will be the domain used for provisioned vms. For localhost use 'nip.io': 'export DOMAIN=\"nip.io\"'"}
: ${HOSTNAME?"Please provide vm hostname HOSTNAME env variable. For localhost use '127.0.0.1': 'export HOSTNAME=\"127.0.0.1\"'"}

export DOMAIN=$DOMAIN
export HOSTNAME=$HOSTNAME
export HOST_IP=$(hostname -I | awk '{print $1}')

export LITELLM_MASTER_KEY=sk-super-secret-key-for-ps

if [[ -n $VERTEX_SA_KEY ]];
then
  echo $VERTEX_SA_KEY > vertex_sa_in.txt
  cat vertex_sa_in.txt | base64 -d > vertex_sa.json
  if [ $? -ne 0 ]; then
     mv vertex_sa_in.txt vertex_sa.json
  fi
  rm vertex_sa_in.txt
fi

docker-compose up -d --scale jupyter=0 --scale docs=0

sudo docker exec litellm wget 'http://localhost:4000/key/generate' \
--header "Authorization: Bearer $LITELLM_MASTER_KEY" \
--header 'Content-Type: application/json' \
--post-data '{"max_budget":1}'

sudo docker cp litellm:/app/generate .

export LITELLM_API_KEY=$(cat generate | jq '.key' | tr -d '"')

docker-compose up -d jupyter docs

wait $!
