/*
  Mega2560: Split Timers for Independent PWM and ADC Update Frequencies
  
  Timer1: Generates a 16-bit PWM on OC1A (pin 11) using full 16-bit resolution.
          ICR1 is fixed to 65535, so the PWM duty cycle can range from 0 to 65535.
          The PWM frequency is given by:
              PWM Frequency = F_CPU / (PWM_PRESCALER * (65535 + 1))
          Adjust PWM_PRESCALER to choose your PWM frequency.

  Timer3: Runs in CTC mode to trigger an ADC update interrupt at DESIRED_ADC_UPDATE_FREQ.
          OCR3A is computed from:
              OCR3A = (F_CPU / (TIMER3_PRESCALER * DESIRED_ADC_UPDATE_FREQ)) - 1
          This allows you to update your ADC at a different rate than the PWM frequency.
*/

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <math.h>

#ifndef F_CPU
#define F_CPU 16000000UL
#endif

// *********** PWM (Timer1) Configuration ***********
// Use full 16-bit resolution for PWM (0 to 65535)
#define PWM_TOP 4095UL
// Choose the Timer1 prescaler for PWM (available options: 1, 8, 64, 256, 1024)
// For example, using 8 yields: PWM Frequency = 16e6 / (8 * 65536) ≈ 30.5 Hz
#define PWM_PRESCALER 8UL //Était à 4 mais Prescaler mis à 8 plus bas (1 << CS11)

// Macro to compute actual PWM frequency (for info only)
#define ACTUAL_PWM_FREQ (F_CPU / (PWM_PRESCALER * (PWM_TOP + 1)))

// *********** ADC Update (Timer3) Configuration ***********
// Set the desired ADC update frequency in Hz (e.g., 1 Hz)
#define DESIRED_ADC_UPDATE_FREQ 1.0
// Choose Timer3 prescaler (e.g., 1024)
#define TIMER3_PRESCALER 1024UL
// Compute OCR3A value so that Timer3 fires at DESIRED_ADC_UPDATE_FREQ
#define OCR3A_VALUE ((uint16_t)((F_CPU / (TIMER3_PRESCALER * DESIRED_ADC_UPDATE_FREQ)) - 1))

// *****************************************************

// Global variables for control and timing
volatile uint32_t adcUpdateCount = 0;
volatile uint8_t currentChannel = 0;
volatile bool newSampleFlag = false;

// ADC raw values for 4 channels (A0 to A3)
volatile uint16_t adcRawValues[4]; // Store ADC results


// Control loop variables
bool running = false;
float Time = 0;
float CurrentTime = 0;
float consigne = 25; // Setpoint voltage

float Kp = 0.88;   // Start with a low value; adjust experimentally.
float Ki = 1/101.72;   // Start with a low value; adjust experimentally.
// float previous = PWM_TOP/2;
float previous_control = 0;
float previous_error = 0;
// float integral = 0;
const float dt = 1/DESIRED_ADC_UPDATE_FREQ; // Assuming your ADC update is 1 Hz

// Forward declarations for serial command handling
void handleLine(const String &line);
void parseParameters(const String &line);
float voltage_to_temp(float volt);
//
// Timer3 Compare Match A ISR
// Fires at the rate defined by DESIRED_ADC_UPDATE_FREQ (e.g., 1 Hz)
ISR(TIMER3_COMPA_vect) {

    adcUpdateCount++;
    currentChannel = 0; // Reset channel index
    ADMUX = (ADMUX & 0xF8) | currentChannel; // Select channel 0
    ADCSRA |= (1 << ADSC); // Start ADC conversion

    
}

//
// ADC Conversion Complete ISR
// The ADC is running in free-running mode and continuously updates the raw values.
ISR(ADC_vect) {
    adcRawValues[currentChannel] = ADC; // Read ADC result

    if (currentChannel < 3) {
        currentChannel++; // Move to the next channel
        ADMUX = (ADMUX & 0xF8) | currentChannel; // Set next ADC channel
        ADCSRA |= (1 << ADSC); // Start next conversion
    } else {
        newSampleFlag = true; // Flag that all conversions are complete
    }
}

