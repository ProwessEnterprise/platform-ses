# Use the official RabbitMQ image as the base image
FROM rabbitmq:3-management

# Copy a custom configuration file into the container
COPY /configs/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
COPY /configs/definitions.json /etc/rabbitmq/definitions.json

# Enable the RabbitMQ management plugin
# RUN rabbitmq-plugins enable --offline rabbitmq_management

