#!/bin/bash

set -e

echo "=== Configurando PetClinic Application ==="

# Update system silently
export DEBIAN_FRONTEND=noninteractive
echo "Atualizando sistema..."
apt-get update > /dev/null 2>&1
apt-get upgrade -y > /dev/null 2>&1

# Install Java 17 (OpenJDK)
echo "Instalando Java 17..."
apt-get install -y openjdk-17-jdk curl wget > /dev/null 2>&1

# Install Node.js 18 LTS
echo "Instalando Node.js 18..."
curl -fsSL https://deb.nodesource.com/setup_18.x 2>/dev/null | bash - > /dev/null 2>&1
apt-get install -y nodejs > /dev/null 2>&1

# Install Maven
echo "Instalando Maven..."
apt-get install -y maven > /dev/null 2>&1

# Verificar versões
echo "Versões instaladas:"
java -version
node --version
npm --version
mvn --version

# Set JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> /home/vagrant/.bashrc
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> /home/vagrant/.bashrc

# Aguardar PostgreSQL estar disponível (local)
echo "Aguardando PostgreSQL estar disponível..."
until nc -z localhost 5432; do
  echo "Aguardando PostgreSQL..."
  sleep 5
done
echo "PostgreSQL está disponível!"

# Change to application directory
cd /opt/petclinic

# Change ownership to vagrant user
chown -R vagrant:vagrant /opt/petclinic

# Make Maven wrapper executable and fix Windows line endings
chmod +x mvnw
# Fix potential Windows line endings in mvnw script
sed -i 's/\r$//' mvnw

# Build as vagrant user
echo "Compilando aplicação PetClinic (isso pode demorar alguns minutos)..."
sudo -u vagrant bash -c "
  export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
  export PATH=\$PATH:\$JAVA_HOME/bin
  cd /opt/petclinic
  
  # Clean and package (skip tests for faster build) - silent mode
  ./mvnw clean package -DskipTests -Dmaven.test.skip=true -q > /dev/null 2>&1
" 

# Verificar se o JAR foi criado
if [ ! -f target/*.jar ]; then
    echo "ERRO: JAR não foi criado."
    echo "Tentando compilar novamente com output visível para debug..."
    sudo -u vagrant bash -c "
      export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
      export PATH=\$PATH:\$JAVA_HOME/bin
      cd /opt/petclinic
      ./mvnw clean package -DskipTests -Dmaven.test.skip=true
    "
    exit 1
fi

echo "✅ Build concluído com sucesso!"

# Create systemd service for PetClinic
echo "Criando serviço systemd..."
cat > /etc/systemd/system/petclinic.service <<EOF
[Unit]
Description=Spring PetClinic Application
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=vagrant
Group=vagrant
WorkingDirectory=/opt/petclinic
Environment=JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
Environment=PATH=/usr/lib/jvm/java-17-openjdk-amd64/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=SPRING_PROFILES_ACTIVE=postgres
Environment=POSTGRES_URL=jdbc:postgresql://localhost:5432/petclinic
Environment=POSTGRES_USER=petclinic
Environment=POSTGRES_PASS=petclinic
ExecStart=/usr/lib/jvm/java-17-openjdk-amd64/bin/java -Xmx1g -jar target/spring-petclinic-3.2.0-SNAPSHOT.jar --server.port=8080 --server.address=0.0.0.0
ExecStop=/bin/kill -15 \$MAINPID
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal
SyslogIdentifier=petclinic

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable petclinic

# Start service
echo "Iniciando serviço PetClinic..."
systemctl start petclinic > /dev/null 2>&1

# Wait a bit and check status
echo "Aguardando inicialização..."
sleep 10

# Check if service is running
if systemctl is-active --quiet petclinic; then
    echo "✅ PetClinic iniciado com sucesso!"
else
    echo "❌ Erro ao iniciar PetClinic. Verificando logs:"
    systemctl status petclinic --no-pager
fi

echo ""
echo "=== 🌸 PetClinic configurado com sucesso! ==="
echo "Aplicação disponível em:"
echo "  - 🌐 Externo: http://localhost:8080"
echo "  - 🔍 Interno: http://192.168.56.11:8080"