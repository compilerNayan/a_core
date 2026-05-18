#ifndef THREAD_H
#define THREAD_H

#include <StandardDefines.h>

#if defined(ARDUINO)
#include <Arduino.h>
#elif defined(ESP_PLATFORM)   // ESP-IDF build
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#else
#include <thread>
#include <chrono>
#endif

/**
 * Cross-platform thread utilities.
 * Sleep() uses delay() on Arduino,
 * vTaskDelay() on ESP-IDF,
 * and std::this_thread::sleep_for on desktop.
 */
class Thread {
public:
    /** Suspend the current execution for the given duration (milliseconds). */
    static void Sleep(ULong durationMs) {
#if defined(ARDUINO)
        delay(static_cast<unsigned long>(durationMs));
#elif defined(ESP_PLATFORM)
        vTaskDelay(pdMS_TO_TICKS(durationMs));
#else
        std::this_thread::sleep_for(std::chrono::milliseconds(durationMs));
#endif
    }
};

#endif // THREAD_H
