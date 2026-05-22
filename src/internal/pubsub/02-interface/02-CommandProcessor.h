#ifndef COMMANDPROCESSOR_INTERNAL_H
#define COMMANDPROCESSOR_INTERNAL_H

#include <StandardDefines.h>
#include "01-ICommandBus.h"

class CommandProcessor {
    /* @Autowired */
    Private ICommandBusPtr bus_;

    Private StdString topic_;
    Private SubscriptionPtr subscription_;
    Private Bool running_ = false;

    Public Virtual ~CommandProcessor() = default;
    Public Virtual Void OnCommandReceived(const Command& cmd) = 0;

    Public CommandProcessor(CStdString topic) : topic_(topic) {
        subscription_ = bus_->Subscribe(topic);
    }

    virtual ~CommandProcessor() {
        Stop();
    }

    void Stop() { running_ = false; }

    Public CStdString GetTopic() const { return topic_; }

    Public Void ProcessCommands() {
        while (running_) {
            if (subscription_->HasCommands()) {
                auto cmd = subscription_->Pull();
                if(cmd.has_value()) { 
                    ProcessCommand(cmd);
                }
            }
        }
    }
};

#endif // COMMANDPROCESSOR_INTERNAL_H