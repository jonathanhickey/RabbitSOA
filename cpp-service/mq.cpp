#include "protobufs/rsoa-example.pb.h"
#include "protobufs/cpp-service.pb.h"
#include "mq.h"
#include <google/protobuf/io/zero_copy_stream_impl_lite.h>
#include <iostream>
#include <vector>


mq::mq(std::string system_password) :
        system_password_(std::move(system_password))
{
    channel_ = connect();
    setupRSOAExchange();
}

void mq::run()
{
    auto tags = std::vector<std::string>{ rsoaConsumerTag_, requestConsumerTag_ };
    while (true)
    {
        AmqpClient::Envelope::ptr_t envelope;
        if (channel_->BasicConsumeMessage(tags, envelope, 30000))  // 30 seconds
        {
            auto exchange = envelope->Exchange();
            auto routing_key = envelope->RoutingKey();
            std::cout << "got message with Exchange: " << exchange << ", RoutingKey: " << routing_key << std::endl;
            if (exchange == rsoaExchangeName_) {
                if (routing_key == valueReqRoutingKey_)
                    handleValueReqMessage(envelope->Message()->Body());
                else if (exchange == rsoaExchangeName_ && routing_key == requestRoutingKey_)
                    handleRequestMessage(envelope->Message()->Body());
            }
        }
        else
        {
            publishB();
        }
    }
}

/////////////////////////////////////////
// private interface
AmqpClient::Channel::ptr_t mq::connect()
{
    AmqpClient::Channel::ptr_t cp;
    while (!cp)
    {
        try
        {
            std::cout << "attempting to create connection to mq" << std::endl;
            AmqpClient::Channel::OpenOpts oopts;
            oopts.host = "mq";
            oopts.auth = AmqpClient::Channel::OpenOpts::BasicAuth("system", system_password_);
            cp = AmqpClient::Channel::Open(oopts);
        }
        catch (AmqpClient::AmqpLibraryException& e)
        {
            std::cout << "connection failed with AmqpClient::AmqpLibraryException "
                      << e.ErrorCode() << ", " << e.what()
                      << ". will try again in 10 sec" << std::endl;
            ::usleep(10000000);
        }
    }
    std::cout << "connected to mq" << std::endl;
    return cp;
}

void mq::setupRSOAExchange()
{
    // declare exchange in case it's not already there
    std::cout << "declaring direct exchange '" << rsoaExchangeName_ << "'" << std::endl;
    channel_->DeclareExchange(rsoaExchangeName_, AmqpClient::Channel::EXCHANGE_TYPE_DIRECT);

    rsoaConsumerTag_ = setupConsume(rsoaExchangeName_, "cpp_service.rsoa.ValueReq", valueReqRoutingKey_);
    requestConsumerTag_ = setupConsume(rsoaExchangeName_, "cpp_service.Request", requestRoutingKey_);
}

std::string mq::setupConsume(const std::string& exchange, const std::string& queue_name, const std::string& binding_key)
{
    std::cout << "declaring queue '" << queue_name << "'" << std::endl;
    auto queue = channel_->DeclareQueue(queue_name);

    std::cout << "binding queue '" << queue_name
              << "' to exchange '" << exchange
              << "' with binding key '" << binding_key << "'" << std::endl;
    channel_->BindQueue(queue, exchange, binding_key);

    return channel_->BasicConsume(queue);
}

void mq::handleValueReqMessage(const std::string& body)
{
    auto ais = google::protobuf::io::ArrayInputStream(body.data(), body.length());

    RSOAExample::ValueReq valueReq;
    valueReq.ParseFromZeroCopyStream(&ais);
    int32_t id = valueReq.id();
    std::cout << "got RSOA ValueReq, id: " << id << std::endl;
}

void mq::handleRequestMessage(const std::string& body)
{
    auto ais = google::protobuf::io::ArrayInputStream(body.data(), body.length());

    cpp_service::Request request;
    request.ParseFromZeroCopyStream(&ais);
    if (request.has_snapshotdataa())
        handleMessage(request.snapshotdataa());
    else if (request.has_subscribedatab())
        handleMessage(request.subscribedatab());
    else
        std::cout << "got an unknown cpp_service::Request" << std::endl;
}

void mq::handleMessage(const cpp_service::SnapshotDataA& sd)
{
    int32_t id = sd.id();
    std::cout << "got cpp_service::SnapshotDataA, id: " << id << std::endl;

    cpp_service::DataA dataA;
    dataA.set_id(id);
    dataA.set_value(189);

    std::string ss;
    dataA.SerializeToString(&ss);
    auto msg = AmqpClient::BasicMessage::Create(ss);
    std::string routing_key = "DataA";
    std::cout << "publish DataA"
              << " to exchange '" << rsoaExchangeName_
              << "' with routing_key '" << routing_key << "'" << std::endl;
    channel_->BasicPublish(rsoaExchangeName_, routing_key, msg);
}

void mq::handleMessage(const cpp_service::SubscribeDataB& sd)
{
    int32_t id = sd.id();
    std::cout << "got cpp_service::SubscribeDataB, id: " << id << std::endl;
    publishB_ = true;
}

void mq::publishB()
{
    if (!publishB_)
        return;

    const int id = 4;
    static int ivalue = 0;
    std::string svalue{"dummmy"};

    cpp_service::DataB dataB;
    dataB.set_id(id);
    dataB.set_ivalue(++ivalue);
    dataB.set_svalue(svalue);

    std::string ss;
    dataB.SerializeToString(&ss);
    auto msg = AmqpClient::BasicMessage::Create(ss);
    std::string routing_key = "DataB";
    std::cout << "publish DataB"
              << " to exchange '" << rsoaExchangeName_
              << "' with routing_key '" << routing_key << "'" << std::endl;
    channel_->BasicPublish(rsoaExchangeName_, routing_key, msg);
}
