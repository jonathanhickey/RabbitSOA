#include "protobufs/cpp-service.pb.h"
#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include <string>


class mq
{
public:
    explicit mq(std::string system_password);
    void run();

private:
    AmqpClient::Channel::ptr_t connect();
    void setupRSOAExchange();
    std::string setupConsume(const std::string& exchange, const std::string& queue_name, const std::string& binding_key);
    void handleValueReqMessage(const std::string& body);
    void handleRequestMessage(const std::string& body);
    void handleMessage(const cpp_service::SnapshotDataA& sd);
    void handleMessage(const cpp_service::SubscribeDataA& sd);

    std::string system_password_;
    AmqpClient::Channel::ptr_t channel_;
    std::string rsoaExchangeName_ = "rsoa_exch";

    std::string valueReqRoutingKey_ = "ValueReq";
    std::string rsoaConsumerTag_;

    std::string requestRoutingKey_ = "Request";
    std::string requestConsumerTag_;
};