// ESP32 sampler controller only. This firmware never drives vehicle thrusters.
// Pump and laser require correctly rated external driver circuits.
#include <Arduino.h>

constexpr uint8_t BUTTON_PIN = 27;
constexpr uint8_t PUMP_PIN = 25;
constexpr uint8_t LASER_PIN = 26;
constexpr bool PUMP_ACTIVE_HIGH = true;
constexpr bool LASER_ACTIVE_HIGH = true;
constexpr uint32_t MAX_PUMP_MS = 5000;
constexpr uint32_t MAX_LASER_MS = 30000;
constexpr uint32_t DEFAULT_PUMP_MS = 1500;
constexpr uint32_t MAX_LINE = 120;

String lineBuffer;
String activeId;
bool active = false;
bool pumpRunning = false;
uint32_t pumpDeadline = 0;
uint32_t laserDeadline = 0;
uint32_t lastButtonMs = 0;
bool lastButton = HIGH;

void setOutput(uint8_t pin, bool on, bool activeHigh) {
  digitalWrite(pin, (on == activeHigh) ? HIGH : LOW);
}

void stopPump() { setOutput(PUMP_PIN, false, PUMP_ACTIVE_HIGH); pumpRunning = false; }
void stopLaser() { setOutput(LASER_PIN, false, LASER_ACTIVE_HIGH); }

void emit(const String &message) { Serial.println(message); }

bool safeId(const String &s) {
  if (s.length() < 1 || s.length() > 32) return false;
  for (size_t i = 0; i < s.length(); i++) {
    char c = s[i];
    if (!isalnum(c) && c != '-' && c != '_') return false;
  }
  return true;
}

void beginSample(const String &id, uint32_t pumpMs) {
  if (!safeId(id)) { emit("ERROR,INVALID_ID"); return; }
  if (active) { emit("ERROR,BUSY"); return; }
  if (pumpMs == 0 || pumpMs > MAX_PUMP_MS) { emit("ERROR,PUMP_DURATION_RANGE"); return; }
  activeId = id;
  active = true;
  setOutput(LASER_PIN, true, LASER_ACTIVE_HIGH);
  setOutput(PUMP_PIN, true, PUMP_ACTIVE_HIGH);
  pumpRunning = true;
  pumpDeadline = millis() + pumpMs;
  laserDeadline = millis() + MAX_LASER_MS;
  emit("ACK," + id + ",STARTED");
  emit("EVENT," + id + ",LASER_ON");
}

void finishSample(const String &id) {
  if (!active || id != activeId) { emit("ERROR,NO_MATCHING_SAMPLE"); return; }
  stopPump();
  stopLaser();
  active = false;
  emit("EVENT," + id + ",COMPLETE");
  activeId = "";
}

void handleLine(String line) {
  line.trim();
  if (line == "PING") { emit("PONG"); return; }
  if (line.startsWith("SAMPLE_START,")) {
    int first = line.indexOf(',');
    int second = line.indexOf(',', first + 1);
    if (second < 0) { emit("ERROR,BAD_FORMAT"); return; }
    String id = line.substring(first + 1, second);
    long pumpMs = line.substring(second + 1).toInt();
    if (pumpMs < 1) { emit("ERROR,BAD_FORMAT"); return; }
    beginSample(id, static_cast<uint32_t>(pumpMs));
    return;
  }
  if (line.startsWith("MEASURE_DONE,")) {
    finishSample(line.substring(String("MEASURE_DONE,").length()));
    return;
  }
  emit("ERROR,UNKNOWN_COMMAND");
}

void setup() {
  // Set output latches to OFF before output mode to minimize startup glitches.
  digitalWrite(PUMP_PIN, PUMP_ACTIVE_HIGH ? LOW : HIGH);
  digitalWrite(LASER_PIN, LASER_ACTIVE_HIGH ? LOW : HIGH);
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(LASER_PIN, OUTPUT);
  stopPump();
  stopLaser();
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(115200);
  lineBuffer.reserve(MAX_LINE);
  emit("READY,1");
}

void loop() {
  while (Serial.available()) {
    char c = static_cast<char>(Serial.read());
    if (c == '\n') { handleLine(lineBuffer); lineBuffer = ""; }
    else if (c != '\r') {
      if (lineBuffer.length() < MAX_LINE) lineBuffer += c;
      else { lineBuffer = ""; emit("ERROR,LINE_TOO_LONG"); }
    }
  }
  if (active && pumpRunning && static_cast<int32_t>(millis() - pumpDeadline) >= 0) {
    stopPump();
    emit("EVENT," + activeId + ",PUMP_TIMEOUT_OFF");
  }
  if (active && static_cast<int32_t>(millis() - laserDeadline) >= 0) {
    stopLaser();
    emit("EVENT," + activeId + ",LASER_TIMEOUT_OFF");
    // Retain active sample state so an explicit done or button abort can close it.
    laserDeadline = millis() + MAX_LASER_MS;
  }
  // Button is a stop-only emergency input. A press de-energizes both outputs.
  bool button = digitalRead(BUTTON_PIN);
  if (lastButton == HIGH && button == LOW && millis() - lastButtonMs > 50) {
    lastButtonMs = millis();
    if (active) {
      String id = activeId;
      stopPump(); stopLaser(); active = false; activeId = "";
      emit("EVENT," + id + ",BUTTON_ABORT");
    }
  }
  lastButton = button;
  delay(2);
}
