#ifndef REQUESTSOURCE_H
#define REQUESTSOURCE_H

/**
 * Source of the HTTP request/response (which server received or will send it).
 */
enum class RequestSource {
    LocalServer,
    CloudServer
};

#endif // REQUESTSOURCE_H
