#ifndef COMMAND_H
#define COMMAND_H

#include <StandardDefines.h>

struct Command {
    Int id;                  // command ID
    Int senderId;            // who sent it
    StdString payload;     // optional metadata
};

#endif // COMMAND_H