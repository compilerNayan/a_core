#ifndef ISERVER_H
#define ISERVER_H

#include <StandardDefines.h>
]
// Forward declaration and pointer types
DefineStandardPointers(IHttpRequest)

/**
 * Interface for network servers (TCP/UDP)
 * Defines common operations that all server implementations should support
 */
DefineStandardPointers(IServer)
class IServer {
    Public Virtual ~IServer() = default;
    
    // ========== Server Lifecycle ==========
    
    /**
     * Start the server and bind to the specified port
     * @param port Port number to listen on (default: DEFAULT_SERVER_PORT)
     * @return true if server started successfully, false otherwise
     */
    Public Virtual Bool Start() = 0;
    
    /**
     * Stop the server and release resources
     */
    Public Virtual Void Stop() = 0;
    

    Public Virtual Bool Restart() = 0;
    
    /**
     * Check if the server is currently running
     * @return true if server is running, false otherwise
     */
    Public Virtual Bool IsRunning() const = 0;
    
    // ========== Message Operations ==========
    
    /**
     * Receive a message from a client
     * @return IHttpRequestPtr (shared_ptr), nullptr on error or no message
     */
    Public Virtual IHttpRequestPtr ReceiveMessage() = 0;
    
    /**
     * Send a message to a client
     * @param requestId The unique request ID (GUID) to identify the client connection
     * @param message Message to send
     * @return true if message was sent successfully, false otherwise
     */
    Public Virtual Bool SendMessage(CStdString& requestId, CStdString& message) = 0;
    };

#endif // ISERVER_H