//
// ADC Initialization: uses AVcc as reference and enables ADC interrupts.
void ADC_Init() {
    ADMUX = (1 << REFS0);  // AVCC reference, start with channel 0
    ADCSRA = (1 << ADEN) | (1 << ADIE) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // Enable ADC, interrupt, prescaler = 128
    DIDR0 = 0x0F; // Disable digital input buffers on ADC0-ADC3
}

//
// Timer1 setup (PWM)
void setupTimer1(){
   // ---------- Timer1 Setup: 16-bit PWM on OC1A ----------
    // Clear Timer1 registers
    TCCR1A = 0;
    TCCR1B = 0;
    // Configure Timer1 for Fast PWM mode with ICR1 as TOP (Mode 14: WGM13=1, WGM12=1, WGM11=1)
    // Setting COM1A1 enables non-inverting PWM on OC1A (digital pin 11)
    TCCR1A |= (1 << COM1A1) | (1 << WGM11);
    TCCR1B |= (1 << WGM13) | (1 << WGM12);
    // Set Timer1 prescaler bits according to PWM_PRESCALER
    // For PWM_PRESCALER=8, set CS10=1 and CS11=1 (see datasheet for Mega2560 Timer1 prescaler settings)
    // (For Mega2560, prescaler bits for Timer1: CS12:0; for prescaler=8: CS11=1, others 0)
    TCCR1B |= (1 << CS11);
    // Set TOP for full 16-bit resolution
    ICR1 = PWM_TOP;
    // Set initial duty cycle to 50% (OCR1A = PWM_TOP/2)
    OCR1A = PWM_TOP / 2; 
}
//
// Timer3 setup (ADC)
void setupTimer3(){
    // ---------- Timer3 Setup: ADC Update Interrupt ----------
    // Clear Timer3 registers
    TCCR3A = 0;
    TCCR3B = 0;
    // Configure Timer3 in CTC mode (Clear Timer on Compare Match, WGM32=1)
    // Set Timer3 prescaler to TIMER3_PRESCALER (e.g., 1024)
    // For Timer3 on Mega2560, prescaler=1024 is set by CS32 and CS30 bits
    TCCR3B = (1 << WGM32) | (1 << CS32) | (1 << CS30); 
    // Set OCR3A for the desired ADC update frequency
    OCR3A = OCR3A_VALUE; 
    // Enable Timer3 Compare Match A interrupt
    TIMSK3 |= (1 << OCIE3A);  
}

//
// Setup function
void setup() {
    Serial.begin(115200);
    ADC_Init();
    ADCSRA |= (1 << ADSC);  // Start ADC conversions in free-running mode

    // Set pin 11 as PWM output (OC1A)
    pinMode(11, OUTPUT);

    cli(); // Disable interrupts during timer configuration

    setupTimer1();

    setupTimer3();

    sei(); // Re-enable interrupts

    Serial.println("Mega2560 started with split timers:");
    Serial.print("PWM Frequency (Timer1): ");
    Serial.print(ACTUAL_PWM_FREQ);
    Serial.println(" Hz (using full 16-bit resolution)");
    Serial.print("ADC Update Frequency (Timer3): ");
    Serial.print(DESIRED_ADC_UPDATE_FREQ);
    Serial.println(" Hz");
    Serial.println("Enter commands:");
    Serial.println("  p    -> start control loop");
    Serial.println("  S    -> stop control loop");
    Serial.println("  R    -> reset and new parameters");
    Serial.println("  PARAM C=2.5 F=1.0  -> set parameters (C = setpoint, F = frequency)");
}

