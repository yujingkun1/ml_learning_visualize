#!/bin/bash

# Database export script for ML Learner project
# This script exports the MySQL database to a SQL file for deployment

# Database configuration (using the same env vars as the app)
DB_USER=${DATABASE_USER:-ml_user}
DB_PASSWORD=${DATABASE_PASSWORD:-'Yjk381088#'}
DB_HOST=${DATABASE_HOST:-127.0.0.1}
DB_PORT=${DATABASE_PORT:-3306}
DB_NAME=${DATABASE_NAME:-ml_learner}

# Output file
OUTPUT_FILE="ml_learner_database_$(date +%Y%m%d_%H%M%S).sql"
BACKUP_DIR="database_backup"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "Exporting MySQL database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "Output file: $BACKUP_DIR/$OUTPUT_FILE"

# Export database using mysqldump (simplified version)
mysqldump \
  --user=$DB_USER \
  --password=$DB_PASSWORD \
  --host=$DB_HOST \
  --port=$DB_PORT \
  $DB_NAME \
  --no-tablespaces \
  > $BACKUP_DIR/$OUTPUT_FILE

if [ $? -eq 0 ]; then
    echo "✅ Database export completed successfully!"
    echo "📁 Backup file: $BACKUP_DIR/$OUTPUT_FILE"
    echo ""
    echo "To restore on the server, run:"
    echo "mysql -u [username] -p < $BACKUP_DIR/$OUTPUT_FILE"
else
    echo "❌ Database export failed!"
    exit 1
fi

# Create a compressed version
echo "Creating compressed backup..."
gzip -c $BACKUP_DIR/$OUTPUT_FILE > $BACKUP_DIR/$OUTPUT_FILE.gz

if [ $? -eq 0 ]; then
    echo "✅ Compressed backup created: $BACKUP_DIR/$OUTPUT_FILE.gz"
fi

echo ""
echo "Database export process completed."
