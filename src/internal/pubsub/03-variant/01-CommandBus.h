#ifndef COMMANDBUS_H
#define COMMANDBUS_H

#include <StandardDefines.h>
#include "../02-interface/01-ICommandBus.h"
#include "../01-type/02-CommandQueue.h"

/* @Component */
class CommandBus final : public ICommandBus {
    Private StdUnorderedMap<StdString, CommandQueuePtr> topicQueues_;
    Private std::mutex mutex_;
    Public CommandBus() = default;
    Public Virtual ~CommandBus() override = default;

    Public Void Publish(CStdString topic, const Command& cmd) override {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = topicQueues_.find(topic);
        if (it != topicQueues_.end()) {
            it->second->Push(cmd);
        }
    }
    
    Public Subscription Subscribe(CStdString topic) override {
        std::lock_guard<std::mutex> lock(mutex_);
        if (topicQueues_.find(topic) == topicQueues_.end()) {
            topicQueues_[topic] = std::make_shared<CommandQueue>();
        }
        return Subscription(topicQueues_[topic]);
    }
};
    

#endif // COMMANDBUS_H