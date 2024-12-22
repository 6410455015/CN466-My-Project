#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include "hw_mic.h"
#include <arduinoFFT.h>

static bool status = false;

// WiFi credentials
const char* ssid = "poom";
const char* password = "ratchapon123";

// MQTT server credentials
const char* mqttServer = "mqtt.eclipseprojects.io";
const int mqttPort = 1883;
const char* mqttTopic = "TU/CN466/callmommy/sound";

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// Sound detection settings
#define SOUND_THRESHOLD 2000000 // Adjust based on environment
#define SAMPLES         128
#define SAMPLING_FREQUENCY 16000

// FFT setup
double vReal[SAMPLES];
double vImag[SAMPLES];
ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, SAMPLES, SAMPLING_FREQUENCY);

void connectToWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

void checkWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected! Reconnecting...");
    connectToWiFi();
  }
}

void connectToMQTT() {
  Serial.print("Connecting to MQTT...");
  while (!mqttClient.connected()) {
    if (mqttClient.connect("ArduinoClient")) {
      Serial.println("connected");
    } else {
      Serial.print("failed with state ");
      Serial.println(mqttClient.state());
      delay(2000);
    }
  }
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    connectToWiFi();
    mqttClient.setServer(mqttServer, mqttPort);
    connectToMQTT();
    hw_mic_init(150000);
}

void loop() {
    static int32_t samples[SAMPLES];
    static uint32_t num_samples = SAMPLES;
      // Ensure WiFi connection
    checkWiFiConnection();

    // Ensure the MQTT connection is active
    if (!mqttClient.connected()) {
        connectToMQTT();
    }
    mqttClient.loop();

    
    hw_mic_read(samples, &num_samples);

    // Calculate average amplitude
    uint32_t avg_sound = 0;
    for (int i = 0; i < num_samples; i++) {
        avg_sound += abs(samples[i]);
    }
    avg_sound /= num_samples;
    Serial.print("Average Sound: ");
    Serial.println(avg_sound);

    // Perform FFT analysis for frequency detection
    for (int i = 0; i < SAMPLES; i++) {
        vReal[i] = samples[i] / 2147483648.0; // Normalize to -1.0 to 1.0
        vImag[i] = 0;
    }
    FFT.windowing(FFT_WIN_TYP_HAMMING, FFT_FORWARD);
    FFT.compute(FFT_FORWARD);
    FFT.complexToMagnitude();
    double dominantFrequency = FFT.majorPeak();

    // Log dominant frequency
    Serial.print("Dominant Frequency: ");
    Serial.println(dominantFrequency);

    // Check if dominant frequency matches child crying range
    if (dominantFrequency > 300 && dominantFrequency < 800) {
        Serial.println("Child cry frequency detected!");
        char message[100];
        snprintf(message, sizeof(message),
             "{\n"
             "  \"timestamp\": %lu,\n"
             "  \"status\": Child is Crying\n"
             "}",
             millis());

        mqttClient.publish(mqttTopic, message);

        // Debug message
        Serial.printf("Transition to ON detected. Timestamp: %lu, Status: Child is Crying\n", millis());
    }

    delay(1000);
}
