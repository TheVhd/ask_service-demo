#!/bin/bash

echo "Waiting for MongoDB to start..."
until mongosh admin --host localhost --port 27017 --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --eval "print(\"waited for connection\")" &>/dev/null; do
    sleep 2
done

echo "Creating MongoDB users..."

mongosh admin --host localhost --port 27017 --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --eval "
    db = db.getSiblingDB('lmxai_llm_ask');
    if (!db.getUser('ask_mongo')) {
        db.createUser({
            user: 'ask_mongo',
            pwd: 'lmxai_ask',
            roles: [{ role: 'readWrite', db: 'lmxai_llm_ask' }]
        });
        print('Ask user created successfully.');
    } else {
        print('Ask user already exists.');
    }
"

echo "MongoDB users creation process completed."
