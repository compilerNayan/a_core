#ifndef ICOMMANDBUS_INTERNAL_H
#define ICOMMANDBUS_INTERNAL_H

#include <StandardDefines.h>
#include "../01-type/01-Command.h"
#include "../01-type/03-Subscription.h"

DefineStandardPointers(ICommandBus)
class ICommandBus {
    Public Virtual ~ICommandBus() = default;
    Public Virtual Void Publish(CStdString topic, const Command& cmd) = 0;
    Public Virtual Subscription Subscribe(CStdString topic) = 0;
};
    
#endif // ICOMMANDBUS_INTERNAL_H