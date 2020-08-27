FROM rabbitmq:3.8.7

RUN apt-get update
RUN apt-get install -y curl

COPY plugins/rabbitmq_lvc_exchange-3.8.0.ez /opt/rabbitmq/plugins/

RUN rabbitmq-plugins enable --offline rabbitmq_management
RUN rabbitmq-plugins enable --offline rabbitmq_lvc_exchange

USER rabbitmq

COPY rabbitmq.conf /etc/rabbitmq/
COPY advanced.config /etc/rabbitmq/

ENV RABBITMQ_LOGS=/log/mq.log

EXPOSE 5672
EXPOSE 15672
