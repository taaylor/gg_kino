#!/bin/sh

# Инициализация конфигурационного сервера
echo "Проверяем состояние конфигурационного сервера..."
if mongosh --host mongodb_cfg1 --eval "rs.status()" 2>&1 | grep -q "no replset config has been received"; then
    echo "Инициализируем конфигурационный сервер..."
    until mongosh --host mongodb_cfg1 --eval "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongodb_cfg1:27017\"}, {_id: 1, host: \"mongodb_cfg2:27017\"}, {_id: 2, host: \"mongodb_cfg3:27017\"}]})"; do
        echo "Ожидаем готовности конфигурации сервера..."
        sleep 5
    done
else
    echo "Конфигурационный сервер уже инициализирован"
fi

# Инициализация первого шарда
echo "Проверяем состояние первого шарда..."
if mongosh --host mongodb_sh1_rep1 --eval "rs.status()" 2>&1 | grep -q "no replset config has been received"; then
    echo "Инициализируем первый шард..."
    until mongosh --host mongodb_sh1_rep1 --eval "rs.initiate({_id: \"mongoshard1\", members: [{_id: 0, host: \"mongodb_sh1_rep1:27017\"}, {_id: 1, host: \"mongodb_sh1_rep2:27017\"}, {_id: 2, host: \"mongodb_sh1_rep3:27017\"}]})"; do
        echo "Ожидание готовности 1 шарда..."
        sleep 5
    done
else
    echo "Первый шард уже инициализирован"
fi

# Инициализация второго шарда
echo "Проверяем состояние второго шарда..."
if mongosh --host mongodb_sh2_rep1 --eval "rs.status()" 2>&1 | grep -q "no replset config has been received"; then
    echo "Инициализируем второй шард..."
    until mongosh --host mongodb_sh2_rep1 --eval "rs.initiate({_id: \"mongoshard2\", members: [{_id: 0, host: \"mongodb_sh2_rep1:27017\"}, {_id: 1, host: \"mongodb_sh2_rep2:27017\"}, {_id: 2, host: \"mongodb_sh2_rep3:27017\"}]})"; do
        echo "Ожидание готовности 2 шарда..."
        sleep 5
    done
else
    echo "Второй шард уже инициализирован"
fi

# Добавление шардов к роутеру
echo "Проверяем добавление первого шарда к роутеру..."
if ! mongosh --host mongodb_router --eval "sh.status()" 2>/dev/null | grep -q "mongoshard1"; then
    echo "Добавляем первый шард к роутеру..."
    until mongosh --host mongodb_router --eval "sh.addShard(\"mongoshard1/mongodb_sh1_rep1\")"; do
        echo "Ожидание добавления к роутеру 1 шарда..."
        sleep 5
    done
else
    echo "Первый шард уже добавлен к роутеру"
fi

echo "Проверяем добавление второго шарда к роутеру..."
if ! mongosh --host mongodb_router --eval "sh.status()" 2>/dev/null | grep -q "mongoshard2"; then
    echo "Добавляем второй шард к роутеру..."
    until mongosh --host mongodb_router --eval "sh.addShard(\"mongoshard2/mongodb_sh2_rep1\")"; do
        echo "Ожидание добавления к роутеру 2 шарда..."
        sleep 5
    done
else
    echo "Второй шард уже добавлен к роутеру"
fi

echo "Отображаем статус кластера:"
mongosh --host mongodb_router --eval "sh.status()"

echo "Настраиваем шардинг для базы данных и коллекций..."
mongosh mongodb_router:27017/${DB_NAME} --eval "
    // Проверяем, включен ли уже шардинг для базы данных
    var dbShardingEnabled = sh.status().databases.some(function(db) {
        return db._id === '${DB_NAME}' && db.partitioned === true;
    });

    if (!dbShardingEnabled) {
        print('Включаем шардинг для базы данных ${DB_NAME}...');
        sh.enableSharding('${DB_NAME}');
    } else {
        print('Шардинг для базы данных ${DB_NAME} уже включен');
    }

    // Создаем коллекции и настраиваем шардинг, если они еще не существуют
    var collections = ['${LIKE_COLL}', '${BOOKMARK_COLL}', '${REVIEWS_COLL}'];

    collections.forEach(function(collName) {
        var collExists = db.getCollectionNames().indexOf(collName) > -1;
        if (!collExists) {
            print('Создаем коллекцию ' + collName + '...');
            db.createCollection(collName);
        } else {
            print('Коллекция ' + collName + ' уже существует');
        }

        var shardedColls = sh.status().databases.find(function(db) {
            return db._id === '${DB_NAME}';
        });

        var isSharded = false;
        if (shardedColls && shardedColls.collections) {
            var fullCollName = '${DB_NAME}.' + collName;
            isSharded = Object.keys(shardedColls.collections).indexOf(fullCollName) > -1;
        }

        if (!isSharded) {
            print('Настраиваем шардинг для коллекции ' + collName + '...');
            sh.shardCollection('${DB_NAME}.' + collName, {'film_id': 'hashed'});
        } else {
            print('Коллекция ' + collName + ' уже шардирована');
        }
    });
"

echo "Кластер успешно сконфигурирован"