//
// Main loop: When a new ADC sample is ready, update the PWM duty cycle based on control calculations.
void loop() {
    noInterrupts();
    bool sampleReady = newSampleFlag;
    // Copy the latest ADC voltage values to temporary variables
    float currSamplet2 = adcRawValues[0] * (5.0 / 1023.0);
    float currSamplet4 = adcRawValues[1] * (5.0 / 1023.0);
    float currSamplet1 = adcRawValues[2] * (5.0 / 1023.0);
    float currSamplet3 = adcRawValues[3] * (5.0 / 1023.0); // Used for control error computation
    uint32_t updateCountSnapshot = adcUpdateCount;
    
    // Calculate PWM period (in seconds):
    // PWM period = (PWM_TOP + 1) * (PWM_PRESCALER / F_CPU)
    float pwmPeriod = (float)(PWM_TOP + 1) * ((float)PWM_PRESCALER / F_CPU);
    // Derive true time from ADC update count
    float trueTime = updateCountSnapshot / DESIRED_ADC_UPDATE_FREQ;
    CurrentTime = trueTime - Time;
    
    if (sampleReady) newSampleFlag = false;
    interrupts();
    
    if (Serial.available() > 0) {

        String line = Serial.readStringUntil('\n');

        line.trim();
        if (line.length() > 0) {
            handleLine(line);
        }
    }

    if (sampleReady) {
        // Process serial commands if available
        
        
        if (running) {

            float volt_consigne = consigne/2.0833f - 9.5f;

            float error = -(volt_consigne - (5 - currSamplet3));
            const float dt = 1.0f / DESIRED_ADC_UPDATE_FREQ;

            // Apply low-pass filter to reduce noise
            //#define ALPHA 0.1
            //error = ALPHA * error + (1 - ALPHA) * previous;

            // integral += error * dt; // Correct integral accumulation

            // Compute PI control output
            // float control = -(error * Kp + integral * Ki) * PWM_TOP / 10;
            // control += PWM_TOP / 2; // Shift midpoint

            // Si on trouve un nouveau PI, il faudra recalculer l'équation de récurrence
            // et ensuite changer les valeurs ici. Les valeurs ne sont pas directement celles du PI.
            // Vous pouvez regarder mes notes voir s'il n'y a pas une formule qui permet la conversion
            // directe.
            float control = (previous_control + error * 0.525f - previous_error * 0.475f);
            // float control = 0;
            previous_control = control;
            // Adjust for operation point
            control += 2.5f;

            // Anti-windup
            if (control > 4.9f) {
                control = 4.9f;
            }
            else if (control < 0.1f) {
                control = 0.1f;
            }

            // Set previous values before going into PWM.
            
            previous_error = error;

            // Convert volts to PWM
            control = ((control-0.1f)/4.8f) * PWM_TOP;
            // control = (control-0.1f)/4.8f;
            // control = control * (1720) + 1200;

            // Implement anti-windup
            // if (control > PWM_TOP - 750) {
            //     control = PWM_TOP - 750;
            //     // integral -= error * dt;
            // } 
            // if (control < 750) {
            //     control = 750;
            //     integral -= error * dt;  
            // }

            // Set PWM output
            uint16_t pwmValue = (uint16_t) control;
            OCR1A = pwmValue;

            // Store error for next cycle
            //previous = error;

            //float control = ((0.8603f/(previous - 0.9805)) * (5-error) + 2.5)*PWM_TOP/5;           
            
            Serial.print(trueTime * 1000, 1);  // Time in ms
            Serial.print(" ms \t| PWM duty: ");
            Serial.print(pwmValue);
            Serial.print(" / ");
            Serial.print(PWM_TOP);
            Serial.print(" | ADC t1: ");
            Serial.print(voltage_to_tempt1(currSamplet1), 3);
            Serial.print(" | ADC t2: ");
            Serial.print(voltage_to_tempt1(currSamplet2), 3);
            Serial.print(" | ADC t3: ");
            Serial.print(voltage_to_tempt3(currSamplet3), 3);
            Serial.print(" | ADC t4: ");
            Serial.print(voltage_to_tempt3(currSamplet4), 3);
            Serial.print(" |\t\t error: ");
            Serial.println(error, 3);
            // Serial.print(" | Integral: ");
            //Serial.println(integral, 3);
        }
        else {
            OCR1A = PWM_TOP / 2;
            Serial.print(trueTime * 1000, 1);
            Serial.print(" ms \t| PWM duty: ");
            Serial.print(PWM_TOP / 2);
            Serial.print(" / ");
            Serial.print(PWM_TOP);
            Serial.print(" | ADC t1: ");
            Serial.print(voltage_to_tempt1(currSamplet1), 3);
            Serial.print(" | ADC t2: ");
            Serial.print(voltage_to_tempt1(currSamplet2), 3);
            Serial.print(" | ADC t3: ");
            Serial.print(voltage_to_tempt3(currSamplet3), 3);
            Serial.print(" | ADC t4: ");
            Serial.print(voltage_to_tempt3(currSamplet4), 3);
            Serial.println("\t Control OFF");
        }
    }
}

