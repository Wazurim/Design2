// Constants
const int thermistorPin = A0; // Analog pin connected to the thermistor
const float Vcc = 5.0;        // Supply voltage
const float R_fixed = 9896.5; // Measured resistance of the reference resistor (in ohms)
const float B = 3984.0;        // B25/85 value of the thermistor
const float R25 = 10000.0;     // Thermistor resistance at 25°C (10kΩ)
const float T0 = 298.15;       // Reference temperature in Kelvin (25°C)

// Function to calculate temperature
float calculateTemperature(float resistance) {
  float logR = log(resistance / R25);
  float tempKelvin = 1.0 / ((logR / B) + (1.0 / T0));
  return tempKelvin - 273.15; // Convert to Celsius
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  // Read the ADC value (10-bit, range: 0-1023)
  int adcValue = analogRead(thermistorPin);

  // Convert ADC value to voltage
  float V_out = (adcValue * Vcc) / 1023.0;

  // Calculate the thermistor resistance
  //float R_thermistor = R_fixed * (Vcc / V_out - 1.0);
  float R_thermistor = R_fixed * (V_out / (Vcc - V_out));

  // Calculate the temperature
  float temperatureCelsius = calculateTemperature(R_thermistor);

// Print the results with high precision
  Serial.print("ADC Value: ");
  Serial.print(adcValue);
  Serial.print(" | Voltage: ");
  Serial.print(V_out, 9);  // Higher precision for voltage
  Serial.print(" V | Resistance: ");
  Serial.print(R_thermistor, 9);  // Higher precision for resistance
  Serial.print(" Ohms | Temperature: ");
  Serial.print(temperatureCelsius, 9);  // Higher precision for temperature
  Serial.println(" °C");


  delay(500); // Delay for readability
}
