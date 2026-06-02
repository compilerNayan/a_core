#ifndef ISERVERPROVIDER_H
#define ISERVERPROVIDER_H

#include <StandardDefines.h>
#include "IServer.h"

DefineStandardPointers(ILocalServer)
DefineStandardPointers(ICloudServer)

DefineStandardPointers(IServerProvider)
class IServerProvider { 
    Public Virtual ~IServerProvider() = default;

    Public Virtual IServerPtr GetLocalServer() const = 0;
    Public Virtual ILocalServerPtr GetLocalServerPtr() const = 0;
    Public Virtual IServerPtr GetCloudServer() const = 0;
    Public Virtual ICloudServerPtr GetCloudServerPtr() const = 0;
};

#endif // ISERVERPROVIDER_H