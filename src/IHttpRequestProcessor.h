#ifndef I_HTTP_REQUEST_PROCESSOR_H
#define I_HTTP_REQUEST_PROCESSOR_H

#include <StandardDefines.h>
#include <communication/IHttpRequest.h>

// Forward declarations
DefineStandardPointers(IHttpRequestProcessor)
class IHttpRequestProcessor {

    Public Virtual ~IHttpRequestProcessor() = default;

    // ============================================================================
    // HTTP REQUEST PROCESSING OPERATIONS
    // ============================================================================
    
    /**
     * @brief Processes a request from the queue if available
     * @return true if a request was processed, false if queue was empty
     */
    Public Virtual Bool ProcessRequest() = 0;

    /**
     * @brief Processes all requests from the queue
     * @return true if any requests were processed, false if queue was empty
     */
    Public Virtual Bool ProcessRequests() = 0;
};

#endif // I_HTTP_REQUEST_PROCESSOR_H

