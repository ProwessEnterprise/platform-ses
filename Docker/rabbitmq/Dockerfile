# Use the official RabbitMQ image as the base image
FROM rabbitmq:3.12.1-management

# Copy a custom configuration file into the container
COPY /app/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY /app/definitions.json /etc/rabbitmq/definitions.json

# Enable the RabbitMQ management plugin
# RUN rabbitmq-plugins enable --offline rabbitmq_management

