#ifndef HTTP_REQUEST_MANAGER_H
#define HTTP_REQUEST_MANAGER_H

#include "IHttpRequestManager.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestProcessor.h"
#include "IHttpResponseProcessor.h"
#include "communication/ServerProvider.h"
#include "logger/ILogger.h"
#include "Thread.h"

/* @Component */
class HttpRequestManager final : public IHttpRequestManager {

    /* @Autowired */
    Private IHttpRequestQueuePtr requestQueue;

    /* @Autowired */
    Private IHttpRequestProcessorPtr requestProcessor;

    /* @Autowired */
    Private IHttpResponseProcessorPtr responseProcessor;

    /* @Autowired */
    Private ILoggerPtr logger;

    Private IServerPtr localServer;
    Private IServerPtr cloudServer;

    Public HttpRequestManager() {
        localServer = ServerProvider::GetLocalServer();
        cloudServer = ServerProvider::GetCloudServer();
    }
    
    Public ~HttpRequestManager() override = default;

    // ============================================================================
    // HTTP Request Management Operations
    // ============================================================================
    
    Private Void RetrieveRequestFromLocalServer() {
        if (localServer == nullptr) return;
        IHttpRequestPtr request = localServer->ReceiveMessage();
        if (request != nullptr) {
            logger->Info(Tag::Untagged, StdString("Received request from local server"));
            requestQueue->EnqueueRequest(request);
        }
    }

    Private Void RetrieveRequestFromCloudServer() {
        if (cloudServer == nullptr) return;
        IHttpRequestPtr request = cloudServer->ReceiveMessage();
        if (request != nullptr) {
            logger->Info(Tag::Untagged, StdString("Received request from cloud server"));
            requestQueue->EnqueueRequest(request);
        }
    }

    Public Bool HandleRequest() override {
        RetrieveRequestFromLocalServer();
        RetrieveRequestFromCloudServer();

        ProcessRequest();
        ProcessResponse();
        Thread::Sleep(1000);
        return true;
    }
    
    Private Bool ProcessRequest() {
        if (requestProcessor == nullptr) {
            return false;
        }
        
        Bool processedAny = false;
        while (requestQueue->HasRequests()) {
            if (requestProcessor->ProcessRequest()) {
                processedAny = true;
            } else {
                break;
            }
        }
        
        return processedAny;
    }
    
    Private Bool ProcessResponse() {
        if (responseProcessor == nullptr) {
            return false;
        }
        
        Bool processedAny = false;
        // Process responses until queue is empty or processor returns false
        while (true) {
            if (responseProcessor->ProcessResponse()) {
                processedAny = true;
            } else {
                break;
            }
        }
        
        return processedAny;
    }
};

#endif // HTTP_REQUEST_MANAGER_H

