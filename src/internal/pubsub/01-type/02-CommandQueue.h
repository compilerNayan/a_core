#ifndef COMMANDQUEUE_H
#define COMMANDQUEUE_H

#include <StandardDefines.h>
#include "01-Command.h"

DefineStandardPointers(CommandQueue)
class CommandQueue {
    
    Private StdQueue<Command> queue_;
    Private mutable std::mutex mutex_;
    
    Public Void Push(const Command& cmd) {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push(cmd);
    }
        
    Public Optional<Command> Pop() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) return std::nullopt;
        Command cmd = queue_.front();
        queue_.pop();
        return cmd;
    }

    Public Bool IsEmpty() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.empty();
    }
};
    
#endif // COMMANDQUEUE_H