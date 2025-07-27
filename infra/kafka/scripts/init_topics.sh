#!/bin/sh

until /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-0:9092 --list; do
    echo 'Waiting for Kafka to be ready...'; sleep 5;
done

EXISTING_TOPICS=$(/opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-0:9092 --list)

echo "Existing topics: $EXISTING_TOPICS"
echo "KAFKA_LIKE_TOPIC: $KAFKA_LIKE_TOPIC"
echo "KAFKA_COMMENT_TOPIC: $KAFKA_COMMENT_TOPIC"
echo "KAFKA_WATCH_PROGRESS_TOPIC: $KAFKA_WATCH_PROGRESS_TOPIC"
echo "KAFKA_WATCH_LIST_TOPIC: $KAFKA_WATCH_LIST_TOPIC"
echo "KAFKA_OTHER_TOPIC: $KAFKA_OTHER_TOPIC"
echo "KAFKA_REC_BOOKMARKS_LIST_TOPIC: $KAFKA_REC_BOOKMARKS_LIST_TOPIC"
echo "KAFKA_REC_RATINGS_FILMS_TOPIC: $KAFKA_REC_RATINGS_FILMS_TOPIC"

TOPICS="$KAFKA_LIKE_TOPIC $KAFKA_COMMENT_TOPIC $KAFKA_WATCH_PROGRESS_TOPIC $KAFKA_WATCH_LIST_TOPIC $KAFKA_OTHER_TOPIC $KAFKA_REC_BOOKMARKS_LIST_TOPIC $KAFKA_REC_RATINGS_FILMS_TOPIC"

echo "Topics list: $TOPICS"

for topic in $TOPICS; do
    if [ -z "$topic" ]; then
        echo "Topic variable is empty, skipping.";
        continue;
    fi;
    if ! echo "$EXISTING_TOPICS" | grep -qw "$topic"; then
        echo "Creating topic $topic";
        /opt/bitnami/kafka/bin/kafka-topics.sh --create --bootstrap-server kafka-0:9092 --topic "$topic" --partitions 3 --replication-factor 2 --config delete.retention.ms=3600000 || echo "Failed to create topic $topic";
    else
        echo "Topic $topic already exists, skipping creation.";
    fi;
done

echo "Final topic list:"
/opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka-0:9092 --list
