#ifndef COMMANDQUEUE_H
#define COMMANDQUEUE_H

#include <StandardDefines.h>
#include "01-Command.h"

DefineStandardPointers(CommandQueue)
class CommandQueue {
    
    Private StdQueue<Command> queue_;
    Private std::mutex mutex_;
    
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
};
    
#endif // COMMANDQUEUE_H