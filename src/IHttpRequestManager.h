#ifndef I_HTTP_REQUEST_MANAGER_H
#define I_HTTP_REQUEST_MANAGER_H

#include <StandardDefines.h>
#include <communication/IHttpRequest.h>
#include <communication/IServer.h>

// Forward declarations
DefineStandardPointers(IHttpRequestManager)
class IHttpRequestManager {

    Public Virtual ~IHttpRequestManager() = default;

    Public Virtual Bool HandleRequest() = 0;
    
    
};

#endif // I_HTTP_REQUEST_MANAGER_H

