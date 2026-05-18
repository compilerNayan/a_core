#ifndef SERVERPROVIDER_H
#define SERVERPROVIDER_H

#include "IServer.h"
#include <StandardDefines.h>
#include <functional>
#include <memory>

/**
 * Provider class for managing server instances
 * Manages server lifecycle and provides singleton access to the default server
 */
class ServerProvider {

    Public Static IServerPtr GetLocalServer() {
        return nullptr;
    }

    Public Static IServerPtr GetCloudServer() {
        return nullptr;
    }
    
};

#endif // SERVERPROVIDER_H

