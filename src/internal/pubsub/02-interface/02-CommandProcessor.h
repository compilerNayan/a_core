#ifndef COMMANDPROCESSOR_INTERNAL_H
#define COMMANDPROCESSOR_INTERNAL_H

#include <StandardDefines.h>
#include "01-ICommandBus.h"

class CommandProcessor {
    /* @Autowired */
    Private ICommandBusPtr bus_;

    Private StdString topic_;
    Private Subscription subscription_;
    Private Bool running_ = false;

    Public Virtual Void OnCommandReceived(const Command& cmd) = 0;

    Public CommandProcessor(CStdString topic) : topic_(topic) {
        subscription_ = bus_->Subscribe(topic);
    }

    Virtual ~CommandProcessor() {
        Stop();
    }

    Void Stop() { running_ = false; }

    Public CStdString GetTopic() const { return topic_; }

    Public Void ProcessCommands() {
        if (subscription_.HasCommands()) {
            auto cmd = subscription_.Pull();
            if(cmd.has_value()) { 
                OnCommandReceived(cmd.value());
            }
        }
    }
};

#endif // COMMANDPROCESSOR_INTERNAL_H