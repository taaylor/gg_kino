#!/bin/sh

until mongosh --host mongodb_cfg1 --eval "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongodb_cfg1:27017\"}, {_id: 1, host: \"mongodb_cfg2:27017\"}, {_id: 2, host: \"mongodb_cfg3:27017\"}]})"; do
    echo "Ожидаем готовности конфигурации сервера..."
    sleep 5
done

until mongosh --host mongodb_sh1_rep1 --eval "rs.initiate({_id: \"mongoshard1\", members: [{_id: 0, host: \"mongodb_sh1_rep1:27017\"}, {_id: 1, host: \"mongodb_sh1_rep2:27017\"}, {_id: 2, host: \"mongodb_sh1_rep3:27017\"}]})"; do
    echo "Ожидание готовности 1 шарда..."
    sleep 5
done

until mongosh --host mongodb_sh2_rep1 --eval "rs.initiate({_id: \"mongoshard2\", members: [{_id: 0, host: \"mongodb_sh2_rep1:27017\"}, {_id: 1, host: \"mongodb_sh2_rep2:27017\"}, {_id: 2, host: \"mongodb_sh2_rep3:27017\"}]})"; do
    echo "Ожидание готовности 2 шарда..."
    sleep 5
done

until mongosh --host mongodb_router --eval "sh.addShard(\"mongoshard1/mongodb_sh1_rep1\")"; do
    echo "Ожидание добавления к роутеру 1 шарда..."
    sleep 5
done

until mongosh --host mongodb_router --eval "sh.addShard(\"mongoshard2/mongodb_sh2_rep1\")"; do
    echo "Ожидание добавления к роутеру 2 шарда..."
    sleep 5
done

mongosh --host mongodb_router --eval "sh.status()"

mongosh mongodb_router:27017/kinoservice --eval "sh.enableSharding('kinoservice')
    && db.createCollection('likeCollection')
    && db.createCollection('bookmarkCollection')
    && db.createCollection('reviewsCollection')
    && sh.shardCollection('kinoservice.likeCollection', {'film_id': 'hashed'})
    && sh.shardCollection('kinoservice.bookmarkCollection', {'film_id': 'hashed'})
    && sh.shardCollection('kinoservice.reviewsCollection', {'film_id': 'hashed'})
    "
