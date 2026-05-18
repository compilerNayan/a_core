#ifndef HTTP_RESPONSE_PROCESSOR_H
#define HTTP_RESPONSE_PROCESSOR_H

#include "IHttpResponseProcessor.h"
#include "IHttpResponseQueue.h"
#include <communication/ServerProvider.h>
#include <communication/IHttpResponse.h>

/* @Component */
class HttpResponseProcessor final : public IHttpResponseProcessor {

    /* @Autowired */
    Private IHttpResponseQueuePtr responseQueue;

    Private IServerPtr localServer;
    Private IServerPtr cloudServer;

    Public HttpResponseProcessor() 
        : localServer(ServerProvider::GetLocalServer()), cloudServer(ServerProvider::GetCloudServer()) {
    }
    
    Public ~HttpResponseProcessor() override = default;

    // ============================================================================
    // HTTP Response Processing Operations
    // ============================================================================
    
    Public Bool ProcessResponse() override {
        if (responseQueue->IsEmpty()) {
            return false;
        }
        
        IHttpResponsePtr response = responseQueue->DequeueLocalResponse();
        if (response == nullptr) {
            return false;
        }
        
        if (localServer == nullptr) {
            return false;
        }

        if (cloudServer == nullptr) {
            return false;
        }
        
        // Get request ID from response
        StdString requestId = StdString(response->GetRequestId());
        if (requestId.empty() || requestId == "ignore") {
            return false;
        }
        
        // Convert response to HTTP string format
        StdString responseString = response->ToHttpString();
        if (responseString.empty()) {
            return false;
        }
        
        // Send response using server
        localServer->SendMessage(requestId, responseString);
        cloudServer->SendMessage(requestId, responseString);
        return false;
    }
};

#endif // HTTP_RESPONSE_PROCESSOR_H