//
// Serial command processing functions
void handleLine(const String &line) {
    if (line.equalsIgnoreCase("p")) {
        running = true;
        Time = CurrentTime + Time;
        CurrentTime = 0;
        
        Serial.println("Control loop ON");
    } else if (line.equalsIgnoreCase("S")) {
        running = false;
        Serial.println("Control loop OFF");
    } else if (line.equalsIgnoreCase("R")) {
        running = false;
        Time = CurrentTime + Time;
        CurrentTime = 0;

        Serial.println("RESET - send new parameters via 'PARAM C=... F=...'");
    } else if (line.startsWith("PARAM")) {
        parseParameters(line);
    } else {
        Serial.print("Unknown command or format: ");
        Serial.println(line);
    }
}

void parseParameters(const String &line) {
    int indexC = line.indexOf("C=");
    int indexI = line.indexOf("I=");
    int indexK = line.indexOf("K=");
    if (indexC == -1) {
        Serial.println("Invalid PARAM C syntax. Use: PARAM C=2.5 I=1.0 K=0.5");
        Serial.println(line);
        return;
    }
    if (indexI == -1) {
        Serial.println("Invalid PARAM I syntax. Use: PARAM C=2.5 I=1.0 K=0.5");

        return;
    }
    if (indexK == -1) {
        Serial.println("Invalid PARAM I syntax. Use: PARAM C=2.5 I=1.0 K=0.5");

        return;
    }
    {
        int start = indexC + 2;
        int end = line.indexOf(' ', start);
        if (end == -1) {
            end = indexI;
        }
        String valC = line.substring(start, end);
        consigne = valC.toFloat();
    }
    {
        int start = indexI + 2;
        int end = line.indexOf(' ', start);
        if (end == -1) {
            end = line.length();
        }
        String valI = line.substring(start, end);
        // Frequency parameter received but not reconfigured at runtime in this example.
        Serial.print("New KI parameter received (not applied at runtime): ");
        Serial.println(valI);
    }
    {
        int start = indexK + 2;
        int end = line.indexOf(' ', start);
        if (end == -1) {
            end = line.length();
        }
        String valK = line.substring(start, end);
        // Frequency parameter received but not reconfigured at runtime in this example.
        Serial.print("New KP parameter received (not applied at runtime): ");
        Serial.println(valK);
    }
    Serial.print("New setpoint (consigne) -> ");
    Serial.println(consigne);
}

float voltage_to_tempt1(float volt) {
    const float A1 = 0.00335401643468053;
    const float B = 0.000256523550896126;
    const float C1 = 0.00000260597012072052;
    const float D1 = 0.000000063292612648746;
    const float RT = 10000.0;
    volt = volt * 1.6f/4.9f + 1.7f;
    float res = 5 * (10000 - 2000 * volt) / volt;
    float logVal = log(RT / res);
    float temp = 1.0 / (A1 + B * logVal + C1 * logVal * logVal + D1 * logVal * logVal * logVal) - 273.15;
    return temp;
}

float voltage_to_tempt3(float volt) {
    const float A1 = 0.00335401643468053;
    const float B = 0.000256523550896126;
    const float C1 = 0.00000260597012072052;
    const float D1 = 0.000000063292612648746;
    const float RT = 10000.0;
    volt = volt * 0.7f/4.9f + 2.2f;
    float res = 5 * (10000 - 2000 * volt) / volt;
    float logVal = log(RT / res);
    float temp = 1.0 / (A1 + B * logVal + C1 * logVal * logVal + D1 * logVal * logVal * logVal) - 273.15;
    return temp;
}

