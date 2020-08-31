#include "mq.h"
//class mq;
#include "rsoa-example.pb.h"
#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include <SimpleAmqpClient/AmqpLibraryException.h>
#include <map>
#include <iostream>
#include <sstream>
#include <unistd.h>

mq* g_mq;

static std::string symbol;
static std::string system_password;

static bool initSymbol()
{
    const char* pszSymbol = ::getenv("SYMBOL");
    if (NULL == pszSymbol)
    {
        std::cerr << "SYMBOL must be defined" << std::endl;
        return false;
    }
    symbol.assign(pszSymbol);
    std::cout << "configured SYMBOL is " << symbol << std::endl;
    return true;
}

static void initSystemPassword()
{
    const char* pszSystemPassword = ::getenv("SYSTEM_PASSWORD");
    if (NULL == pszSystemPassword)
    {
        pszSystemPassword = "system";
        std::cerr << "using default SYSTEM_PASSWORD" << std::endl;
    }
    system_password.assign(pszSystemPassword);
}

int main()
{
    GOOGLE_PROTOBUF_VERIFY_VERSION;

    initSystemPassword();

    g_mq = new mq(system_password);
    g_mq->run();
}

