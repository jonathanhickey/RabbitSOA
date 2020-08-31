#include "rsoa-example.pb.h"
#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include <SimpleAmqpClient/AmqpLibraryException.h>
#include <string>


class mq
{
public:
    explicit mq(std::string system_password);
    void run();

private:
    AmqpClient::Channel::ptr_t connect();
    void setupReactorctlExchange();
    void handleReactorCtlMessage(std::string body);

    std::string reactorctlExchangeName_ = "msgs";
    std::string system_password_;
    AmqpClient::Channel::ptr_t channel_;
    std::string actionConsumerTag_;
    std::string reactorctlConsumerTag_;
};