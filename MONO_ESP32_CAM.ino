/**
 * ESP32-CAM (XIAO ESP32S3) → Raspberry Pi
 * ----------------------------------------
 * Captures frames from the camera and streams them over TCP to a Raspberry Pi server.
 *
 * Hardware: Seeed Studio XIAO ESP32S3 (with PSRAM)
 * Camera: OV2640
 *
 * Usage:
 * 1. Configure WiFi SSID, password, and server (host, port) below.
 * 2. Flash to ESP32S3 board using Arduino IDE or PlatformIO.
 * 3. On Raspberry Pi, run a TCP server to receive frames.
 *
 * Author: Harsha Vardhan Reddy Yerranagu
 * Repo: https://github.com/Harshavardhan200/MONO_ROBOT//MONO_ESP32_CAM.ino
 */

#include "esp_camera.h"
#include <WiFi.h>

// ==== Camera Model ====
#define CAMERA_MODEL_XIAO_ESP32S3 // Has PSRAM
WiFiClient client;

// ==== Pin Configuration (XIAO ESP32S3 + OV2640) ====
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     10
#define SIOD_GPIO_NUM     40
#define SIOC_GPIO_NUM     39

#define Y9_GPIO_NUM       48
#define Y8_GPIO_NUM       11
#define Y7_GPIO_NUM       12
#define Y6_GPIO_NUM       14
#define Y5_GPIO_NUM       16
#define Y4_GPIO_NUM       18
#define Y3_GPIO_NUM       17
#define Y2_GPIO_NUM       15
#define VSYNC_GPIO_NUM    38
#define HREF_GPIO_NUM     47
#define PCLK_GPIO_NUM     13

#define LED_GPIO_NUM      21

// ==== WiFi Credentials ====
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// ==== Server (Raspberry Pi) ====
const char* host = "192.168.1.176";  // Change to your Pi’s IP
const uint16_t port = 8080;          // Match server port

// ==== Setup ====
void setup() {
  Serial.begin(115200);
  while (!Serial);

  // WiFi
  Serial.println("🔌 Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\n✅ WiFi connected: %s\n", WiFi.localIP().toString().c_str());

  // Camera config
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size   = FRAMESIZE_QVGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location  = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count     = 1;

  if (psramFound()) {
    config.jpeg_quality = 10;
    config.fb_count     = 2;
    config.grab_mode    = CAMERA_GRAB_LATEST;
  } else {
    config.frame_size   = FRAMESIZE_SVGA;
    config.fb_location  = CAMERA_FB_IN_DRAM;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed with error 0x%x\n", err);
  } else {
    Serial.println("✅ Camera initialized successfully!");
  }
}

// ==== Helper: Safe Send ====
bool sendAll(WiFiClient &client, const uint8_t *data, size_t len) {
  size_t totalSent = 0;
  while (totalSent < len) {
    size_t sent = client.write(data + totalSent, len - totalSent);
    if (sent == 0) return false;
    totalSent += sent;
  }
  return true;
}

// ==== Main Loop ====
void loop() {
  // Ensure TCP connection
  if (!client.connected()) {
    Serial.println("🔌 Connecting to Raspberry Pi...");
    if (client.connect(host, port)) {
      Serial.println("✅ Connected to RPi");
    } else {
      Serial.println("❌ Connection failed, retrying...");
      delay(2000);
      return;
    }
  }

  // Capture frame
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Frame capture failed");

    int32_t errorLen = -1;
    sendAll(client, (uint8_t*)&errorLen, sizeof(errorLen));
    const char *errMsg = "Frame capture failed";
    sendAll(client, (const uint8_t*)errMsg, strlen(errMsg));

    delay(2000);
    return;
  }

  Serial.printf("\n📸 Frame: %dx%d (%d bytes)\n", fb->width, fb->height, fb->len);

  // Send size
  if (!sendAll(client, (uint8_t*)&fb->len, sizeof(fb->len))) {
    Serial.println("❌ Failed to send frame size");
    esp_camera_fb_return(fb);
    return;
  }

  // Send buffer
  if (!sendAll(client, fb->buf, fb->len)) {
    Serial.println("❌ Failed to send frame data");
  } else {
    Serial.printf("📤 Sent frame (%d bytes)\n", fb->len);
  }

  esp_camera_fb_return(fb);

  delay(2000); // ~1 frame every 2 seconds
}
