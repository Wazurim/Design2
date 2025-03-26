/* 
   Example Arduino code: 
   Bidirectional serial communication with a simulated "temperature" (sine wave),
   plus commands from the PC for start/stop/reset/parameters.
*/

#include <Arduino.h>

bool running = false;    // Indicates if we send the sine wave values
float amplitude = 1.0;   // Sine wave amplitude
float freq = 0.1;        // Sine wave frequency
unsigned long lastSendTime = 0;
unsigned long interval = 200; // ms between sends (~5 Hz)
unsigned long t = 0;    // Discrete "time" counter for the sine wave

// Forward declarations
void handleLine(const String &line);
void parseParameters(const String &line);

void setup() {
  Serial.begin(115200);
  delay(2000);  // Optional: let Arduino settle after reset
  
  Serial.println("Arduino started. Waiting for commands...");
  Serial.println("Available commands:");
  Serial.println("  p                   -> Start sending sine wave");
  Serial.println("  S                   -> Stop sending");
  Serial.println("  R                   -> Reset & prompt for new parameters");
  Serial.println("  PARAM A=2.0 F=0.5   -> Set consigne/frequency");
  Serial.println();
}

void loop() {
  // 1) Check if we have a full line available
  //    We read the entire line at once using readStringUntil('\n').
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) {
      handleLine(line);
    }
  }

  // 2) If running, send a sinusoidal value every 'interval' ms
  if (running) {
    unsigned long now = millis();
    if (now - lastSendTime >= interval) {
      lastSendTime = now;
      float tempValue = amplitude * sin(2.0 * PI * freq * t);
      t++;  // increment discrete time
      
      // Send the value, ending with newline so Python can read line-by-line
      Serial.println(tempValue);
    }
  }
}

// handleLine() decides how to process each command line
void handleLine(const String &line) {
  // Single-character commands
  if (line.equalsIgnoreCase("p")) {
    running = true;
    Serial.println("Asservissement ON");
  }
  else if (line.equalsIgnoreCase("S")) {
    running = false;
    Serial.println("Asservissement OFF");
  }
  else if (line.equalsIgnoreCase("R")) {
    running = false;
    t = 0;
    Serial.println("RESET - send new parameters via 'PARAM A=... F=...'");
  }
  // Parameter command
  else if (line.startsWith("PARAM")) {
    parseParameters(line);
  }
  // Unknown
  else {
    Serial.print("Unknown command or format: ");
    Serial.println(line);
  }
}

// parseParameters() extracts amplitude/frequency from a line like "PARAM A=2.0 F=0.5"
void parseParameters(const String &line) {
  // For example: "PARAM A=2.0 F=0.5"
  // We look for "A=" and "F="
  int indexA = line.indexOf("A=");
  int indexF = line.indexOf("F=");
  if (indexA == -1 || indexF == -1) {
    Serial.println("Invalid PARAM syntax. Use: PARAM C=2.0 F=0.5");
    return;
  }

  // Extract amplitude substring
  {
    // Start right after "A="
    int start = indexA + 2;
    // End at the first space after "A=", or if none found, just before "F="
    int end = line.indexOf(' ', start);
    if (end == -1) {
      // If there's no space, stop where "F=" begins
      end = indexF;
    }
    String valA = line.substring(start, end);
    amplitude = valA.toFloat();
  }

  // Extract frequency substring
  {
    int start = indexF + 2;
    // End at space or end of string
    int end = line.indexOf(' ', start);
    if (end == -1) {
      end = line.length();
    }
    String valF = line.substring(start, end);
    freq = valF.toFloat();
  }

  // Display the newly set parameters
  Serial.print("New parameters -> Consigne: ");
  Serial.print(amplitude);
  Serial.print(" , Frequency: ");
  Serial.println(freq);
}
