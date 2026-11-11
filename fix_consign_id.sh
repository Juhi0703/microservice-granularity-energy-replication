#!/bin/bash
# Train Ticket creates its consign-price config with a new random id at every start.
# locust_3.py sends the authors' fixed id, so every consignprice POST failed with HTTP 500
# (authors' README, DEBUG: "change the id of task23"). This copies the current id from MySQL
# into loadtesting/locust_3.py. Run inside a train_system/<granularity> folder, services up.
id=$(docker compose exec -T ts-price-mysql mysql -uroot -pAbc123% ts -N -B -e "SELECT id FROM consign_price WHERE idx=0 LIMIT 1;" 2>/dev/null | tr -d '\r')
if [[ $id =~ ^[0-9a-f-]{36}$ ]]; then
  sed -i -E "s/\"id\": \"[0-9a-f-]{36}\"/\"id\": \"$id\"/" loadtesting/locust_3.py
  echo "consignprice id set to $id in loadtesting/locust_3.py"
else
  echo "WARNING: could not read the consign_price id from MySQL; consignprice requests will fail"
fi
