#!/bin/bash

# ML Learner Production Deployment Script
# This script sets up the production environment on a Ubuntu/Debian server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - Change these as needed
PROJECT_NAME="ml-learner"
DOMAIN_NAME="your-domain.com"  # Replace with your actual domain
PROJECT_PATH="/var/www/$PROJECT_NAME"
SERVICE_USER="www-data"

echo -e "${GREEN}🚀 Starting ML Learner Production Deployment${NC}"
echo "================================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   exit 1
fi

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install required packages
echo -e "${YELLOW}📦 Installing required packages...${NC}"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    mysql-server \
    mysql-client \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    build-essential \
    libmysqlclient-dev \
    pkg-config

# Install gunicorn globally for systemd
pip3 install gunicorn

# Create project directory
echo -e "${YELLOW}📁 Creating project directory...${NC}"
mkdir -p $PROJECT_PATH
chown $SERVICE_USER:$SERVICE_USER $PROJECT_PATH

# Clone or copy project (assuming you're running this from project directory)
if [ -f "README.md" ]; then
    echo -e "${YELLOW}📋 Copying project files...${NC}"
    cp -r . $PROJECT_PATH/
else
    echo -e "${YELLOW}📥 Cloning project from GitHub...${NC}"
    # Replace with your actual GitHub repository URL
    git clone https://github.com/yourusername/ml-learner.git $PROJECT_PATH
fi

cd $PROJECT_PATH
chown -R $SERVICE_USER:$SERVICE_USER .

# Setup Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
su - $SERVICE_USER -c "cd $PROJECT_PATH/backend && python3 -m venv venv"
su - $SERVICE_USER -c "cd $PROJECT_PATH/backend && source venv/bin/activate && pip install -r requirements.txt"

# Install additional production dependencies
su - $SERVICE_USER -c "cd $PROJECT_PATH/backend && source venv/bin/activate && pip install gunicorn pymysql"

# Setup database
echo -e "${YELLOW}🗄️ Setting up MySQL database...${NC}"
mysql -e "CREATE DATABASE IF NOT EXISTS ml_learner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'ml_user'@'localhost' IDENTIFIED BY 'your_secure_password_here';"
mysql -e "GRANT ALL PRIVILEGES ON ml_learner.* TO 'ml_user'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Import database dump if it exists
if [ -f "database_backup/*.sql" ]; then
    echo -e "${YELLOW}📤 Importing database...${NC}"
    DB_DUMP_FILE=$(ls database_backup/*.sql | head -1)
    mysql ml_learner < $DB_DUMP_FILE
fi

# Build frontend
echo -e "${YELLOW}🎨 Building frontend...${NC}"
cd frontend
npm install
npm run build
cd ..

# Setup environment variables
echo -e "${YELLOW}🔧 Setting up environment variables...${NC}"
cp env.production.template .env.production
# Note: You need to manually edit .env.production with your actual values

# Setup systemd service
echo -e "${YELLOW}⚙️ Setting up systemd service...${NC}"
cp ml-learner.service /etc/systemd/system/
# Update paths in service file
sed -i "s|/path/to/your/project|$PROJECT_PATH|g" /etc/systemd/system/ml-learner.service
systemctl daemon-reload
systemctl enable ml-learner
systemctl start ml-learner

# Setup nginx
echo -e "${YELLOW}🌐 Setting up Nginx...${NC}"
cp nginx.conf /etc/nginx/sites-available/$PROJECT_NAME
# Update paths in nginx config
sed -i "s|/path/to/your/project/frontend/dist|$PROJECT_PATH/frontend/dist|g" /etc/nginx/sites-available/$PROJECT_NAME
sed -i "s|your-domain.com|$DOMAIN_NAME|g" /etc/nginx/sites-available/$PROJECT_NAME

ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Setup firewall (if ufw is available)
if command -v ufw &> /dev/null; then
    echo -e "${YELLOW}🔥 Setting up firewall...${NC}"
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw --force enable
fi

# Setup SSL certificate (optional)
read -p "Do you want to setup SSL certificate with Let's Encrypt? (y/n): " setup_ssl
if [[ $setup_ssl =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
    certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${GREEN}🌐 Your application should be available at:${NC}"
echo "  http://$DOMAIN_NAME"
if [[ $setup_ssl =~ ^[Yy]$ ]]; then
    echo "  https://$DOMAIN_NAME"
fi
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Edit $PROJECT_PATH/.env.production with your actual database password and secret key"
echo "2. Restart the service: systemctl restart ml-learner"
echo "3. Check logs: journalctl -u ml-learner -f"
echo "4. Test the application: curl http://localhost/health"
echo ""
echo -e "${YELLOW}🔧 Useful commands:${NC}"
echo "  Start service: systemctl start ml-learner"
echo "  Stop service: systemctl stop ml-learner"
echo "  Restart service: systemctl restart ml-learner"
echo "  Check status: systemctl status ml-learner"
echo "  View logs: journalctl -u ml-learner -f"
