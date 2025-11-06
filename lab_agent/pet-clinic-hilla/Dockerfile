# Multi-stage build for Hilla Pet Clinic
FROM maven:3.8-openjdk-17 AS build

# Set working directory
WORKDIR /app

# Copy Maven files for dependency resolution
COPY pom.xml .
COPY mvnw .
COPY mvnw.cmd .
COPY .mvn .mvn

# Copy source code
COPY src ./src
COPY package.json .
COPY package-lock.json .
COPY tsconfig.json .
COPY types.d.ts .
COPY vite.config.ts .
COPY vite.generated.ts .

# Build the application
RUN mvn clean package -Pproduction -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jdk-alpine

# Install required packages
RUN apk add --no-cache curl

# Create app user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Set working directory
WORKDIR /app

# Copy built jar from build stage
COPY --from=build /app/target/*.jar app.jar

# Change ownership to app user
RUN chown appuser:appgroup /app/app.jar

# Switch to app user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# Expose port
EXPOSE 8080

# Environment variables
ENV SPRING_PROFILES_ACTIVE=postgres
ENV JAVA_OPTS="-Xmx512m -Xms256m"

# Run the application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]