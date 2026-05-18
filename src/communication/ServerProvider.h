#ifndef SERVERPROVIDER_H
#define SERVERPROVIDER_H

#include <StandardDefines.h>
#include "ILocalServer.h"
#include "ICloudServer.h"

/**
 * Provider class for managing server instances
 * Manages server lifecycle and provides singleton access to the default server
 */
class ServerProvider {

    Public Static IServerPtr GetLocalServer() {
        /* @Autowired */
        ILocalServerPtr localServer;
        return localServer;
    }

    Public Static IServerPtr GetCloudServer() {
        /* @Autowired */
        ICloudServerPtr cloudServer;
        return cloudServer;
    }
    
};

#endif // SERVERPROVIDER_H

