#ifndef SUBSCRIPTION_H
#define SUBSCRIPTION_H

#include <StandardDefines.h>
#include "02-CommandQueue.h"

class Subscription {
    Private CommandQueuePtr queue_;
    
    Public Explicit Subscription(CommandQueuePtr q) : queue_(q) {}
    Public Virtual ~Subscription() = default;

    Public Bool HasCommands() const {
        return !queue_->IsEmpty();
    }
    
    Public Optional<Command> Pull() {
        return queue_->Pop();
    }

};
    

#endif // SUBSCRIPTION_H