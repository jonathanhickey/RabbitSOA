#include "rsoa-example.pb.h"
#include "mq.h"
//#include <boost/algorithm/string.hpp>
#include <google/protobuf/io/zero_copy_stream_impl_lite.h>
#include <iostream>
#include <vector>


mq::mq(std::string system_password) :
        system_password_(std::move(system_password))
{
    channel_ = connect();
    setupReactorctlExchange();
}

/////////////////////////////////////////
// private interface
AmqpClient::Channel::ptr_t
mq::connect()
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

void
mq::run()
{
    auto tags = std::vector<std::string>{ reactorctlConsumerTag_ };
    while (true)
    {
        AmqpClient::Envelope::ptr_t envelope;
        if (channel_->BasicConsumeMessage(tags, envelope, -1))  // -1 to deactivate, 30000 to activate fake BBO
        {
            auto exchange = envelope->Exchange();
            auto routing_key = envelope->RoutingKey();
            std::cout << "got message with Exchange: " << exchange << ", RoutingKey: " << routing_key << std::endl;
            if (exchange == reactorctlExchangeName_)
            {
                std::cout << "got message with routing key: " << routing_key << std::endl;
                handleReactorCtlMessage(std::move(envelope->Message()->Body()));
            }
        }
        else
        {
//            publishFakeBBO();
        }
    }
}

void
mq::setupReactorctlExchange()
{
    std::cout << "declaring direct exchange '" << reactorctlExchangeName_ << "'" << std::endl;
    channel_->DeclareExchange(reactorctlExchangeName_, AmqpClient::Channel::EXCHANGE_TYPE_DIRECT);

//    auto reactorctl_queue_name = "reactor.reactorctl." + symbol_;
    auto reactorctl_queue_name = "reactor.reactorctl";
    std::cout << "declaring queue '" << reactorctl_queue_name << "'" << std::endl;
    auto reactorctlQueue = channel_->DeclareQueue(reactorctl_queue_name);

//    auto binding_key = "reactorctl." + symbol_;
    auto binding_key = "*";
    std::cout << "binding queue '" << reactorctl_queue_name
              << "' to exchange '" << reactorctlExchangeName_
              << "' with binding key '" << binding_key << "'" << std::endl;
    channel_->BindQueue(reactorctlQueue, reactorctlExchangeName_, binding_key);

    reactorctlConsumerTag_ = channel_->BasicConsume(reactorctlQueue);
}

void
mq::handleReactorCtlMessage(std::string body)
{
    auto ais = google::protobuf::io::ArrayInputStream(body.data(), body.length());

    RSOAExample::ValueReq valueReq;
    valueReq.ParseFromZeroCopyStream(&ais);
//    if (reactorCtl.has_setactivestate())
//        handleSetActiveState(reactorCtl.setactivestate());
//    else if (reactorCtl.has_rulesettings())
//        handleRuleSettings(reactorCtl.rulesettings());
//    else
//        std::cout << "got an unknown ReactorCore::ReactorCtl" << std::endl;
}

//void
//mq::handleSetActiveState(const ReactorCore::SetActiveState& setActiveState)
//{
//    std::cout << "got SetActiveState with activeState " << setActiveState.activestate() << std::endl;
//    switch (operationalState_)
//    {
//        case OperationalState::WaitingForRuleSettings:
//        {
//            std::cout << "Ignoring SetActiveState. operationalState_ is WaitingForRuleSettings." << std::endl;
//        } break;
//
//        case OperationalState::Suspended: {
//            switch (setActiveState.activestate())
//            {
//                case ReactorCore::ActiveState::UNKNOWN_ACTIVESTATE:
//                {
//                    std::cout << "Ignoring SetActiveState. UNKNOWN_ACTIVESTATE is not valid." << std::endl;
//                } break;
//                case ReactorCore::ActiveState::SUSPENDED:
//                {
//                    std::cout << "Ignoring SetActiveState. operationalState_ is already Suspended." << std::endl;
//                } break;
//                case ReactorCore::ActiveState::ACTIVE:
//                {
//                    std::cout << "Changing operationalState_ to Active" << std::endl;
//                    operationalState_ = OperationalState::Active;
//
//                    markets::ActiveStatus activeStatus;
//                    activeStatus.set_activestate(markets::ActiveState::ACTIVE);
//                    publishActiveStatus(activeStatus);
//                } break;
//            }
//        } break;
//
//        case OperationalState::Active: {
//            switch (setActiveState.activestate())
//            {
//                case ReactorCore::ActiveState::UNKNOWN_ACTIVESTATE:
//                {
//                    std::cout << "Ignoring SetActiveState. UNKNOWN_ACTIVESTATE is not valid." << std::endl;
//                } break;
//                case ReactorCore::ActiveState::SUSPENDED:
//                {
//                    std::cout << "Changing operationalState_ to Suspended" << std::endl;
//                    operationalState_ = OperationalState::Suspended;
//
//                    markets::ActiveStatus activeStatus;
//                    activeStatus.set_activestate(markets::ActiveState::SUSPENDED);
//                    publishActiveStatus(activeStatus);
//                } break;
//                case ReactorCore::ActiveState::ACTIVE:
//                {
//                    std::cout << "Ignoring SetActiveState. operationalState_ is already Active." << std::endl;
//                } break;
//            }
//        } break;
//
//        default:
//            std::cout << "We are in an invalid operationalState_. This is very bad." << std::endl;
//    }
//}
